import ast
import builtins
import contextlib
import dataclasses
import errno
import io
import json
import os
import pathlib
import pwd
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
ROOT = SCRIPTS.parents[2]
for path in (SCRIPTS / "veri", SCRIPTS):
    while str(path) in sys.path:
        sys.path.remove(str(path))
    sys.path.insert(0, str(path))

from veri import entry


def fake_pid_file_ps(monkeypatch, conductor=True):
    """Answer pid_file's ps reads: the pid is a claude under run_conductor.py, or else an unrelated process."""
    import importlib

    def ps(field, pid):
        if field == "ppid":
            return "1"
        if not conductor:
            return "vim notes.txt"
        return "python3 run_conductor.py 1" if str(pid) == "1" else "claude -p"

    for name in ("pid_file", "veri.pid_file"):
        monkeypatch.setattr(importlib.import_module(name), "_ps", ps, raising=True)


def live_conductor(monkeypatch, run_tdd, issue):
    """A conductor.pid in <run_tdd> that answers kill -0, its process a claude under run_conductor.py."""
    (run_tdd / "conductor.pid").write_text("%d\n" % os.getpid())
    fake_pid_file_ps(monkeypatch)


@dataclasses.dataclass(frozen=True)
class Definition:
    name: str
    segment: str
    literals: tuple
    names: tuple
    constants: tuple
    strings: tuple
    byte_strings: tuple


@dataclasses.dataclass(frozen=True)
class WalkResult:
    definitions: tuple


def _constants(node):
    if isinstance(node, ast.JoinedStr):
        return
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            yield node.value
        return
    for field, value in ast.iter_fields(node):
        if isinstance(node, ast.Assert) and field == "msg":
            continue
        for child in value if isinstance(value, list) else [value]:
            if isinstance(child, ast.AST):
                yield from _constants(child)


def _strings(parts, kind):
    """Every `kind` constant but an f-string's own literal fragments: the text a readers audit counts as read,
    assert messages and constants inside an f-string's `{...}` included, as each audit's own walk counted it before #2170."""
    fragments = {id(v) for j in parts if isinstance(j, ast.JoinedStr) for v in j.values}
    return tuple(p.value for p in parts if isinstance(p, ast.Constant) and type(p.value) is kind and id(p) not in fragments)


def _lines(text):
    """text split as ast.get_source_segment splits it, once per file instead of once per definition."""
    return re.findall(r"[^\r\n]*(?:\r\n|\n|\r)|[^\r\n]+$", text)


def _segment(lines, node):
    first, last = node.lineno - 1, node.end_lineno - 1
    if first == last:
        return lines[first].encode()[node.col_offset:node.end_col_offset].decode()
    return "".join([lines[first].encode()[node.col_offset:].decode(), *lines[first + 1:last],
                    lines[last].encode()[:node.end_col_offset].decode()])


def _definition(text, node, lines=None):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        names = [node.name]
    else:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = [t.id for target in targets for t in ast.walk(target) if isinstance(t, ast.Name)]
    parts = list(ast.walk(node))
    return [Definition(
        name=name,
        segment=_segment(lines if lines is not None else _lines(text), node),
        literals=tuple(p.value for p in parts if isinstance(p, ast.Constant) and isinstance(p.value, str)),
        names=tuple(p.id for p in parts if isinstance(p, ast.Name) and isinstance(p.ctx, ast.Load)),
        constants=tuple(_constants(node)),
        strings=_strings(parts, str),
        byte_strings=tuple(b.decode("utf-8", "replace") for b in _strings(parts, bytes)),
    ) for name in names]


class TestFile:
    def __init__(self, path):
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self._tree = None
        self._walk = None

    @property
    def tree(self):
        if self._tree is None:
            self._tree = ast.parse(self.text)
        return self._tree

    @property
    def walk(self):
        if self._walk is None:
            lines = _lines(self.text)
            self._walk = WalkResult(tuple(
                d for node in self.tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign, ast.AnnAssign))
                for d in _definition(self.text, node, lines)))
        return self._walk


@pytest.fixture(scope="session")
def tests_py_index():
    root = pathlib.Path(__file__).resolve().parent
    return [TestFile(path) for path in sorted(root.rglob("test_*.py"))]


REAL_RUN, REAL_POPEN = subprocess.run, subprocess.Popen


CANONICAL_SHIM = re.compile(r'exec (?:python3|"\$py") "\$\(dirname "\$0"\)/(veri/[\w-]+\.py)" "\$@"')
SHIM_EXEC = re.compile(r'^exec (?:python3|"\$py") .*/(veri/[\w-]+\.py)"', re.MULTILINE)
VENV_PREFIX = ['py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"', '[ -x "$py" ] || py=python3']
FLOOR_SOURCE = '. "$(dirname "$0")/lib/shim-python.sh"'


def interpreter_venv():
    """The venv a process case hands a shim as VERI_VENV: the one running pytest, else the outer VERI_VENV or
    ~/.veri-tools/venv. A case with a scratch HOME and no VERI_VENV would leave the shim on PATH's python3,
    /usr/bin/python3 3.9 on the development Mac, under the 3.12 floor (#2106)."""
    if sys.prefix != sys.base_prefix and os.access(os.path.join(sys.prefix, "bin", "python3"), os.X_OK):
        return sys.prefix
    return os.environ.get("VERI_VENV") or os.path.expanduser("~/.veri-tools/venv")


