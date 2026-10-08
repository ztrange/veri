"""In-process cases for veri/supervise.py, the module supervise.sh is a shim over."""
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

USAGE = b"usage: supervise.sh <name> <cmd> [args...]\n"


@pytest.fixture
def supervise():
    return importlib.import_module("veri.supervise")


def fake_processes(monkeypatch):
    """Every subprocess entry point recording each command it was asked to start."""
    calls = []

    def record(args, *_, **__):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, record)
    return calls


def test_main_refuses_a_missing_or_empty_name_and_a_missing_cmd_with_its_usage_line_starting_nothing_and_writing_nothing(
        monkeypatch, tmp_path, capsysbinary, supervise):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(monkeypatch)

    answers = []
    for argv in ([], [""], ["develop-red"]):
        code = supervise.main(argv)
        answers.append((argv, code, capsysbinary.readouterr()))

    assert answers == [
        ([], 2, (b"", USAGE)),
        ([""], 2, (b"", USAGE)),
        (["develop-red"], 2, (b"", b"supervise: missing <cmd>\n" + USAGE)),
    ]
    assert calls == []
    assert sorted(os.listdir(tmp_path)) == []


class Launched(BaseException):
    """Raised by the fake process boundary when main starts anything but git."""


def fake_git_only(monkeypatch, toplevel):
    """Every subprocess entry point: git answers rev-parse (failing when toplevel is None), anything else is a launch."""
    calls = []

    def answer(args, kwargs):
        calls.append(list(args))
        if not args or args[0] != "git":
            raise Launched(args)
        if "--show-toplevel" in args:
            code, out = (128, "") if toplevel is None else (0, f"{toplevel}\n")
        else:
            code, out = 0, "0123456789abcdef0123456789abcdef01234567\n"
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out = out.encode()
        return code, out

    def run(args, *_, **kwargs):
        code, out = answer(args, kwargs)
        if code and kwargs.get("check"):
            raise subprocess.CalledProcessError(code, args, out, "")
        return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

    def check_output(args, *_, **kwargs):
        code, out = answer(args, kwargs)
        if code:
            raise subprocess.CalledProcessError(code, args, out)
        return out

    def popen(args, *_, **kwargs):
        answer(args, kwargs)
        raise Launched(args)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", check_output)
    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
    return calls


def test_main_refuses_a_settled_timeout_not_a_whole_number_of_seconds_and_a_kill_poll_not_a_non_negative_number_starting_nothing_but_git_and_creating_no_tdd(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    argv = ["develop-red", "true"]

    def clean_env(**env):
        for key in list(os.environ):
            if key.startswith("VERI_"):
                monkeypatch.delenv(key)
        for key, value in env.items():
            monkeypatch.setenv(key, value)

    def settled(root, content):
        (root / ".tdd").mkdir(parents=True)
        (root / ".tdd" / "issue-954-timeout").write_text(content)

    for n, (content, shown) in enumerate((("", ""), ("abc\n\n", "abc"), ("0\n", "0"), ("00", "00"))):
        for env in ({"VERI_ISSUE": "954"}, {"VERI_ISSUE": "954", "VERI_TIMEOUT": ""}):
            top = tmp_path / f"top-{n}-{len(env)}"
            work = top / "sub"
            work.mkdir(parents=True)
            settled(top, content)
            monkeypatch.chdir(work)
            clean_env(**env)
            calls = fake_git_only(monkeypatch, top)
            code = supervise.main(argv)
            out, err = capsysbinary.readouterr()
            assert (code, out, err, sorted(os.listdir(work)), all(c[0] == "git" for c in calls)) == (
                2, b"",
                f"supervise: {top}/.tdd/issue-954-timeout must hold a whole number of seconds >= 1: '{shown}'\n".encode(),
                [], True), (content, env)

            bare = tmp_path / f"bare-{n}-{len(env)}"
            settled(bare, content)
            monkeypatch.chdir(bare)
            calls = fake_git_only(monkeypatch, None)
            code = supervise.main(argv)
            out, err = capsysbinary.readouterr()
            assert (code, out, err, sorted(os.listdir(bare)), os.listdir(bare / ".tdd"),
                    all(c[0] == "git" for c in calls)) == (
                2, b"",
                f"supervise: .tdd/issue-954-timeout must hold a whole number of seconds >= 1: '{shown}'\n".encode(),
                [".tdd"], ["issue-954-timeout"], True), (content, env)

    for value in ("abc", "-1", "1.", ".5"):
        work = tmp_path / f"poll-{value}"
        settled(work, "abc")
        monkeypatch.chdir(work)
        clean_env(VERI_ISSUE="", VERI_KILL_POLL=value)
        calls = fake_git_only(monkeypatch, work)
        code = supervise.main(argv)
        out, err = capsysbinary.readouterr()
        assert (code, out, err, os.listdir(work / ".tdd"), all(c[0] == "git" for c in calls)) == (
            2, b"", f"supervise: VERI_KILL_POLL must be a non-negative number: {value}\n".encode(),
            ["issue-954-timeout"], True), value

    work = tmp_path / "poll-empty"
    work.mkdir()
    monkeypatch.chdir(work)
    clean_env(VERI_KILL_POLL="")
    fake_git_only(monkeypatch, work)
    with pytest.raises(Launched):
        supervise.main(argv)
    assert b"VERI_KILL_POLL" not in capsysbinary.readouterr().err
