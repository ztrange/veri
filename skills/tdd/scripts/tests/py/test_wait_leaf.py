"""In-process cases for veri/wait_leaf.py, the module wait-leaf.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: wait-leaf.sh <name> [max-seconds]\n"


@pytest.fixture
def wait_leaf():
    return importlib.import_module("veri.wait_leaf")


def fake_processes(monkeypatch, answer):
    """subprocess.run recording each command as one line, its program by basename;
    <answer>(line) -> (exit code, stdout, stderr)."""
    calls = []

    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        code, out, err = answer(line)
        return subprocess.CompletedProcess(args, code, out, err)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_refuses_a_missing_name_answers_a_recorded_code_and_times_out_with_3(
        monkeypatch, capsys, tmp_path, wait_leaf):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch, lambda line: (0, "1000\n", "") if line == "date +%s" else (0, "", ""))

    refusals = []
    for argv in ([], [""]):
        code = wait_leaf.main(argv)
        captured = capsys.readouterr()
        refusals.append((code, captured.out, captured.err))
    assert refusals == [(2, "", USAGE), (2, "", USAGE)]
    assert calls == []

    (tmp_path / ".tdd").mkdir()
    recorded = []
    for text in ("0\n", "1\n", "2\n", "3\n", "5\n"):
        (tmp_path / ".tdd" / "x.exit").write_text(text)
        recorded.append(wait_leaf.main(["x"]))
    assert recorded == [0, 1, 2, 3, 2]

    (tmp_path / ".tdd" / "x.exit").unlink()
    assert wait_leaf.main(["x", "0"]) == 3