INTERPRETER_VENV = interpreter_venv()


def shim_problems(scripts, exempt=()):
    problems = []
    seen = set()
    for script in sorted(pathlib.Path(scripts).glob("*.sh")):
        seen.add(script.name)
        lines = script.read_text().splitlines()
        code = [line for line in lines if line.strip() and not line.startswith("#")]
        exec_line = code[-1] if code else ""
        canonical = bool(lines) and lines[0] == "#!/bin/sh" and (
            (len(code) == 1 and exec_line.startswith("exec python3 "))
            or (len(code) == 3 and code[:2] == VENV_PREFIX and exec_line.startswith('exec "$py" '))
            or (len(code) == 2 and code[0] == FLOOR_SOURCE and exec_line.startswith('exec "$py" '))
        )
        match = CANONICAL_SHIM.fullmatch(exec_line) if canonical else None
        if match is not None and script.name in exempt:
            problems.append("%s: stale exemption, the script is now the canonical shim" % script.name)
        elif match is None and script.name not in exempt:
            problems.append("%s: not the canonical shim" % script.name)
        elif match is not None and not (script.parent / match.group(1)).is_file():
            problems.append("%s: %s does not exist" % (script.name, match.group(1)))
    problems += ["%s: stale exemption, the script is gone" % name for name in sorted(set(exempt) - seen)]
    return problems


def entry_bypass_problems(scripts):
    problems = []
    shims = [(script, SHIM_EXEC.search(script.read_text())) for script in sorted(pathlib.Path(scripts).glob("*.sh"))]
    shims = [(script, match) for script, match in shims if match]
    if not shims:
        problems.append("no shim found under %s" % scripts)
    for script, match in shims:
        module = pathlib.Path(scripts) / match.group(1)
        lines = module.read_text().splitlines()
        for number, line in enumerate(lines, 1):
            if line.startswith("if __name__ == ") and "pycache_prefix.py" not in line:
                block = []
                for l in lines[number:]:
                    if l.strip() and not l[0].isspace():
                        break
                    block.append(l)
                if not any("entry.run(" in l.split("#")[0] for l in block):
                    problems.append("%s:%d __main__ block does not go through entry.run" % (module.name, number))
    return problems


def shim_source_problems(scripts):
    rules = (
        (re.compile(r"\bpython3?\b[^#]*<<"), "feeds python3 a heredoc"),
        (re.compile(r"\bpython3?\b[^#]*\s-c(?:\s|$)"), "feeds python3 a -c string"),
        (re.compile(r"\bgh\s+(issue|pr|repo|api|auth\s+status)\b"), "calls gh"),
    )
    gh_assign = re.compile(r'^(?:if\s+!?\s*|!\s*|local\s+)?(\w+)="?\$\((?:(?:gh|gh_list|gh_json|\w*_json)[\s)]|cat\s+"?\$\{?VERI_GH_JSON)')
    problems = []
    for script in sorted(pathlib.Path(scripts).glob("*.sh")) + sorted(pathlib.Path(scripts).glob("lib/*.sh")):
        library = script.parent.name == "lib"
        name = str(script.relative_to(scripts))
        gh_names = set()
        for number, line in enumerate(script.read_text().splitlines(), 1):
            code = line.lstrip()
            if code.startswith("#"):
                continue
            assigned = gh_assign.match(code)
            if assigned:
                gh_names.add(assigned.group(1))
            if re.search(r"\bpython3?\b", code) and any(re.search(r"\$\{?%s\b" % name, code) for name in gh_names):
                problems.append("%s:%d hands python3 a gh JSON document" % (name, number))
            if library:
                continue
            for pattern, what in rules:
                if pattern.search(code):
                    problems.append("%s:%d %s" % (name, number, what))
    return problems


def pytest_configure(config):
    config.option.importmode = "append"
    config.addinivalue_line("markers", "process(boundary): a medium case, naming the process boundary it observes")
    config.addinivalue_line("markers", "tree_audit(sweeps): a case that lists the repository's own directories, run by make test and not make unit")
    config.addinivalue_line("markers", "serial(reason): a case that must not run beside a full parallel load, naming why")


def pytest_collection_modifyitems(config, items):
    registered = {line.split(":")[0].split("(")[0].strip() for line in config.getini("markers")}
    unregistered = ["%s (%s)" % (item.nodeid, mark.name) for item in items
                    for mark in item.iter_markers() if mark.name not in registered]
    if unregistered:
        raise pytest.UsageError("unregistered mark: %s" % ", ".join(unregistered))
    for name, missing in (("process", "a boundary"), ("tree_audit", "a sweep"), ("serial", "a reason")):
        unnamed = [item.nodeid for item in items
                   if any(not mark.args or not str(mark.args[0]).strip() for mark in item.iter_markers(name))]
        if unnamed:
            raise pytest.UsageError("%s mark without %s: %s" % (name, missing, ", ".join(unnamed)))
    modules = {item.nodeid.split("/")[-1].split("::")[0]: item.module for item in items if isinstance(item, pytest.Function)}
    cases = set(modules) | {"%s::%s" % (name, attr) for name, module in modules.items() for attr in dir(module)}
    for label, table in (("permission-bits", PERMISSION_BITS_EXEMPT), ("system-location", SYSTEM_LOCATION_EXEMPT)):
        problems = exemption_problems(table, cases)
        if problems:
            raise pytest.UsageError("%s exemption table: %s" % (label, "; ".join(problems)))
    for label, table in (("starts-pytest", STARTS_PYTEST_EXEMPT), ("starts-git", STARTS_GIT_IN_REPOSITORY_EXEMPT),
                         ("below-floor", BELOW_FLOOR_INTERPRETER_EXEMPT)):
        problems = reasonless_problems(table)
        if problems:
            raise pytest.UsageError("%s exemption table: %s" % (label, "; ".join(problems)))
    default = max(PROCESS_CASE_TIMEOUT, config.getoption("timeout", None) or 0)
    for item in items:
        if item.get_closest_marker("process") is not None and item.get_closest_marker("timeout") is None:
            item.add_marker(pytest.mark.timeout(default))


