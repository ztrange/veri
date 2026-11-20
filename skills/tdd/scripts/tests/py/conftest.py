import builtins
import contextlib
import errno
import gc
import importlib
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
from time import time_ns

import pytest
import process_fakes
import repo_builder
from case_size_guards import (  # noqa: F401  (the guards, registered through this module; tests reach them as conftest.<name>)
    BELOW_FLOOR_INTERPRETER_EXEMPT, GUARD_WRAPPERS, PATHLIB_SOURCE, PERMISSION_BITS_EXEMPT, PROCESS_CASE_TIMEOUT,
    RUNS_GIT_WITH_NO_CWD, STARTS_GIT_IN_REPOSITORY_EXEMPT, STARTS_PYTEST_EXEMPT, SUPERVISOR_POLL, SYSTEM_LOCATION_EXEMPT,
    at_or_under_root, caller_outside_pathlib, case_expects_no_system_location_unreadable_or_unwritable,
    case_forces_no_failure_through_permission_bits, case_starts_no_test_runner, case_tail, case_waits_no_default_push_backoff,
    exempt_from, exemption_problems, fail_unbacked_push, in_repository_outside,
    process_case_children_do_not_inherit_ignored_signals,
    process_case_supervisor_polls_sub_second, process_case_waits_no_default_push_backoff, pytest_collection_modifyitems,
    reasonless_problems, register_markers, unmarked_case_lists_no_repository_directory,
    unmarked_case_reads_no_real_process_listing)
from tree_index import TestFile, VeriModules, mentioned_names, tests_py_index_of  # noqa: F401  (TestFile, mentioned_names: audits import them from here)

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
ROOT = SCRIPTS.parents[2]
ROOT_NAME = str(ROOT)


def bare_route(stdout):
    return re.sub(r"(?<=\s)[^\s:]*::", "", stdout) if stdout.startswith(("red ", "repair ", "supersede ")) else stdout


for path in (SCRIPTS / "tests" / "leg", SCRIPTS / "veri", SCRIPTS):  # tests/leg: the pytest leg and its plugins (#4051)
    while str(path) in sys.path:
        sys.path.remove(str(path))
    sys.path.insert(0, str(path))


# One module object per file of scripts/veri/. Production runs a module as `python3 veri/x.py`, so siblings import
# flat (`import git`); tests name them `veri.git`. Left alone, both names load the file twice, and a monkeypatch on
# one copy misses the copy the code under test runs. This finder answers every `veri.<name>` (<name>.py in veri/)
# with the flat `<name>` module itself, so `sys.modules["veri.<name>"] is sys.modules["<name>"]`, whichever name is
# imported first, and `importlib.reload` (which finds the module by its flat `__name__`) keeps it one object.
# Guarantees: that identity for imports made after this point; a module bound earlier under both names is
# collapsed in sys.modules, though references already held to the other copy stay as they were.
# Does not: change `__name__` (always the flat name; `__package__` is empty, so a relative import inside a module
# still falls to its flat `try`), touch `spec_from_file_location` loads (deliberate separate copies), or make
# `veri.<name>` of a file outside veri/ (a package, a missing module) anything but the usual lookup. Each
# pytest-xdist worker imports this conftest and installs its own finder.
import importlib.abc
import importlib.util


class _FlatAlias(importlib.abc.Loader):
    def create_module(self, spec):
        module = importlib.import_module(spec.name.removeprefix("veri."))
        self.flat_spec = module.__spec__
        return module

    def exec_module(self, module):
        module.__spec__ = self.flat_spec  # the import machinery just stamped the alias spec; reload needs the real one


