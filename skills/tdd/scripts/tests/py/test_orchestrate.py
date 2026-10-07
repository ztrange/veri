"""In-process cases for veri/orchestrate.py, the module orchestrate.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def orchestrate():
    return importlib.import_module("veri.orchestrate")


def _boundaries(monkeypatch, solvable):
    """Fake solvable-issues.sh answering <solvable> = (exit code, stdout) and the conductor launch;
    return the lists of asks and launches they record."""
    asks, launches = [], []

    def fake_run(args, *rest, **kwargs):
        if pathlib.Path(args[0]).name != "solvable-issues.sh":
            raise AssertionError("unexpected subprocess.run call: %r" % (args,))
        asks.append(list(args))
        stdout = solvable[1]
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            stdout = stdout.encode()
        return subprocess.CompletedProcess(args, solvable[0], stdout, None)

    def fake_popen(args, *rest, **kwargs):
        launches.append(list(args))
        raise AssertionError("no conductor should launch: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return asks, launches


def test_a_bad_budget_refuses_before_any_ask_and_a_solvable_answer_of_1_or_3_ends_the_run_with_its_exit_code(
        capsys, monkeypatch, tmp_path, orchestrate):
    monkeypatch.chdir(tmp_path)

    monkeypatch.setenv("VERI_CONDUCTOR_CTX_BUDGET", "120k")
    asks, launches = _boundaries(monkeypatch, (0, "7\n"))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: 120k\n")
    assert (asks, launches) == ([], [])

    monkeypatch.delenv("VERI_CONDUCTOR_CTX_BUDGET")
    asks, launches = _boundaries(monkeypatch, (1, ""))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "orchestrate.sh: solvable-issues.sh exited 1; no answer about the solvable set\n")
    assert len(asks) == 1 and launches == []

    asks, launches = _boundaries(monkeypatch, (3, ""))
    code = orchestrate.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "", "")
    assert len(asks) == 1 and launches == []