# A process case starts real processes, so machine load stretches it past the 30 s a small case gets (#2724, #2679).
PROCESS_CASE_TIMEOUT = 90


CWD_OUTSIDE_REPOSITORY = {
    "test_affected_suites.py",
    "test_event.py",
    "test_invisible_work.py",
    "test_parallel_conductors.py",
    "test_push_branch.py",
    "test_rebase_onto_default.py",
    "test_refactor_touched.py",
    "test_session_cost.py",
    "test_solvable_issues.py",
    "test_status.py",
    "test_timed_test_run.py",
    "test_transform_touches_tests.py",
    "test_verify.py",
    "test_workqueue.py",
}


@pytest.fixture(autouse=True)
def hermetic_environment(request, monkeypatch, tmp_path, tmp_path_factory):
    offline = {name: value for name, value in os.environ.items()
               if name in ("GIT_CONFIG_COUNT", "GIT_TEMPLATE_DIR", "GIT_EXEC_PATH")
               or name.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    for name in list(os.environ):
        if name.startswith(("VERI_", "CLAUDE_", "GH_", "GIT_")) and name != "VERI_VENV":
            monkeypatch.delenv(name)
        elif name == "LANG" or name.startswith("LC_"):
            monkeypatch.delenv(name)
        elif name in ("PYTEST_PLUGINS", "PYTEST_XDIST_WORKER"):
            monkeypatch.delenv(name)
    if request.node.path.name in CWD_OUTSIDE_REPOSITORY:
        monkeypatch.chdir(tmp_path)
    elif at_or_under_root(pathlib.Path.cwd().resolve()):
        monkeypatch.chdir(ROOT)
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(tmp_path / "veri-pytest-legs"))
    monkeypatch.setenv("VERI_MIN_FREE_GB", "0")
    monkeypatch.setenv("VERI_VENV", INTERPRETER_VENV)
    inherited = os.path.realpath(tempfile.tempdir or os.environ.get("TMPDIR") or "/tmp")
    basetemp = os.path.realpath(tmp_path_factory.getbasetemp())
    case_tmpdir = str(tmp_path_factory.mktemp("tmpdir"))
    monkeypatch.setenv("TMPDIR", case_tmpdir)
    monkeypatch.setattr(tempfile, "tempdir", case_tmpdir)
    for name, value in offline.items():
        monkeypatch.setenv(name, value)

    def refuse_inherited_tmpdir(path, frame):
        if not isinstance(path, (str, bytes, os.PathLike)):
            return
        name = os.path.basename(frame.f_code.co_filename)
        target = os.path.realpath(os.fsdecode(path))
        if (name.startswith(("test_", "conftest")) and target.startswith(inherited + os.sep)
                and not target.startswith(basetemp + os.sep)):
            raise AssertionError("%s creates %s in the inherited TMPDIR %s at %s:%d"
                                 % (request.node.nodeid, os.fsdecode(path), inherited, frame.f_code.co_filename, frame.f_lineno))

    real_open, real_mkdir, real_os_open = builtins.open, os.mkdir, os.open

    def guarded_open(file, *rest, **kwargs):
        refuse_inherited_tmpdir(file, caller_outside_pathlib())
        return real_open(file, *rest, **kwargs)

    def guarded_mkdir(path, *rest, **kwargs):
        refuse_inherited_tmpdir(path, caller_outside_pathlib())
        return real_mkdir(path, *rest, **kwargs)

    def guarded_os_open(path, flags, *rest, **kwargs):
        refuse_inherited_tmpdir(path, caller_outside_pathlib())
        return real_os_open(path, flags, *rest, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(os, "mkdir", guarded_mkdir)
    monkeypatch.setattr(os, "open", guarded_os_open)


def fail_unbacked_push(request):
    pytest.fail("%s reached the push backoff without setting VERI_PUSH_BACKOFF" % request.node.nodeid, pytrace=False)


@pytest.fixture(autouse=True)
def case_waits_no_default_push_backoff(request, monkeypatch):
    import importlib

    for name in ("veri.push_branch", "push_branch"):
        module = importlib.import_module(name)

        def guarded(args, *rest, _run=module.run, **kwargs):
            if args[0] == "sleep" and "VERI_PUSH_BACKOFF" not in os.environ:
                fail_unbacked_push(request)
            return _run(args, *rest, **kwargs)

        monkeypatch.setattr(module, "run", guarded)


SLEEP_SHIM = """#!/bin/sh
second() { echo "$2"; }
set -f
case "$(second $(ps -o command= -p "$PPID"))" in
  */veri/push_branch.py) [ -n "${VERI_PUSH_BACKOFF+x}" ] || { echo "$0" >> "$PUSH_BACKOFF_LOG"; exit 1; } ;;
esac
exec "$REAL_SLEEP" "$@"
"""


@pytest.fixture(autouse=True)
def process_case_waits_no_default_push_backoff(request, monkeypatch, tmp_path_factory):
    if request.node.get_closest_marker("process") is None:
        yield
        return
    shim_dir = tmp_path_factory.mktemp("push-backoff-guard")
    log = shim_dir / "reached"
    shim = shim_dir / "sleep"
    shim.write_text(SLEEP_SHIM)
    shim.chmod(0o755)
    monkeypatch.setenv("REAL_SLEEP", shutil.which("sleep"))
    monkeypatch.setenv("PUSH_BACKOFF_LOG", str(log))
    monkeypatch.setenv("PATH", str(shim_dir) + os.pathsep + os.environ.get("PATH", ""))
    yield
    if log.exists():
        fail_unbacked_push(request)


@pytest.fixture(autouse=True)
def process_case_children_do_not_inherit_ignored_signals(request):
    if request.node.get_closest_marker("process") is None:
        yield
        return
    ignored = []
    for number, handler in ((signal.SIGINT, signal.default_int_handler), (signal.SIGTERM, signal.SIG_DFL),
                            (signal.SIGHUP, signal.SIG_DFL)):
        if signal.getsignal(number) == signal.SIG_IGN:
            ignored.append(number)
            signal.signal(number, handler)
    yield
    for number in ignored:
        signal.signal(number, signal.SIG_IGN)


def at_or_under_root(path):
    return path == ROOT or ROOT in path.parents


def in_repository_outside(resolved, scratch):
    return at_or_under_root(resolved) and scratch != resolved and scratch not in resolved.parents


@pytest.fixture(autouse=True)
def unmarked_case_lists_no_repository_directory(request, monkeypatch, tmp_path):
    if request.node.get_closest_marker("tree_audit") is not None:
        for name in ("scandir", "listdir"):
            monkeypatch.setattr(os, name, getattr(getattr(os, name), "real", getattr(os, name)))
        return
    scratch = tmp_path.resolve()

    def checked(real):
        def lister(path="."):
            check(path)
            return real(path)

        lister.real = real
        return lister

    def check(path):
        try:
            listed = pathlib.Path(os.fsdecode(os.path.abspath(path))).resolve()
        except TypeError:
            return
        if in_repository_outside(listed, scratch) and listed.is_dir():
            raise AssertionError("%s lists the repository directory %s: mark it tree_audit" % (request.node.nodeid, listed))

    for name in ("scandir", "listdir"):
        monkeypatch.setattr(os, name, checked(getattr(os, name)))


STARTS_PYTEST_EXEMPT = {
    "test_conftest.py::test_a_case_reading_a_cwd_relative_path_gives_the_same_outcome_started_from_the_repository_root_as_from_skills_tdd_scripts":
        "the pytest session started from two directories is the subject",
    "test_conftest.py::test_the_path_setup_case_gives_the_same_outcome_started_from_skills_tdd_scripts_with_a_relative_path_as_from_the_repository_root":
        "the pytest session started from two directories is the subject",
    "test_stale_bytecode_process.py::test_every_directly_runnable_module_keeps_its_bytecode_out_of_the_tree_2405":
        "pytest_leg.py run directly is one of the modules whose bytecode placement is the subject",
}


def case_tail(request):
    path, _, case = request.node.nodeid.partition("::")
    return path.split("/")[-1] + "::" + case


def exempt_from(tail, table):
    return tail in table or tail.split("::")[0] in table


RUNS_GIT_WITH_NO_CWD = "the module under test runs git with no cwd while the process works in the repository; the case fakes the process or reads only the recorded call"

STARTS_GIT_IN_REPOSITORY_EXEMPT = {
    "test_supervise.py": "supervise.py records the skill clone's own HEAD; the case only lets it run rev-parse HEAD there",
    "test_run_conductor.py": "run_conductor.py runs git -C <skill clone> and the cases fake every process, so the path only reaches the recorded call",
    "test_rebase_onto_default.py::test_main_run_through_a_symlink_from_another_directory_rebases_the_callers_clone_and_never_the_skills_repository":
        "the skills repository's own HEAD is read to prove it was never rebased",
    "test_no_tracked_artifacts.py::test_no_file_under_a_nested_tdd_directory_is_tracked_598":
        "the repository's own tracked files are the subject",
    "test_no_tracked_artifacts.py::test_git_ignores_the_event_log_a_suite_run_writes_under_a_nested_tdd_directory_598":
        "the repository's own ignore rules are the subject",
    "test_skill_identity.py::test_no_tracked_file_outside_the_two_stubs_still_names_the_old_scripts_dir":
        "the repository's own tracked files are the subject",
    "test_skill_identity.py::test_no_tracked_file_outside_the_two_stubs_names_either_old_command":
        "the repository's own tracked files are the subject",
    "test_refactor_budget_process.py::test_no_tracked_file_outside_the_docs_and_tdd_trees_states_3_as_the_veri_issue_refactor_budget_default":
        "the repository's own tracked files are the subject",
}


@pytest.fixture(autouse=True)
def case_starts_no_test_runner(request, monkeypatch):
    real = subprocess.Popen.__init__

    def is_pytest(words):
        names = [os.path.basename(os.fsdecode(w)) for w in words]
        if names[0] in ("pytest", "py.test", "pytest_leg.py"):
            return True
        if not names[0].startswith("python"):
            return False
        return names[1:2] == ["pytest_leg.py"] or any(a == "-m" and b == "pytest" for a, b in zip(names, names[1:]))

    def from_exempt_helper():
        frame = sys._getframe()
        while frame is not None:
            if frame.f_code.co_name == "child_pytest" and os.path.basename(frame.f_code.co_filename) == "test_conftest.py":
                return True
            frame = frame.f_back
        return False

    def is_suite(arg):
        parts = pathlib.PurePath(os.fsdecode(arg)).parts
        return bool(parts) and parts[-1].endswith(".test.sh") and "tests" in parts[:-1]

    def git_directory(words, cwd):
        if os.path.basename(os.fsdecode(words[0])) != "git":
            return None
        directory = os.fsdecode(cwd) if cwd is not None else None
        rest = [os.fsdecode(w) for w in words[1:]]
        if rest == ["--version"]:
            return None
        if directory is None:
            directory = os.getcwd()
        for flag, value in zip(rest, rest[1:]):
            if flag == "-C":
                directory = os.path.join(directory, value) if directory else value
        return directory

    def in_repository(directory):
        scratch = request.getfixturevalue("tmp_path").resolve()
        resolved = pathlib.Path(os.path.abspath(directory)).resolve()
        return in_repository_outside(resolved, scratch)

    def refuse_git_in_repository(args, kwargs):
        words = [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)
        if isinstance(args, str) and kwargs.get("shell"):
            words = shlex.split(args)
        command = " ".join(os.fsdecode(w) for w in words)
        directory = git_directory(words, kwargs.get("cwd")) if words else None
        tail = case_tail(request)
        if directory is not None and not exempt_from(tail, STARTS_GIT_IN_REPOSITORY_EXEMPT) and in_repository(directory):
            raise AssertionError("%s starts git against the repository the tests live in: %s (%s)" % (request.node.nodeid, directory, command))
        return words, command, tail

    def checked(self, args, *rest, **kwargs):
        words, command, tail = refuse_git_in_repository(args, kwargs)
        if words and (is_suite(words[0]) or (os.path.basename(os.fsdecode(words[0])) in ("bash", "sh") and any(is_suite(w) for w in words[1:]))):
            raise AssertionError("%s starts a bash suite: %s" % (request.node.nodeid, command))
        if words and is_pytest(words) and not from_exempt_helper() and tail not in STARTS_PYTEST_EXEMPT:
            raise AssertionError("%s starts pytest: %s" % (request.node.nodeid, command))
        return real(self, args, *rest, **kwargs)

    monkeypatch.setattr(subprocess.Popen, "__init__", checked)

    setattr_ = monkeypatch.setattr

    def refusing_git_in_repository(replacement):
        def run(args, *a, **kw):
            refuse_git_in_repository(args, kw)
            return replacement(args, *a, **kw)

        return run

    def guarded_setattr(target, name, *rest, **kwargs):
        if target == "subprocess.run" and callable(name):
            return setattr_(target, refusing_git_in_repository(name), *rest, **kwargs)
        value = rest[0] if rest else kwargs.get("value")
        if target is subprocess and name == "run" and callable(value):
            return setattr_(target, name, refusing_git_in_repository(value), *rest[1:], **{k: v for k, v in kwargs.items() if k != "value"})
        return setattr_(target, name, *rest, **kwargs)

    monkeypatch.setattr = guarded_setattr


_MEETS_FLOOR = {}


def meets_floor(python):
    real = os.path.realpath(python)
    key = (real, os.stat(real).st_mtime_ns)
    if key not in _MEETS_FLOOR:
        floor = re.search(r"^VENV_FLOOR=(\d+)\.(\d+)", (SCRIPTS / "lib" / "venv-python.sh").read_text(), re.MULTILINE)
        said = REAL_RUN([python, "-c", "import platform; print(platform.python_version())"],
                        capture_output=True, text=True).stdout.strip()
        version = re.match(r"(\d+)\.(\d+)", said)
        _MEETS_FLOOR[key] = bool(floor and version) and (int(version.group(1)), int(version.group(2))) >= (int(floor.group(1)), int(floor.group(2)))
    return _MEETS_FLOOR[key]


BELOW_FLOOR_INTERPRETER_EXEMPT = {
    "test_bash_version_guard_process.py::test_on_a_real_python3_below_the_floor_first_on_path_usr_bin_python3_leaf_launchable_sh_refuses_with_exit_2_naming_the_floor_and_its_version":
        "the shim's refusal of a below-floor python3 on PATH is the subject",
    "test_shims.py::test_issue_2106_shim_with_both_python3s_below_the_floor_exits_2_without_its_module_naming_each_interpreter_its_source_and_version":
        "the shim's refusal of a below-floor venv and PATH python3 is the subject",
    "test_shims.py::test_issue_2106_shim_with_no_venv_python3_and_none_on_path_exits_2_naming_where_it_looked_for_each":
        "the shim's refusal when no python3 is found is the subject",
    "test_shims.py::test_issue_2106_shim_with_both_python3s_exiting_1_silently_exits_2_naming_each_interpreter_and_an_unknown_version":
        "the shim's refusal of interpreters reporting no version is the subject",
}


@pytest.fixture(autouse=True)
def process_case_shim_has_a_floor_interpreter(request, monkeypatch):
    if request.node.get_closest_marker("process") is None or exempt_from(case_tail(request), BELOW_FLOOR_INTERPRETER_EXEMPT):
        return
    real = subprocess.Popen.__init__

    def checked(self, args, *rest, **kwargs):
        words = [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)
        shim = os.fsdecode(words[0]) if words else ""
        if os.path.dirname(os.path.abspath(shim)) == str(SCRIPTS) and shim.endswith(".sh"):
            env = kwargs.get("env") if kwargs.get("env") is not None else os.environ
            home = env["HOME"] if "HOME" in env else pwd.getpwuid(os.getuid()).pw_dir
            venv = env.get("VERI_VENV") or home + "/.veri-tools/venv"
            venv_python = os.path.join(venv, "bin", "python3")
            on_path = shutil.which("python3", path=env.get("PATH", os.defpath))
            if not ((os.access(venv_python, os.X_OK) and meets_floor(venv_python))
                    or (on_path and meets_floor(on_path))):
                raise AssertionError("%s launches %s with no python3 at the floor: VERI_VENV=%s, PATH's python3 is %s"
                                     % (request.node.nodeid, os.path.basename(shim), env.get("VERI_VENV"), on_path))
        return real(self, args, *rest, **kwargs)

    monkeypatch.setattr(subprocess.Popen, "__init__", checked)


PATHLIB_SOURCE = os.path.splitext(pathlib.__file__)[0].removesuffix("__init__")


GUARD_WRAPPERS = {"checked", "checked_mkdir", "checked_os_open", "guarded_open", "guarded_mkdir", "guarded_os_open"}


def caller_outside_pathlib():
    frame = sys._getframe(2)
    while frame.f_code.co_filename.startswith(PATHLIB_SOURCE) or (
            frame.f_code.co_filename == __file__ and frame.f_code.co_name in GUARD_WRAPPERS):
        frame = frame.f_back
    return frame


PERMISSION_BITS_EXEMPT = {}


def reasonless_problems(table):
    return ["%s: exemption carries no reason" % entry for entry, reason in table.items() if not reason] + [
        "%s: whole-file exemption with the runs-git-with-no-cwd reason" % entry
        for entry, reason in table.items() if "::" not in entry and reason == RUNS_GIT_WITH_NO_CWD]


def exemption_problems(table, cases):
    problems = reasonless_problems(table)
    for entry in table:
        if entry not in cases:
            problems.append("%s: exemption names no existing case" % entry)
    return problems


@pytest.fixture(autouse=True)
def case_forces_no_failure_through_permission_bits(request, monkeypatch):
    real = os.chmod
    tail = case_tail(request)

    def checked(path, mode, *rest, **kwargs):
        frame = caller_outside_pathlib()
        if mode & 0o600 != 0o600 and not exempt_from(tail, PERMISSION_BITS_EXEMPT):
            raise AssertionError("%s takes permission bits off %s with chmod at %s:%d: uid 0 ignores them"
                                 % (request.node.nodeid, path, frame.f_code.co_filename, frame.f_lineno))
        return real(path, mode, *rest, **kwargs)

    monkeypatch.setattr(os, "chmod", checked)


SYSTEM_LOCATION_EXEMPT = {}


@pytest.fixture(autouse=True)
def case_expects_no_system_location_unreadable_or_unwritable(request, monkeypatch):
    real = io.open
    tail = case_tail(request)

    def system_location(path):
        resolved = pathlib.Path(os.path.abspath(path))
        if any(resolved.is_relative_to(temp) for temp in (pathlib.Path("/tmp"), pathlib.Path(tempfile.gettempdir()))):
            return False
        return len(resolved.parts) == 2 or resolved.parts[1:2] in (("etc",), ("root",), ("proc",))

    def refuse_system_location(verb, path, frame):
        name = os.path.basename(frame.f_code.co_filename)
        if (isinstance(path, (str, bytes, os.PathLike)) and name.startswith(("test_", "conftest"))
                and system_location(os.fsdecode(path)) and not exempt_from(tail, SYSTEM_LOCATION_EXEMPT)):
            raise AssertionError("%s %s the system location %s at %s:%d: uid 0 ignores what makes it fail"
                                 % (request.node.nodeid, verb, os.fsdecode(path), frame.f_code.co_filename, frame.f_lineno))

    def checked(file, *rest, **kwargs):
        refuse_system_location("opens", file, caller_outside_pathlib())
        return real(file, *rest, **kwargs)

    real_mkdir = os.mkdir

    def checked_mkdir(path, *rest, **kwargs):
        refuse_system_location("creates", path, caller_outside_pathlib())
        return real_mkdir(path, *rest, **kwargs)

    real_os_open = os.open

    def checked_os_open(path, flags, *rest, **kwargs):
        if flags & os.O_CREAT:
            refuse_system_location("creates", path, caller_outside_pathlib())
        return real_os_open(path, flags, *rest, **kwargs)

    monkeypatch.setattr(io, "open", checked)
    monkeypatch.setattr(builtins, "open", checked)
    monkeypatch.setattr(os, "open", checked_os_open)
    monkeypatch.setattr(os, "mkdir", checked_mkdir)


@pytest.fixture
def run_cli(monkeypatch, capfd):
    def run(module, argv, stdin="", env=None, cwd=None):
        for name, value in (env or {}).items():
            monkeypatch.setenv(name, value)
        if cwd is not None:
            monkeypatch.chdir(cwd)
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
        monkeypatch.setattr(sys, "path", list(sys.path))
        environ, start = dict(os.environ), os.getcwd()
        try:
            code = entry.exit_code(module.main, argv, on_broken_pipe=lambda: None)
        except SystemExit as exit:
            code = exit.code
        finally:
            os.environ.clear()
            os.environ.update(environ)
            os.chdir(start)
        if code is not None and not isinstance(code, int):
            sys.stderr.write("%s\n" % (code,))
            sys.stderr.flush()
            code = 1
        out, err = capfd.readouterr()
        return 0 if code is None else code, out, err

    return run


@pytest.fixture
def fake_processes(monkeypatch):
    def install(answer=None):
        calls = []

        def line_of(args):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            calls.append(line)
            return line

        def record(args, *_, **__):
            line_of(args)
            return subprocess.CompletedProcess(args, 0, "", "")

        def run(args, *_, **kwargs):
            code, out, err = answer(line_of(args), **kwargs)
            encoding = kwargs.get("encoding") or "utf-8"
            text = kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines")

            def in_mode(value):
                if text and isinstance(value, bytes):
                    return value.decode(encoding)
                if not text and isinstance(value, str):
                    return value.encode(encoding)
                return value

            out, err = in_mode(out), in_mode(err)
            if kwargs.get("stderr") == subprocess.STDOUT:
                out, err = out + err, None
            if kwargs.get("check") and code:
                raise subprocess.CalledProcessError(code, args, out, err)
            return subprocess.CompletedProcess(args, code, out, err)

        def refuse(args, *_, **__):
            raise AssertionError("unexpected process: %s" % line_of(args))

        for name in ("run", "Popen", "call", "check_call", "check_output"):
            entry = record if answer is None else run if name == "run" else refuse
            monkeypatch.setattr(subprocess, name, entry)
        return calls

    return install


def _starts_event_sh(args):
    return isinstance(args, (list, tuple)) and any(os.path.basename(str(a)) == "event.sh" for a in args)


class Events:
    """The records a caller appends to <directory>/.tdd/events.jsonl, ts and awake dropped."""

    def __init__(self, monkeypatch):
        self.monkeypatch = monkeypatch

    def records(self, directory="."):
        path = pathlib.Path(directory) / ".tdd" / "events.jsonl"
        if not path.is_file():
            return []
        lines = [json.loads(line) for line in path.read_text().splitlines()]
        return [{k: v for k, v in line.items() if k not in ("ts", "awake")} for line in lines]

    def unappendable(self, directory="."):
        (pathlib.Path(directory) / ".tdd" / "events.jsonl").mkdir(parents=True)

    def refuse_event_sh(self):
        """Over the fakes subprocess carries now, every start naming event.sh is refused as the OS would."""
        faked = {name: getattr(subprocess, name) for name in ("run", "call", "Popen")}

        def guarded(name):
            def start(args, *rest, **kwargs):
                if _starts_event_sh(args):
                    raise PermissionError(errno.EACCES, "the case refuses starting event.sh", str(args[0]))
                return faked[name](args, *rest, **kwargs)
            return start

        for name in faked:
            self.monkeypatch.setattr(subprocess, name, guarded(name))


@pytest.fixture
def events(monkeypatch):
    return Events(monkeypatch)


class ViaStdin:
    def __init__(self, module, ledger):
        self.module, self.ledger = module, ledger

    def main(self, argv):
        sys.stdin = io.TextIOWrapper(io.BytesIO(self.ledger.encode()))
        return self.module.main(argv)


def issues_listing(numbers, label="ready-for-agent", priority=()):
    """The open-issue listing text selecting <numbers> (None: a listing the selection cannot read)."""
    if numbers is None:
        return "not json"
    return json.dumps([{"number": number, "title": "an issue", "state": "OPEN", "body": "",
                        "labels": [{"name": label}] + ([{"name": "priority"}] if number in priority else [])}
                       for number in numbers])


def serve_listing(directory, monkeypatch):
    """serve(answer): the open-issue and PR listings the selection reads through VERI_GH_JSON, written to
    <directory>, which VERI_GH_JSON names. <answer> is the numbers of the open <label> issues (a list, each
    a number or a string), [] for no labelled open issue, or None for a listing the selection cannot read."""
    directory.mkdir(exist_ok=True)
    monkeypatch.setenv("VERI_GH_JSON", str(directory))
    for name in ("VERI_GH_DRIVER", "VERI_PRIORITY_LABEL"):
        monkeypatch.delenv(name, raising=False)

    def serve(answer, label="ready-for-agent", priority=()):
        (directory / "prs.json").write_text("[]")
        (directory / "issues.json").write_text(issues_listing(answer, label, priority))

    return serve


GH_SERVING = """#!/bin/sh
d=%(directory)s
issues() {
  n=$(cat "$d/count" 2>/dev/null || echo 0); n=$((n + 1)); echo "$n" > "$d/count"
  [ -f "$d/touch-$n" ] && while read -r path; do touch "$path"; done < "$d/touch-$n"
  [ "$n" -gt "$(cat "$d/answers")" ] && n=$(cat "$d/answers")
  cat "$d/issues-$n.json"
}
prs() { cat "$(cat "$d/prs")" 2>/dev/null || echo '[]'; }
case "$1 $2" in
  "issue list") issues ;;
  "pr list") prs ;;
  "api "*)
    case "$2" in
      */issues\\?*) issues ;;
      */pulls\\?*page=[2-9]*) echo '[]' ;;
      */pulls\\?*) prs ;;
      *) exit 1 ;;
    esac ;;
  *) exit 1 ;;
esac
"""


def serve_through_gh(directory, monkeypatch, prs=None):
    """serve(answers): a gh on PATH that answers the open-issue listing with the next of <answers> at each
    request, the last repeating, and the PR listing from the file <prs> (none: no open PR). Each answer is
    (code, stdout[, priority numbers]), as listed() takes it. <touch> maps the request number to paths gh
    touches as it answers that request. VERI_GH_JSON is unset, so the selection asks gh, over whichever route
    VERI_GH_DRIVER names."""
    directory.mkdir(exist_ok=True)
    bin_dir = directory / "bin"
    bin_dir.mkdir(exist_ok=True)
    (bin_dir / "gh").write_text(GH_SERVING % {"directory": shlex.quote(str(directory))})
    (bin_dir / "gh").chmod(0o755)
    (directory / "prs").write_text(str(prs) if prs is not None else "")
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.delenv("VERI_GH_JSON", raising=False)

    def serve(answers, label="ready-for-agent", touch=None):
        for path in directory.glob("touch-*"):
            path.unlink()
        for n, paths in (touch or {}).items():
            (directory / ("touch-%d" % n)).write_text("".join("%s\n" % path for path in paths))
        (directory / "count").write_text("0")
        (directory / "answers").write_text(str(len(answers)))
        for n, answer in enumerate(answers, 1):
            numbers, priority = listed(*answer[:2]), (answer[2:] or ((),))[0]
            (directory / ("issues-%d.json" % n)).write_text(issues_listing(numbers, label, priority))

    return serve


@pytest.fixture
def listing(tmp_path, monkeypatch):
    return serve_through_gh(tmp_path / "solvable-listing", monkeypatch)


def listed(code, stdout):
    """The listing answer that makes the selection exit <code> printing <stdout>: 0 with its lines
    as issue numbers, 3 with none, 2 with an unreadable listing."""
    if code == 2 and not stdout:
        return None
    if code == 3 and not stdout:
        return []
    assert code == 0 and stdout.endswith("\n"), "no listing selects to exit %d, stdout %r" % (code, stdout)
    lines = stdout[:-1].split("\n")
    return [int(line) for line in lines] if all(line.isdigit() for line in lines) else lines


def script(path, body):
    path.write_text("#!/usr/bin/env bash\n%s\n" % body)
    path.chmod(0o755)


def fixture_root(root):
    """<root> holding a Makefile, one git hook, a SKILL.md naming entry.sh, and entry.sh calling helper.sh."""
    scripts = root / "skills" / "tdd" / "scripts"
    hooks = root / "docs" / "hooks"
    scripts.mkdir(parents=True)
    hooks.mkdir(parents=True)
    (root / "Makefile").write_text("test:\n\t@echo ok\n")
    (hooks / "reference-transaction").write_text("#!/bin/sh\nexit 0\n")
    (root / "skills" / "tdd" / "SKILL.md").write_text("# skill\n\nRun `$S/entry.sh <n>` to start.\n")
    script(scripts / "entry.sh", '"$(dirname "$0")/helper.sh" "$@"')
    return scripts


def started_for_real(args, *rest, **kwargs):
    """subprocess.run started as a real process, although subprocess.Popen is faked."""
    faked = subprocess.Popen
    subprocess.Popen = REAL_POPEN
    try:
        return REAL_RUN(args, *rest, **kwargs)
    finally:
        subprocess.Popen = faked


def listed_in_turn(listing, answers, **kwargs):
    """Serve <answers> to <listing> now, and answer with subprocess.run starting every process for real."""
    listing(answers, **kwargs)
    return started_for_real


@contextlib.contextmanager
def supervised(args, started=None, **kwargs):
    """Start supervise.sh in a session of its own; on the way out, however the case ends, kill that session's group."""
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)
    ran = subprocess.Popen(args, start_new_session=True, **kwargs)
    if started is not None:
        started.append(ran)
    try:
        yield ran
    finally:
        try:
            os.killpg(ran.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        ran.wait()


def run_supervised(args, timeout, started=None, **kwargs):
    """Start supervise.sh in a session of its own and wait <timeout> seconds for it."""
    with supervised(args, started=started, **kwargs) as ran:
        out, err = ran.communicate(timeout=timeout)
        return subprocess.CompletedProcess(args, ran.returncode, out, err)
