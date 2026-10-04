"""In-process cases for veri/invisible_work.py, the module invisible-work.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def fake_processes(monkeypatch, answer):
    """subprocess.run recording each command as one line, its program by basename;
    <answer>(line) -> exit code, with empty output."""
    calls = []

    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        code = answer(line)
        if kwargs.get("check") and code != 0:
            raise subprocess.CalledProcessError(code, args, "", "")
        empty = "" if kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines") else b""
        return subprocess.CompletedProcess(args, code, empty, empty)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_returns_2_with_empty_stdout_when_origin_is_unreachable_or_origin_head_is_unset(
        monkeypatch, tmp_path, capsys):
    invisible_work = importlib.import_module("veri.invisible_work")
    (tmp_path / "issues.json").write_text("[]")
    (tmp_path / "prs.json").write_text("[]")

    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    unreachable_calls = fake_processes(
        monkeypatch, lambda line: 128 if line.startswith("git ls-remote --heads origin") else 0)
    unreachable = invisible_work.main([])
    unreachable_out = capsys.readouterr()

    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_processes(
        monkeypatch,
        lambda line: 128 if line.startswith("git symbolic-ref --short refs/remotes/origin/HEAD") else 0)
    unset_head = invisible_work.main([])
    unset_head_out = capsys.readouterr()

    assert (unreachable, unreachable_out.out, unset_head, unset_head_out.out) == (2, "", 2, "")
    assert unreachable_out.err.endswith("invisible-work.sh: cannot reach origin\n")
    assert [line for line in unreachable_calls if line.startswith("gh")] == []
