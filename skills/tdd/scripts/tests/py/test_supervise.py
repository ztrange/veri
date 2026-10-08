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


def clean_env(monkeypatch, **env):
    """No VERI_* variable but the ones given."""
    for key in list(os.environ):
        if key.startswith("VERI_"):
            monkeypatch.delenv(key)
    for key, value in env.items():
        monkeypatch.setenv(key, value)


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
            clean_env(monkeypatch, **env)
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
        clean_env(monkeypatch, VERI_ISSUE="", VERI_KILL_POLL=value)
        calls = fake_git_only(monkeypatch, work)
        code = supervise.main(argv)
        out, err = capsysbinary.readouterr()
        assert (code, out, err, os.listdir(work / ".tdd"), all(c[0] == "git" for c in calls)) == (
            2, b"", f"supervise: VERI_KILL_POLL must be a non-negative number: {value}\n".encode(),
            ["issue-954-timeout"], True), value

    work = tmp_path / "poll-empty"
    work.mkdir()
    monkeypatch.chdir(work)
    clean_env(monkeypatch, VERI_KILL_POLL="")
    fake_git_only(monkeypatch, work)
    with pytest.raises(Launched):
        supervise.main(argv)
    assert b"VERI_KILL_POLL" not in capsysbinary.readouterr().err


def fake_leaf_launch(monkeypatch):
    """date, stat and git answered in-process; a Popen of a /bin/sh -c wrapper runs that wrapper for real, to its end."""
    real_popen = subprocess.Popen
    launches = []

    def answer(args, kwargs):
        args = list(args)
        if args[:1] == ["git"]:
            out = "0123456789abcdef0123456789abcdef01234567\n"
        elif args[:1] in (["date"], ["stat"]):
            out = "1000\n"
        else:
            out = ""
        if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
            out = out.encode()
        return out

    def run(args, *_, **kwargs):
        out = answer(args, kwargs)
        return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

    def popen(args, *a, **kwargs):
        launches.append((list(args), dict(kwargs)))
        if list(args[:2]) != ["/bin/sh", "-c"]:
            return real_popen(["true"])
        leaf = real_popen(args, *a, **kwargs)
        leaf.wait()
        return leaf

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: answer(args, k))
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: 0)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: 0)
    monkeypatch.setattr(subprocess, "Popen", popen)
    return launches


def test_main_launches_the_leaf_through_one_sh_wrapper_in_its_own_group_logging_it_and_recording_its_rc_then_reports_success_or_failure(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    clean_env(monkeypatch)

    answers = []
    for rc in (0, 1):
        work = tmp_path / f"rc-{rc}"
        work.mkdir()
        monkeypatch.chdir(work)
        launches = fake_leaf_launch(monkeypatch)
        leaf = ["sh", "-c", f"printf 'leaf out\\n'; printf 'leaf err\\n' >&2; exit {rc}"]
        code = supervise.main(["verdict-red", *leaf])
        out, err = capsysbinary.readouterr()

        def read(name):
            path = work / ".tdd" / name
            return path.read_bytes() if path.exists() else None

        answers.append((
            code, out, err.splitlines()[-1:],
            read("verdict-red.log"), read("verdict-red.rc"), read("verdict-red.exit"),
            [(args[:2], kwargs.get("process_group"), kwargs.get("stdin")) for args, kwargs in launches],
        ))

    assert answers == [
        (0, b"leaf out\nleaf err\n", [b"supervise[verdict-red]: success"],
         b"leaf out\nleaf err\n", b"0\n", b"0\n", [(["/bin/sh", "-c"], 0, None)]),
        (1, b"leaf out\nleaf err\n", [b"supervise[verdict-red]: failure"],
         b"leaf out\nleaf err\n", b"1\n", b"1\n", [(["/bin/sh", "-c"], 0, None)]),
    ]