class _OneModuleObject(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        head, _, name = fullname.partition(".")
        if head == "veri" and name.isidentifier() and (SCRIPTS / "veri" / (name + ".py")).is_file():
            return importlib.util.spec_from_loader(fullname, _FlatAlias())
        return None


sys.meta_path[:] = [f for f in sys.meta_path if not isinstance(f, _OneModuleObject)]
sys.meta_path.insert(0, _OneModuleObject())
for _name in [n for n in sys.modules if n.startswith("veri.") and n.count(".") == 1]:
    _flat = _name.removeprefix("veri.")
    if (SCRIPTS / "veri" / (_flat + ".py")).is_file():
        sys.modules[_name] = sys.modules.setdefault(_flat, sys.modules[_name])

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

    monkeypatch.setattr(importlib.import_module("pid_file"), "ps_field", ps, raising=True)


def live_conductor(monkeypatch, run_tdd, issue):
    """A conductor.pid in <run_tdd> that answers kill -0, its process a claude under run_conductor.py."""
    (run_tdd / "conductor.pid").write_text("%d\n" % os.getpid())
    fake_pid_file_ps(monkeypatch)




@pytest.fixture(autouse=True, scope="session")
def repo_templates_under_basetemp(tmp_path_factory):
    """repo_builder.new_repo keeps its templates under this worker's --basetemp, which the leg cleans up (#3931)."""
    repo_builder.TEMPLATE_ROOT = tmp_path_factory.getbasetemp() / "repo-templates"


@pytest.fixture(scope="session")
def tests_py_index():
    return tests_py_index_of(pathlib.Path(__file__).resolve().parent)


@pytest.fixture(scope="session")
def veri_modules_index():
    # The pytest leg (tests/leg/) is the product's own test launcher and imports veri/'s interface, so its modules count
    # as users of veri/'s names in the index audits; it moved out of veri/ (#4051). tests/py files never count.
    return VeriModules(SCRIPTS / "veri", users=SCRIPTS / "tests" / "leg")


REAL_RUN, REAL_POPEN = subprocess.run, subprocess.Popen


# The floor guard stays here: tests patch conftest.REAL_RUN and conftest.SCRIPTS to count how meets_floor reaches its interpreter.
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


def interpreter_venv():
    """The venv a process case hands a shim as VERI_VENV: the one running pytest, else the outer VERI_VENV or
    ~/.veri-tools/venv. A case with a scratch HOME and no VERI_VENV would leave the shim on PATH's python3,
    /usr/bin/python3 3.9 on the development Mac, under the 3.12 floor (#2106)."""
    if sys.prefix != sys.base_prefix and os.access(os.path.join(sys.prefix, "bin", "python3"), os.X_OK):
        return sys.prefix
    return os.environ.get("VERI_VENV") or os.path.expanduser("~/.veri-tools/venv")


INTERPRETER_VENV = interpreter_venv()


def pytest_configure(config):
    config.option.importmode = "append"
    register_markers(config)


CWD_OUTSIDE_REPOSITORY = {
    "test_affected_suites.py",
    "test_affected_suites_process.py",
    "test_build_verify_prompt.py",
    "test_event.py",
    "test_invisible_work.py",
    "test_invisible_work_process.py",
    "test_parallel_conductors.py",
    "test_pr_ready.py",
    "test_push_branch.py",
    "test_pytest_leg.py",
    "test_rebase_onto_default.py",
    "test_rebase_onto_default_process.py",
    "test_refactor_touched.py",
    "test_refactor_touched_process.py",
    "test_release_issue.py",
    "test_solvable_issues.py",
    "test_solvable_issues_process.py",
    "test_stack_land.py",
    "test_stack_red.py",
    "test_status.py",
    "test_status_process.py",
    "test_timed_test_run.py",
    "test_timed_test_run_process.py",
    "test_transform_touches_tests.py",
    "test_transform_touches_tests_process.py",
    "test_verify.py",
    "test_verify_process.py",
    "test_verify_prompt_retirements.py",
    "test_wait_ci.py",
    "test_workqueue.py",
    "test_workqueue_process.py",
}




@pytest.fixture(autouse=True)
def hermetic_environment(request, monkeypatch, tmp_path, tmp_path_factory):
    offline, doomed = {}, []
    for name, value in os.environ.items():
        if (name in ("GIT_CONFIG_COUNT", "GIT_TEMPLATE_DIR", "GIT_EXEC_PATH")
                or name.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))):
            offline[name] = value
        if name.startswith(("VERI_", "CLAUDE_", "GH_", "GIT_")) and name != "VERI_VENV":
            doomed.append(name)
        elif name == "LANG" or name.startswith("LC_"):
            doomed.append(name)
        elif name in ("PYTEST_PLUGINS", "PYTEST_XDIST_WORKER"):
            doomed.append(name)
    for name in doomed:
        monkeypatch.delenv(name)
    if request.node.path.name in CWD_OUTSIDE_REPOSITORY:
        monkeypatch.chdir(tmp_path)
    else:
        cwd = os.path.realpath(os.getcwd())
        if cwd == ROOT_NAME or cwd.startswith(ROOT_NAME + os.sep):
            monkeypatch.chdir(ROOT)
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(tmp_path / "veri-pytest-legs"))
    monkeypatch.setenv("VERI_TEST_CEILING_FILE", str(tmp_path / "veri-test-ceiling"))
    monkeypatch.setenv("VERI_TEST_CAP_FILE", str(tmp_path / "veri-test-cap"))
    monkeypatch.setenv("VERI_TEST_LOAD_FILE", str(tmp_path / "veri-test-load"))
    monkeypatch.setenv("VERI_TEST_TIMEOUTS_FILE", str(tmp_path / "veri-test-timeouts"))
    monkeypatch.setenv("VERI_TEST_BUDGET_DIR", str(tmp_path / "veri-test-budget"))
    monkeypatch.setenv("VERI_MIN_FREE_GB", "0")
    if request.node.get_closest_marker("process") is not None:
        monkeypatch.setenv("VERI_POLL", SUPERVISOR_POLL)
    monkeypatch.setenv("VERI_HOME", str(tmp_path))
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")
    monkeypatch.setenv("VERI_VENV", INTERPRETER_VENV)
    inherited = os.path.realpath(tempfile.tempdir or os.environ.get("TMPDIR") or "/tmp")
    basetemp = os.path.realpath(tmp_path_factory.getbasetemp())
    case_tmpdir = tempfile.mkdtemp(prefix="tmpdir_", dir=tmp_path_factory.getbasetemp())
    monkeypatch.setenv("TMPDIR", case_tmpdir)
    monkeypatch.setattr(tempfile, "tempdir", case_tmpdir)
    for name, value in offline.items():
        monkeypatch.setenv(name, value)
    if "github" in sys.modules:
        # github.trusted_comment reads the gh login once per process; a case must not inherit another case's.
        monkeypatch.setattr(sys.modules["github"], "_TRUSTING_LOGIN", {})

    def refuse_inherited_tmpdir(path, frame):
        if not isinstance(path, (str, bytes, os.PathLike)):
            return
        if not os.path.basename(frame.f_code.co_filename).startswith(("test_", "conftest")):
            return
        target = os.path.realpath(os.fsdecode(path))
        if target.startswith(inherited + os.sep) and not target.startswith(basetemp + os.sep):
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


