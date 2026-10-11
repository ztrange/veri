import errno
import io
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
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


def pytest_collection_modifyitems(config, items):
    registered = {line.split(":")[0].split("(")[0].strip() for line in config.getini("markers")}
    unregistered = ["%s (%s)" % (item.nodeid, mark.name) for item in items
                    for mark in item.iter_markers() if mark.name not in registered]
    if unregistered:
        raise pytest.UsageError("unregistered mark: %s" % ", ".join(unregistered))
    unnamed = [item.nodeid for item in items
               if any(not mark.args or not mark.args[0] for mark in item.iter_markers("process"))]
    if unnamed:
        raise pytest.UsageError("process mark without a boundary: %s" % ", ".join(unnamed))


@pytest.fixture(autouse=True)
def hermetic_environment(monkeypatch):
    offline = {name: value for name, value in os.environ.items()
               if name == "GIT_CONFIG_COUNT" or name.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    for name in list(os.environ):
        if name.startswith(("VERI_", "CLAUDE_", "GH_", "GIT_")) and name != "VERI_VENV":
            monkeypatch.delenv(name)
        elif name == "LANG" or name.startswith("LC_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("LC_ALL", "C")
    for name, value in offline.items():
        monkeypatch.setenv(name, value)


@pytest.fixture(autouse=True)
def small_case_guard(request, monkeypatch):
    if request.node.get_closest_marker("process") is None:
        monkeypatch.setenv("PATH", str(SCRIPTS / "tests" / "unit-guard") + os.pathsep + os.environ.get("PATH", ""))


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


def serve_listing(directory):
    """serve(answer): the open-issue and PR listings the real solvable-issues.sh selects from, written to
    <directory>. <answer> is the numbers of the open ready-for-agent issues (a list, each a number or a
    string), [] for no labelled open issue, or None for a listing the selection cannot read; <priority>
    names those carrying the priority label."""
    directory.mkdir(exist_ok=True)

    def serve(answer, priority=(), label="ready-for-agent"):
        (directory / "prs.json").write_text("[]")
        if answer is None:
            (directory / "issues.json").write_text("not json")
            return
        issues = [{"number": n, "title": "an issue", "state": "OPEN", "body": "",
                   "labels": [{"name": label}] + ([{"name": "priority"}] if n in priority else [])}
                  for n in answer]
        (directory / "issues.json").write_text(json.dumps(issues))

    serve.directory = directory
    return serve


@pytest.fixture
def listing(tmp_path):
    return serve_listing(tmp_path / "solvable-listing")


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


def run_over_listing(listing, args, *rest, **kwargs):
    """subprocess.run started as a real process over <listing> alone, although subprocess.Popen is faked."""
    env = dict(kwargs.pop("env", None) or os.environ, VERI_GH_JSON=str(listing.directory))
    for name in ("VERI_GH_DRIVER", "VERI_PRIORITY_LABEL"):
        env.pop(name, None)
    faked = subprocess.Popen
    subprocess.Popen = REAL_POPEN
    try:
        return REAL_RUN(args, *rest, env=env, **kwargs)
    finally:
        subprocess.Popen = faked


def listed_in_turn(listing, answers):
    """A subprocess.run that serves the next of <answers>, each (code, stdout[, priority numbers]), to
    listing, then starts the process over it."""
    pending = [(listed(*answer[:2]), answer[2:]) for answer in answers]

    def run(args, *rest, **kwargs):
        answer, priority = pending.pop(0) if len(pending) > 1 else pending[0]
        listing(answer, *priority)
        return run_over_listing(listing, args, *rest, **kwargs)

    return run
