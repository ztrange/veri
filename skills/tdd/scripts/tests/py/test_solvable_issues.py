"""In-process cases for veri/solvable_issues.py, the module solvable-issues.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: solvable-issues.sh [--repo owner/name]\n"


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_LABEL", "VERI_PRIORITY_LABEL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def solvable_issues():
    return importlib.import_module("veri.solvable_issues")


def no_process(monkeypatch):
    """subprocess.run and subprocess.Popen recording every command they are asked to start."""
    started = []

    def refuse(args, *rest, **kwargs):
        started.append(args)
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    return started


@pytest.mark.parametrize("argv", [["--repo"], ["--repo", ""]])
def test_main_refuses_repo_with_no_value_or_an_empty_one_with_2_and_the_usage_line_alone_starting_no_process(argv, monkeypatch, capsys, solvable_issues):
    started = no_process(monkeypatch)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)