# A file whose mtime or ctime lies within this window of the snapshot may be rewritten into the same
# stat fingerprint (a coarse kernel clock, a same-size rewrite), so the snapshot keeps its bytes (#3002).
RACY_NS = 2_000_000_000
# The unmarked-case guard swaps os.scandir for one that refuses repository directories; the snapshot lists one.
REAL_SCANDIR = os.scandir


def veri_pycache_snapshot(cache):
    """name -> (inode, size, mtime_ns, ctime_ns), plus the bytes of each racy file; no file is opened but a racy one."""
    now = time_ns()
    stats, racy = {}, {}
    try:
        entries = [entry for entry in REAL_SCANDIR(cache) if not entry.name.startswith(".")]
    except FileNotFoundError:
        return stats, racy
    for entry in entries:
        found = entry.stat()
        name = f"{cache.name}/{entry.name}"
        stats[name] = (found.st_ino, found.st_size, found.st_mtime_ns, found.st_ctime_ns)
        if now - max(found.st_mtime_ns, found.st_ctime_ns) < RACY_NS:
            racy[name] = (cache.parent / name).read_bytes()
    return stats, racy


def veri_pycache_changed(cache, before, after):
    """The names whose file differs between two snapshots: a stat fingerprint that moved, or a racy file's bytes."""
    (stats_before, racy_before), (stats_after, _) = before, after
    changed = {name for name in stats_before.keys() | stats_after.keys() if stats_before.get(name) != stats_after.get(name)}
    for name, content in racy_before.items():
        if name not in changed and (cache.parent / name).read_bytes() != content:
            changed.add(name)
    return sorted(changed)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    cache = SCRIPTS / "veri" / "__pycache__"
    before = veri_pycache_snapshot(cache)
    result = yield
    changed = veri_pycache_changed(cache, before, veri_pycache_snapshot(cache))
    if changed:
        raise AssertionError(f"the case left {cache} changed: {', '.join(changed)}")
    return result




def evict_planted_modules(present, basetemp):
    """Drops each module that is not in `present` and was loaded from a file under `basetemp`.

    pytest's default import mode caches a planted test module by its basename, so one a call imported from its tree would
    make the next tree planting that basename fail collection with `import file mismatch`. Only modules loaded from under
    the run's --basetemp, where every case's tmp_path lives, go: veri's own and pytest's plugins never live there."""
    root = os.path.join(os.path.realpath(basetemp), "")
    for name, mod in list(sys.modules.items()):
        path = getattr(mod, "__file__", None)
        if name not in present and isinstance(path, str) and os.path.realpath(path).startswith(root):
            sys.modules.pop(name, None)


