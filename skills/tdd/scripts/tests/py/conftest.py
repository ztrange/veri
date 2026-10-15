import errno
import io
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
ROOT = SCRIPTS.parents[2]
for path in (SCRIPTS / "veri", SCRIPTS):
    while str(path) in sys.path:
        sys.path.remove(str(path))
    sys.path.insert(0, str(path))

from veri import entry

REAL_RUN, REAL_POPEN = subprocess.run, subprocess.Popen


CANONICAL_SHIM = re.compile(r'exec python3 "\$\(dirname "\$0"\)/(veri/[\w-]+\.py)" "\$@"')


def shim_problems(scripts, exempt=()):
    problems = []
    seen = set()
    for script in sorted(pathlib.Path(scripts).glob("*.sh")):
        seen.add(script.name)
        code = [line for line in script.read_text().splitlines() if line.strip() and not line.startswith("#")]
        match = CANONICAL_SHIM.fullmatch(code[0]) if len(code) == 1 else None
        if match is not None and script.name in exempt:
            problems.append("%s: stale exemption, the script is now the canonical shim" % script.name)
        elif match is None and script.name not in exempt:
            problems.append("%s: not the canonical shim" % script.name)
        elif match is not None and not (script.parent / match.group(1)).is_file():
            problems.append("%s: %s does not exist" % (script.name, match.group(1)))
    problems += ["%s: stale exemption, the script is gone" % name for name in sorted(set(exempt) - seen)]
    return problems


def pytest_configure(config):
    config.option.importmode = "append"
    config.addinivalue_line("markers", "process(boundary): a medium case, naming the process boundary it observes")
    config.addinivalue_line("markers", "tree_audit(sweeps): a case that lists the repository's own directories, run by make test and not make unit")


def pytest_collection_modifyitems(config, items):
    registered = {line.split(":")[0].split("(")[0].strip() for line in config.getini("markers")}
    unregistered = ["%s (%s)" % (item.nodeid, mark.name) for item in items
                    for mark in item.iter_markers() if mark.name not in registered]
    if unregistered:
        raise pytest.UsageError("unregistered mark: %s" % ", ".join(unregistered))
    for name, missing in (("process", "a boundary"), ("tree_audit", "a sweep")):
        unnamed = [item.nodeid for item in items
                   if any(not mark.args or not mark.args[0] for mark in item.iter_markers(name))]
        if unnamed:
            raise pytest.UsageError("%s mark without %s: %s" % (name, missing, ", ".join(unnamed)))


@pytest.fixture(autouse=True)
def hermetic_environment(monkeypatch):
    offline = {name: value for name, value in os.environ.items()
               if name == "GIT_CONFIG_COUNT" or name.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    for name in list(os.environ):
        if name.startswith(("VERI_", "CLAUDE_", "GH_", "GIT_")) and name != "VERI_VENV":
            monkeypatch.delenv(name)
        elif name == "LANG" or name.startswith("LC_"):
            monkeypatch.delenv(name)
    if ROOT in pathlib.Path.cwd().resolve().parents or pathlib.Path.cwd().resolve() == ROOT:
        monkeypatch.chdir(ROOT)
    monkeypatch.setenv("LC_ALL", "C")
    for name, value in offline.items():
        monkeypatch.setenv(name, value)


@pytest.fixture(autouse=True)
def small_case_guard(request, monkeypatch):
    if request.node.get_closest_marker("process") is None:
        monkeypatch.setenv("PATH", str(SCRIPTS / "tests" / "unit-guard") + os.pathsep + os.environ.get("PATH", ""))


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
        if (listed == ROOT or ROOT in listed.parents) and scratch != listed and scratch not in listed.parents and listed.is_dir():
            raise AssertionError("%s lists the repository directory %s: mark it tree_audit" % (request.node.nodeid, listed))

    for name in ("scandir", "listdir"):
        monkeypatch.setattr(os, name, checked(getattr(os, name)))


STARTS_PYTEST_EXEMPT = {
    "test_run_suite.py::test_main_runs_a_pytest_suite_under_the_venv_python_and_maps_its_exit_code_without_a_count_line_check":
        "run_suite.run_pytest is the subject; the interpreter it starts is a stub in the case's scratch venv",
    "test_run_suite.py::test_main_hands_a_pytest_suite_no_ambient_veri_or_claude_variable_but_veri_venv_and_still_finds_the_caller_venv_1258":
        "run_suite.run_pytest is the subject; the interpreter it starts is a stub in the case's scratch venv",
    "test_conftest.py::test_a_case_reading_a_cwd_relative_path_gives_the_same_outcome_started_from_the_repository_root_as_from_skills_tdd_scripts":
        "the pytest session started from two directories is the subject",
    "test_conftest.py::test_the_path_setup_case_gives_the_same_outcome_started_from_skills_tdd_scripts_with_a_relative_path_as_from_the_repository_root":
        "the pytest session started from two directories is the subject",
}


@pytest.fixture(autouse=True)
def case_starts_no_test_runner(request, monkeypatch):
    real = subprocess.Popen.__init__

    def is_pytest(words):
        names = [os.path.basename(os.fsdecode(w)) for w in words]
        if names[0] in ("pytest", "py.test") or "pytest_leg.py" in names:
            return True
        return names[0].startswith("python") and any(a == "-m" and b == "pytest" for a, b in zip(names, names[1:]))

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

    def checked(self, args, *rest, **kwargs):
        words = [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)
        if isinstance(args, str) and kwargs.get("shell"):
            words = shlex.split(args)
        if words and (is_suite(words[0]) or (os.path.basename(os.fsdecode(words[0])) in ("bash", "sh") and any(is_suite(w) for w in words[1:]))):
            raise AssertionError("%s starts a bash suite: %s" % (request.node.nodeid, " ".join(os.fsdecode(w) for w in words)))
        if words and is_pytest(words) and not from_exempt_helper() and request.node.nodeid.split('/')[-1] not in STARTS_PYTEST_EXEMPT:
            raise AssertionError("%s starts pytest: %s" % (request.node.nodeid, " ".join(os.fsdecode(w) for w in words)))
        return real(self, args, *rest, **kwargs)

    monkeypatch.setattr(subprocess.Popen, "__init__", checked)


@pytest.fixture
def run_cli(monkeypatch, capfd):
    def run(module, argv, stdin="", env=None, cwd=None):
        for name, value in (env or {}).items():
            monkeypatch.setenv(name, value)
        if cwd is not None:
            monkeypatch.chdir(cwd)
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
        environ, start = dict(os.environ), os.getcwd()
        try:
            code = module.main(argv)
        except SystemExit as exit:
            code = exit.code
        except BrokenPipeError:
            code = entry.BROKEN_PIPE
        except Exception as exc:
            sys.stderr.write(entry.refusal(module.main, exc))
            sys.stderr.flush()
            code = 2
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
