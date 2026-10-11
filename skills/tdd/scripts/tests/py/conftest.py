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
    for name in list(os.environ):
        if name.startswith(("VERI_", "CLAUDE_", "GH_", "GIT_")) and name != "VERI_VENV":
            monkeypatch.delenv(name)
        elif name == "LANG" or name.startswith("LC_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("LC_ALL", "C")


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