@pytest.fixture
def run_cli(monkeypatch, capfd, tmp_path_factory):
    present, basetemp = set(sys.modules), tmp_path_factory.getbasetemp()

    def run(module, argv, stdin="", env=None, cwd=None):
        for name, value in (env or {}).items():
            monkeypatch.setenv(name, value)
        if cwd is not None:
            monkeypatch.chdir(cwd)
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
        monkeypatch.setattr(sys, "path", list(sys.path))
        evict_planted_modules(present, basetemp)
        for name, mod in list(sys.modules.items()):
            if isinstance(getattr(mod, "__file__", None), str) and not os.path.exists(mod.__file__):
                monkeypatch.delitem(sys.modules, name)
        environ, start = dict(os.environ), os.getcwd()
        try:
            code = entry.exit_code(module.main, argv, on_broken_pipe=lambda: None)
        except SystemExit as exit:
            code = exit.code
        finally:
            if dict(os.environ) != environ:
                os.environ.clear()
                os.environ.update(environ)
            os.chdir(start)
        if code is not None and not isinstance(code, int):
            sys.stderr.write("%s\n" % (code,))
            sys.stderr.flush()
            code = 1
        out, err = capfd.readouterr()
        return 0 if code is None else code, out, err

    yield run
    evict_planted_modules(present, basetemp)


@pytest.fixture
def frozen_heap():
    """Keeps the cost of a pytest session a case starts in-process independent of how much the run has loaded so far.

    pytest ends every session with five full `gc.collect()` calls (its unraisable-exception plugin), each walking every
    object the worker holds, so a nested leg's time grew with the suite: three sessions reached the 30 s case timeout on
    CI. `gc.freeze()` moves what exists into the permanent generation, which a collection skips; what the nested
    session allocates is still collected."""
    gc.freeze()
    try:
        yield
    finally:
        gc.unfreeze()


@pytest.fixture
def fake_processes(monkeypatch):
    """Fakes every way subprocess starts a process, so a unit case starts none: `fake_processes.answers({prefix: answer})`.
    The interface (answers table, sequences, exceptions, the five entry points, calls/argvs/seen/rests/popens, FakePopen,
    the legacy `fake_processes(answer)` form) is the docstring of process_fakes.py."""
    return process_fakes.installer(monkeypatch)


@pytest.fixture
def fed_history(monkeypatch, tmp_path):
    """Answers case_history's git queries from a table of named revisions:
    `fed_history((name, subject, {path: text}), ..., root=tmp_path, branch="main")`; see fed_history.py."""
    import fed_history as table
    return table.feeder(monkeypatch, tmp_path)


@pytest.fixture
def fed_commits(fed_history, fake_processes, tmp_path):
    """`repo = fed_commits(root=tmp_path, branch="main", default=None)`: a git index and commit log over the work tree
    `root` (`repo.add(*paths)`, `repo.commit(subject, all=False)`, `repo.mv(source, target)`, `repo.head`,
    `repo.checkout(rev)`, `repo.ref(name)`; `default` is origin's default branch), each commit fed
    to case_history through fed_history; the pass marker's git calls answered by fake_processes. See fed_history.py."""
    import fed_history as table

    def start(root=tmp_path, branch="main", default=None):
        repo = table.FedCommits(fed_history, root, branch, default)
        fake_processes.answers(repo.git_answers())
        return repo
    return start


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
    return json.dumps([{"number": number, "title": "an issue", "state": "OPEN", "body": "", "author_association": "OWNER",
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


RECEIPT_SHA = "0123456789abcdef0123456789abcdef01234567"


@pytest.fixture
def leave_receipt(monkeypatch):
    """Leave a pin-recheck-ok receipt beside a ledger; in-process, git() answers that sha with no path changed."""
    return receipt_leaver(monkeypatch)


def _receipt_git(*args, **kwargs):
    """leave_receipt's git(): the receipt's sha with no path changed while it is set on a git module, else git.

    It is set on the git modules themselves too, so a module first imported during a case (`from git import git`)
    binds it, and monkeypatch never restores that binding. So it answers only while still set on a git module and
    runs git like git.git once the case is undone: else such a module, `ledger` imported by an entry point under
    the receipt, kept an empty `git show` for every later case in the process (#3053). One function for the whole
    session, so the next receipt revives a binding an earlier case left."""
    if importlib.import_module("git").git is not _receipt_git:
        return subprocess.run(["git", *args], **kwargs)
    text = kwargs.get("text") or kwargs.get("universal_newlines")
    out = RECEIPT_SHA + "\n" if args[:1] == ("rev-parse",) else ""
    return subprocess.CompletedProcess(args, 0, out if text else out.encode(), "" if text else b"")


def receipt_leaver(monkeypatch):
    """leave_receipt's leave(ledger, repo=None), its fake git() set through and undone with `monkeypatch`."""
    def leave(ledger, repo=None):
        sha = RECEIPT_SHA
        if repo is not None:
            sha = REAL_RUN(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
        else:
            reals = {importlib.import_module("git").git}
            for module in list(sys.modules.values()):
                if getattr(module, "git", None) in reals:
                    monkeypatch.setattr(module, "git", _receipt_git)
        (pathlib.Path(ledger).parent / "pin-recheck-ok").write_text(sha + "\n")

    return leave
