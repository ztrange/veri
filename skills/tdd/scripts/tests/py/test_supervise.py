"""In-process cases for veri/supervise.py, the module supervise.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest


SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
USAGE = b"usage: supervise.sh <name> <cmd> [args...]\n"


REFUSAL = "supervise: refusing to launch {}: leaf {} (pid {}) is still alive in this worktree"
LIVE_LEAF_WINDOW = {"VERI_STUCK_RETRIES": "0", "VERI_HEARTBEAT": "30", "VERI_TIMEOUT": "60", "VERI_POLL": "0.02",
                    "VERI_KILL_POLL": "0.01"}


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def group_alive(pgid):
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    return True


def skill_head():
    return subprocess.run(["git", "-C", str(SCRIPTS), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


@pytest.fixture
def supervise():
    return importlib.import_module("veri.supervise")


def test_cli_refuses_no_argument_an_empty_name_and_a_name_alone_through_run_cli_with_exit_2_its_usage_line_nothing_on_stdout_and_no_tdd(
        monkeypatch, tmp_path, supervise, run_cli, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    usage = USAGE.decode()

    answers = [(argv, run_cli(supervise, argv, cwd=tmp_path)) for argv in ([], [""], ["develop-red"])]

    assert answers == [
        ([], (2, "", usage)),
        ([""], (2, "", usage)),
        (["develop-red"], (2, "", "supervise: missing <cmd>\n" + usage)),
    ]
    assert calls == []
    assert sorted(os.listdir(tmp_path)) == []


SET_BY_CLEAN_ENV = set()


def clean_env(monkeypatch, **env):
    """No VERI_* variable but the ones given."""
    for key in list(os.environ):
        if key in SET_BY_CLEAN_ENV:
            monkeypatch.delenv(key)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
        SET_BY_CLEAN_ENV.add(key)


def as_asked(out, kwargs):
    """out as the str or bytes the subprocess call's kwargs ask for."""
    if kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding"):
        return out
    return out.encode()


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
        return code, as_asked(out, kwargs)

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

    for n, (content, shown) in enumerate((("", ""), ("0\n\n", "0"), ("00", "00"))):
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


def test_cli_refuses_a_kill_poll_that_is_not_a_number_through_run_cli_with_exit_2_one_stderr_line_naming_it_and_its_value_starting_nothing(
        monkeypatch, tmp_path, supervise, run_cli, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes()
    clean_env(monkeypatch, VERI_TIMEOUT="900")

    answers = [run_cli(supervise, ["develop-red", "true"], env={"VERI_KILL_POLL": value}, cwd=tmp_path)
               for value in ("fast", "1e3")]

    assert answers == [
        (2, "", "supervise: VERI_KILL_POLL must be a non-negative number: fast\n"),
        (2, "", "supervise: VERI_KILL_POLL must be a non-negative number: 1e3\n"),
    ]
    assert calls == []
    assert sorted(os.listdir(tmp_path)) == []


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
        return as_asked(out, kwargs)

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


def test_main_maps_the_leaf_rc_to_its_exit_code_records_its_own_pid_and_clears_a_stale_log_rc_and_exit_before_the_launch_leaving_a_leafs_own_exit_record(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    clean_env(monkeypatch)

    leaves = {
        "rc-2": ("exit 2", False),
        "rc-3": ("exit 3", False),
        "rc-126": ("exit 126", False),
        "rc-127": ("exit 127", False),
        "rc-empty": ("exit 0", True),
        "own-exit": ("printf '7\\n' > .tdd/verdict-red.exit; exit 1", False),
    }
    real_popen = subprocess.Popen
    answers = {}
    for label, (script, empty_rc) in leaves.items():
        work = tmp_path / label
        (work / ".tdd").mkdir(parents=True)
        tdd = work / ".tdd"
        (tdd / "verdict-red.log").write_bytes(b"stale log\n")
        (tdd / "verdict-red.rc").write_bytes(b"0\n")
        (tdd / "verdict-red.exit").write_bytes(b"5\n")
        monkeypatch.chdir(work)
        monkeypatch.setattr(subprocess, "Popen", real_popen)
        fake_leaf_launch(monkeypatch)
        launching = subprocess.Popen
        seen = []

        def popen(args, *a, _launching=launching, _tdd=tdd, _empty_rc=empty_rc, _seen=seen, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                def read(name):
                    path = _tdd / name
                    return path.read_bytes() if path.exists() else None
                _seen.append((read("verdict-red.pid"), read("verdict-red.log"),
                              read("verdict-red.rc"), read("verdict-red.exit")))
            leaf = _launching(args, *a, **kwargs)
            if _empty_rc and list(args[:2]) == ["/bin/sh", "-c"]:
                (_tdd / "verdict-red.rc").write_bytes(b"")
            return leaf

        monkeypatch.setattr(subprocess, "Popen", popen)
        code = supervise.main(["verdict-red", "sh", "-c", script])
        _, err = capsysbinary.readouterr()
        answers[label] = (code, err.splitlines()[-1:], (tdd / "verdict-red.exit").read_bytes(), seen)

    before = (f"{os.getpid()}\n".encode(), b"", None, None)
    failure = [b"supervise[verdict-red]: failure"]
    assert answers == {
        "rc-2": (2, failure, b"2\n", [before]),
        "rc-3": (1, failure, b"1\n", [before]),
        "rc-126": (1, failure, b"1\n", [before]),
        "rc-127": (1, failure, b"1\n", [before]),
        "rc-empty": (1, failure, b"1\n", [before]),
        "own-exit": (1, failure, b"7\n", [before]),
    }


def test_main_marks_a_watched_names_launch_and_exit_as_records_under_its_role_and_none_for_a_verdict_or_refused_name_whose_failure_changes_nothing(
        monkeypatch, tmp_path, capsysbinary, supervise, events):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: 5000.0)

    def run_one(label, name, appendable, script, **env):
        work = tmp_path / label
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, **env)
        if not appendable:
            events.unappendable(work)
        fake_leaf_launch(monkeypatch)
        events.refuse_event_sh()
        code = supervise.main([name, "sh", "-c", script])
        out, err = capsysbinary.readouterr()
        exit_record = (work / ".tdd" / f"{name}.exit").read_bytes()
        role_lines = [line for line in err.splitlines() if line.startswith(b"leaf-role:")]
        return code, out, exit_record, events.records(work), role_lines

    context = {"issue": "1073", "actor": "developer", "phase": "red", "step": "4", "attempt": "1",
               "skill_commit": "0123456789abcdef0123456789abcdef01234567"}
    marked = [
        {**context, "event": "launch", "name": "develop-red", "cmd": "sh -c printf 'leaf out\\n'; exit 1",
         "model": "opus-x"},
        {**context, "event": "exit", "status": "1", "secs": "0"},
    ]
    leaf = "printf 'leaf out\\n'; exit 1"
    env = {"VERI_ISSUE": "1073", "VERI_STEP": "4", "VERI_MODEL": "opus-x", "VERI_TIMEOUT": "900"}
    assert run_one("ok", "develop-red", True, leaf, **env) == (1, b"leaf out\n", b"1\n", marked, [])
    assert run_one("failing", "develop-red", False, leaf, **env) == (1, b"leaf out\n", b"1\n", [], [])

    assert run_one("verdict", "verdict-plan", True, leaf, **env) == (1, b"leaf out\n", b"1\n", [], [])

    code, out, exit_record, records, role_lines = run_one("bogus", "bogus-x", True, "printf 'leaf out\\n'", **env)
    diagnostic = b"leaf-role: leaf name 'bogus-x' has an unknown leading word (want develop-*|revise-*|verify-*|conductor-*)"
    assert (code, out, exit_record, records, role_lines) == (0, b"leaf out\n", b"0\n", [], [diagnostic, diagnostic])


def test_main_hands_a_verify_leaf_veri_test_lock_0_and_a_develop_leaf_no_such_variable_2195(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    clean_env(monkeypatch, VERI_TIMEOUT="900")
    seen = {}
    for name in ("verify-red", "develop-red"):
        work = tmp_path / name
        work.mkdir()
        monkeypatch.chdir(work)
        fake_leaf_launch(monkeypatch)
        code = supervise.main([name, "sh", "-c", 'printf "%s" "${VERI_TEST_LOCK-unset}"'])
        out, _ = capsysbinary.readouterr()
        seen[name] = (code, out)

    assert seen == {"verify-red": (0, b"0"), "develop-red": (0, b"unset")}


def test_main_resolves_the_model_in_process_marks_it_on_the_launch_and_hands_the_leaf_its_own_environment_plus_veri_leaf_model_and_veri_skill_commit(
        monkeypatch, tmp_path, capsysbinary, supervise, events):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: 5000.0)
    monkeypatch.setenv("VERI_LEAF_MODEL", "ambient")
    monkeypatch.setenv("VERI_SKILL_COMMIT", "ambient")
    SET_BY_CLEAN_ENV.update(("VERI_LEAF_MODEL", "VERI_SKILL_COMMIT"))
    here = os.path.dirname(os.path.dirname(os.path.abspath(supervise.__file__)))
    sha = "0123456789abcdef0123456789abcdef01234567"
    whitespace = b"leaf-model: model 'opus x' contains whitespace (a model id or alias is one word)"

    def run_one(label, git_ok, **env):
        work = tmp_path / label
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="900", **env)
        fake_leaf_launch(monkeypatch)
        launching = subprocess.Popen
        leaf_envs = []

        def git(args, kwargs):
            if list(args) == ["git", "-C", here, "rev-parse", "HEAD"] and git_ok:
                return 0, as_asked(f"{sha}\n", kwargs)
            return 128, as_asked("", kwargs)

        def run(args, *a, **kwargs):
            args = [str(x) for x in args]
            if args[:1] == ["git"]:
                code, out = git(args, kwargs)
                if code and kwargs.get("check"):
                    raise subprocess.CalledProcessError(code, args, out)
                return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")
            out = as_asked("1000\n", kwargs)
            return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

        def check_output(args, *a, **kwargs):
            if [str(x) for x in args][:1] == ["git"]:
                code, out = git([str(x) for x in args], kwargs)
                if code:
                    raise subprocess.CalledProcessError(code, args, out)
                return out
            return run(args, *a, **kwargs).stdout

        def popen(args, *a, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                given = kwargs.get("env")
                leaf_envs.append(dict(os.environ if given is None else given))
            return launching(args, *a, **kwargs)

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", check_output)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)
        events.refuse_event_sh()
        before = dict(os.environ)
        code = supervise.main(["develop-red", "sh", "-c", "exit 0"])
        _, err = capsysbinary.readouterr()
        launches = [{k: r[k] for k in ("actor", "phase", "attempt", "model", "skill_commit")}
                    for r in events.records(work) if r["event"] == "launch"]
        handed = ("VERI_LEAF_MODEL", "VERI_SKILL_COMMIT")
        added = [{**{k: v for k, v in e.items() if k not in before or before[k] != v},
                  **{k: e.get(k) for k in handed}} for e in leaf_envs]
        dropped = [sorted(k for k in before if k not in e) for e in leaf_envs]
        return code, launches, added, dropped, err.splitlines().count(whitespace)

    def leaf(model, commit):
        return [{"VERI_LEAF_MODEL": model, "VERI_SKILL_COMMIT": commit}]

    def launch(model, commit):
        return [{"actor": "developer", "phase": "red", "attempt": "1", "model": model, "skill_commit": commit}]

    answers = {
        "chosen": run_one("chosen", True, VERI_MODEL="opus-x"),
        "none": run_one("none", True),
        "whitespace": run_one("whitespace", True, VERI_MODEL="opus x"),
        "dash-n": run_one("dash-n", True, VERI_MODEL="-n"),
        "dash-e": run_one("dash-e", True, VERI_MODEL="-e"),
        "dash-E": run_one("dash-upper-e", True, VERI_MODEL="-E"),
        "git-beats-inherited": run_one("git-beats-inherited", True, VERI_SKILL_COMMIT="inherited"),
        "inherited": run_one("inherited", False, VERI_SKILL_COMMIT="inherited"),
        "inherited-empty": run_one("inherited-empty", False, VERI_SKILL_COMMIT=""),
        "unknown": run_one("unknown", False),
    }

    assert answers == {
        "chosen": (0, launch("opus-x", sha), leaf("opus-x", sha), [[]], 0),
        "none": (0, launch("sonnet", sha), leaf("sonnet", sha), [[]], 0),
        "whitespace": (0, launch("", sha), leaf("", sha), [[]], 1),
        "dash-n": (0, launch("", sha), leaf("", sha), [[]], 0),
        "dash-e": (0, launch("", sha), leaf("", sha), [[]], 0),
        "dash-E": (0, launch("", sha), leaf("", sha), [[]], 0),
        "git-beats-inherited": (0, launch("sonnet", sha), leaf("sonnet", sha), [[]], 0),
        "inherited": (0, launch("sonnet", "inherited"), leaf("sonnet", "inherited"), [[]], 0),
        "inherited-empty": (0, launch("sonnet", "unknown"), leaf("sonnet", "unknown"), [[]], 0),
        "unknown": (0, launch("sonnet", "unknown"), leaf("sonnet", "unknown"), [[]], 0),
    }


def test_main_appends_one_usage_record_for_a_watched_leaf_with_its_role_and_skill_commit_a_log_with_no_closing_result_gets_harvests_diagnostic_on_stderr_before_the_status_line_and_a_verdict_name_none(
        monkeypatch, tmp_path, capfdbinary, supervise, events):
    import json
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: 5000.0)
    sha = "0123456789abcdef0123456789abcdef01234567"
    closing = json.dumps(
        {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 91234, "duration_api_ms": 40118,
         "num_turns": 7, "result": "done", "session_id": "4d1a", "total_cost_usd": 0.31,
         "usage": {"input_tokens": 37, "cache_creation_input_tokens": 41002, "cache_read_input_tokens": 903117,
                   "output_tokens": 5140}})

    def run_one(name, leaf_says):
        work = tmp_path / f"{name}-{len(leaf_says)}"
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="900")
        fake_leaf_launch(monkeypatch)
        code = supervise.main([name, "sh", "-c", f"printf '%s\\n' '{leaf_says}'"])
        out, err = capfdbinary.readouterr()
        lines = [line for line in err.splitlines()
                 if line.startswith((b"harvest-usage.sh:", b"supervise["))]
        usage = [{k: r.get(k) for k in ("actor", "phase", "attempt", "skill_commit", "num_turns")}
                 for r in events.records(work) if r["event"] == "usage"]
        return code, out, (work / ".tdd" / f"{name}.exit").read_bytes(), usage, lines

    assert run_one("develop-red", closing) == (
        0, closing.encode() + b"\n", b"0\n",
        [{"actor": "developer", "phase": "red", "attempt": "1", "skill_commit": sha, "num_turns": "7"}],
        [b"supervise[develop-red]: success"])
    assert run_one("develop-red", "no result here") == (
        0, b"no result here\n", b"0\n", [],
        [b"harvest-usage.sh: no closing result record in .tdd/develop-red.log \xe2\x80\x94 no usage event appended for develop-red",
         b"supervise[develop-red]: success"])
    assert run_one("verdict-red", closing) == (
        0, closing.encode() + b"\n", b"0\n", [], [b"supervise[verdict-red]: success"])


def test_main_gives_the_same_exit_stdout_stderr_and_usage_record_with_any_start_of_harvest_usage_sh_refused_at_the_process_boundary_for_a_log_with_a_closing_result_and_one_without(
        monkeypatch, tmp_path, capfdbinary, supervise, events):
    import json
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: 5000.0)
    sha = "0123456789abcdef0123456789abcdef01234567"
    closing = json.dumps(
        {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 91234, "duration_api_ms": 40118,
         "num_turns": 7, "result": "done", "session_id": "4d1a", "total_cost_usd": 0.31,
         "usage": {"input_tokens": 37, "cache_creation_input_tokens": 41002, "cache_read_input_tokens": 903117,
                   "output_tokens": 5140}})
    refused = []

    def refuse_harvest_start(monkeypatch_target, attr):
        inner = getattr(monkeypatch_target, attr)

        def guarded(args, *a, **k):
            if "harvest-usage.sh" in " ".join(map(str, args if isinstance(args, (list, tuple)) else [args])):
                refused.append(args)
                raise OSError("harvest-usage.sh start refused")
            return inner(args, *a, **k)

        monkeypatch.setattr(monkeypatch_target, attr, guarded)

    def run_one(name, leaf_says):
        work = tmp_path / f"{name}-{len(leaf_says)}"
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="900")
        fake_leaf_launch(monkeypatch)
        for attr in ("run", "Popen", "call", "check_call", "check_output"):
            refuse_harvest_start(subprocess, attr)
        code = supervise.main([name, "sh", "-c", f"printf '%s\\n' '{leaf_says}'"])
        out, err = capfdbinary.readouterr()
        lines = [line for line in err.splitlines()
                 if line.startswith((b"harvest-usage.sh:", b"supervise["))]
        usage = [{k: r.get(k) for k in ("actor", "phase", "attempt", "skill_commit", "num_turns")}
                 for r in events.records(work) if r["event"] == "usage"]
        return code, out, (work / ".tdd" / f"{name}.exit").read_bytes(), usage, lines

    assert run_one("develop-red", closing) == (
        0, closing.encode() + b"\n", b"0\n",
        [{"actor": "developer", "phase": "red", "attempt": "1", "skill_commit": sha, "num_turns": "7"}],
        [b"supervise[develop-red]: success"])
    assert run_one("develop-red", "no result here") == (
        0, b"no result here\n", b"0\n", [],
        [b"harvest-usage.sh: no closing result record in .tdd/develop-red.log \xe2\x80\x94 no usage event appended for develop-red",
         b"supervise[develop-red]: success"])
    assert refused == []


class StubLeaf:
    args = []

    def __init__(self, pid=4242, returncode=None, on_poll=None):
        self.pid = pid
        self.returncode = returncode
        self.on_poll = on_poll

    def poll(self):
        if self.on_poll:
            self.on_poll()
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode


class Runaway(BaseException):
    """Raised by the fake sleep when main keeps polling a leaf it should long since have killed."""


def test_main_with_veri_heartbeat_unset_kills_a_silent_leaf_at_181s_of_silence_not_180s_sending_term_to_its_group_and_its_default_is_the_one_the_header_and_skill_md_state(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import re
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.chdir(tmp_path)
    clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_STUCK_RETRIES="0")
    here = pathlib.Path(supervise.__file__).resolve().parents[1]
    header = (here / "supervise.sh").read_text()
    skill = (here.parents[0] / "SCRIPTS.md").read_text()
    stated = [re.search(r"VERI_HEARTBEAT silence window secs \(default ([0-9]+)", header),
              re.search(r"`VERI_HEARTBEAT` \(silence window s,\s+default ([0-9]+)", skill)]
    stated = [int(m.group(1)) if m else None for m in stated]

    clock = {"wall": 1000, "sleeps": 0}

    def sleep(_):
        clock["sleeps"] += 1
        if clock["sleeps"] > 2000:
            raise Runaway()
        clock["wall"] += 1

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

    leaf = StubLeaf()
    kills = []

    def killpg(pgid, sig):
        kills.append((clock["wall"], "group", pgid, sig))
        if pgid == leaf.pid:
            leaf.returncode = -sig

    def kill(pid, sig):
        if pid < 0:
            return killpg(-pid, sig)
        kills.append((clock["wall"], "pid", pid, sig))
        if pid == leaf.pid and sig:
            leaf.returncode = -sig

    monkeypatch.setattr(os, "killpg", killpg)
    monkeypatch.setattr(os, "kill", kill)

    def answer(args):
        args = [str(a) for a in args]
        if args[:1] == ["git"]:
            return 0, "0123456789abcdef0123456789abcdef01234567\n"
        if args[:1] == ["date"]:
            return 0, f"{clock['wall']}\n"
        if args[:3] == ["stat", "-c", "%Y"]:
            return 0, "1000\n"
        if args[:1] == ["stat"]:
            return 1, ""
        return 0, ""

    def run(args, *_, **kwargs):
        code, out = answer(args)
        out = as_asked(out, kwargs)
        if code and kwargs.get("check"):
            raise subprocess.CalledProcessError(code, args, out)
        return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

    def check_output(args, *_, **kwargs):
        code, out = answer(args)
        if code:
            raise subprocess.CalledProcessError(code, args)
        return as_asked(out, kwargs)

    launched = []

    def popen(args, *_, **kwargs):
        if list(args[:2]) == ["/bin/sh", "-c"]:
            launched.append(kwargs.get("process_group"))
            return leaf
        raise AssertionError(f"unexpected Popen: {args}")

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", check_output)
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
    monkeypatch.setattr(subprocess, "Popen", popen)

    try:
        code = supervise.main(["develop-red", "leaf-hang"])
    except Runaway:
        code = "<never ended>"
    _, err = capsysbinary.readouterr()
    exitfile = tmp_path / ".tdd" / "develop-red.exit"

    assert (stated, code, launched, kills[:1],
            [line for line in err.splitlines() if line.startswith(b"supervise[")][-1:],
            exitfile.read_bytes() if exitfile.exists() else None) == (
        [180, 180], 2, [0], [(1181, "group", 4242, signal.SIGTERM)],
        ["supervise[develop-red]: killed-stuck — no heartbeat for 181s (window 180s)".encode()],
        b"2\n")


def test_main_reads_the_wall_clock_through_date_and_a_logs_mtime_through_stat_c_then_stat_f_falling_back_to_date_and_takes_veri_heartbeat_as_bash_arithmetic(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def watch(name, heartbeat, stat, step, rc_after=None):
        work = tmp_path / f"w{len(list(tmp_path.iterdir()))}"
        work.mkdir()
        monkeypatch.chdir(work)
        env = {"VERI_TIMEOUT": "100000", "VERI_STUCK_RETRIES": "0"}
        if heartbeat is not None:
            env["VERI_HEARTBEAT"] = heartbeat
        clean_env(monkeypatch, **env)
        clock = {"wall": 1000, "sleeps": 0}
        calls, kills = [], []

        leaf = StubLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 2000:
                raise Runaway()
            clock["wall"] += step
            if clock["sleeps"] == rc_after:
                (work / ".tdd" / f"{name}.rc").write_text("0\n")
                leaf.returncode = 0

        monkeypatch.setattr(time, "sleep", sleep)
        monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

        def killpg(pgid, sig):
            kills.append((clock["wall"], "group", pgid, sig))
            if pgid == leaf.pid and sig:
                leaf.returncode = -sig

        def kill(pid, sig):
            if pid < 0:
                return killpg(-pid, sig)
            kills.append((clock["wall"], "pid", pid, sig))
            if pid == leaf.pid and sig:
                leaf.returncode = -sig

        monkeypatch.setattr(os, "killpg", killpg)
        monkeypatch.setattr(os, "kill", kill)

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["git"]:
                return 0, "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                calls.append(" ".join(args))
                return 0, f"{clock['wall']}\n"
            if args[:1] == ["stat"]:
                calls.append(" ".join(args))
                return stat(args[1], clock["wall"])
            return 0, ""

        def run(args, *_, **kwargs):
            code, out = answer(args)
            out = as_asked(out, kwargs)
            if code and kwargs.get("check"):
                raise subprocess.CalledProcessError(code, args, out)
            return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

        def check_output(args, *_, **kwargs):
            code, out = answer(args)
            if code:
                raise subprocess.CalledProcessError(code, args)
            return as_asked(out, kwargs)

        def popen(args, *_, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                return leaf
            raise AssertionError(f"unexpected Popen: {args}")

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", check_output)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)

        try:
            code = supervise.main([name, "leaf-hang"])
        except Runaway:
            code = "<never ended>"
        except Exception as e:
            code = f"<raised {type(e).__name__}>"
        _, err = capsysbinary.readouterr()
        exitfile = work / ".tdd" / f"{name}.exit"
        return {"code": code, "calls": calls, "kills": kills[:1], "sleeps": clock["sleeps"],
                "status": [l.decode() for l in err.splitlines() if l.startswith(b"supervise[")][-1:],
                "err": err.splitlines(),
                "exit": exitfile.read_bytes() if exitfile.exists() else None}

    log = ".tdd/develop-red.log"
    date, gnu, bsd = "date +%s", f"stat -c %Y {log}", f"stat -f %m {log}"
    fails = (1, "")
    term = signal.SIGTERM

    spelled = [
        watch("develop-red", None, lambda s, w: fails if s == "-c" else (0, "1000\n"), 1, rc_after=1)["calls"],
        watch("develop-red", None, lambda s, w: (0, "1000\n") if s == "-c" else fails, 1, rc_after=1)["calls"],
        watch("develop-red", None, lambda s, w: (0, "abc\n") if s == "-c" else (0, "1000\n"), 1, rc_after=1)["calls"],
        watch("develop-red", None, lambda s, w: fails, 1, rc_after=1)["calls"],
    ]
    assert spelled == [[date, gnu, bsd] * 2, [date, gnu] * 2, [date, gnu, date] * 2, [date, gnu, bsd, date] * 2]

    missing = watch("develop-red", "5", lambda s, w: fails, 10, rc_after=4)
    changed = watch("develop-red", "5", lambda s, w: (0, f"{min(w, 1020)}\n") if s == "-c" else fails, 1)
    verdict = watch("verdict-red", "5", lambda s, w: (0, "1000\n") if s == "-c" else fails, 10, rc_after=3)
    octal = watch("develop-red", "010", lambda s, w: (0, "1000\n") if s == "-c" else fails, 1)
    assert [(r["code"], r["kills"], r["status"]) for r in (missing, changed, verdict, octal)] + [
        [c for c in verdict["calls"] if c.startswith("stat")]] == [
        (0, [], ["supervise[develop-red]: success"]),
        (2, [(1026, "group", 4242, term)], ["supervise[develop-red]: killed-stuck — no heartbeat for 6s (window 5s)"]),
        (0, [], ["supervise[verdict-red]: success"]),
        (2, [(1011, "group", 4242, term)], ["supervise[develop-red]: killed-stuck — no heartbeat for 11s (window 010s)"]),
        []]

    broken = {value: watch("develop-red", value, lambda s, w: (0, "1000\n") if s == "-c" else fails, 100, rc_after=3)
              for value in ("1.5",)}
    assert {value: (r["code"], r["kills"], r["status"], len([l for l in r["err"] if value.encode() in l]))
            for value, r in broken.items()} == {
        "1.5": (2, [], [], 1)}

    word = watch("develop-red", "abc", lambda s, w: (0, "1000\n") if s == "-c" else fails, 100)
    assert (word["code"], word["sleeps"], word["kills"], word["exit"]) == (2, 0, [], None)


def test_main_reads_a_veri_heartbeat_with_leading_zeros_as_decimal_010_a_10s_window_and_08_an_8s_window_that_fires_1198(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def silent_leaf(heartbeat):
        work = tmp_path / heartbeat
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="100000", VERI_STUCK_RETRIES="0", VERI_HEARTBEAT=heartbeat)
        clock = {"wall": 1000, "sleeps": 0}
        kills = []

        leaf = StubLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 2000:
                raise Runaway()
            clock["wall"] += 1

        monkeypatch.setattr(time, "sleep", sleep)
        monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

        def killpg(pgid, sig):
            kills.append((clock["wall"] - 1000, sig))
            if pgid == leaf.pid and sig:
                leaf.returncode = -sig

        def kill(pid, sig):
            if pid < 0:
                return killpg(-pid, sig)
            if pid == leaf.pid and sig:
                kills.append((clock["wall"] - 1000, sig))
                leaf.returncode = -sig

        monkeypatch.setattr(os, "killpg", killpg)
        monkeypatch.setattr(os, "kill", kill)

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["git"]:
                return 0, "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return 0, f"{clock['wall']}\n"
            if args[:3] == ["stat", "-c", "%Y"]:
                return 0, "1000\n"
            if args[:1] == ["stat"]:
                return 1, ""
            return 0, ""

        def run(args, *_, **kwargs):
            code, out = answer(args)
            out = as_asked(out, kwargs)
            if code and kwargs.get("check"):
                raise subprocess.CalledProcessError(code, args, out)
            return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

        def check_output(args, *_, **kwargs):
            code, out = answer(args)
            if code:
                raise subprocess.CalledProcessError(code, args)
            return as_asked(out, kwargs)

        def popen(args, *_, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                return leaf
            raise AssertionError(f"unexpected Popen: {args}")

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", check_output)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)

        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Runaway:
            code = "<never ended>"
        capsysbinary.readouterr()
        return code, kills[:1]

    assert {value: silent_leaf(value) for value in ("010", "08")} == {
        "010": (2, [(11, signal.SIGTERM)]),
        "08": (2, [(9, signal.SIGTERM)])}


def test_main_fires_the_hard_timeout_on_the_awake_clock_slides_the_heartbeat_by_a_suspend_and_settles_the_timeout_from_veri_timeout_the_issue_file_or_900(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    uptime_raw = getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC)

    def watch(env, step, jump=None, rc_after=None, settled=None, uptime=True):
        work = tmp_path / f"w{len(list(tmp_path.iterdir()))}"
        (work / ".tdd").mkdir(parents=True)
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_STUCK_RETRIES="0", **env)
        if settled is not None:
            (work / ".tdd" / "issue-7-timeout").write_text(settled)
        if not uptime:
            monkeypatch.delattr(time, "CLOCK_UPTIME_RAW", raising=False)
        clock = {"wall": 1000, "awake": 5000, "sleeps": 0}
        clocks, awake_runs, kills = [], [], []

        leaf = StubLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 2000:
                raise Runaway()
            clock["wall"] += step + (jump if clock["sleeps"] == 3 and jump else 0)
            clock["awake"] += step
            if clock["sleeps"] == rc_after:
                (work / ".tdd" / "develop-red.rc").write_text("0\n")
                leaf.returncode = 0

        def clock_gettime(clk):
            clocks.append(clk)
            return clock["awake"] + 0.5

        monkeypatch.setattr(time, "sleep", sleep)
        monkeypatch.setattr(time, "clock_gettime", clock_gettime)

        def killpg(pgid, sig):
            kills.append((clock["wall"] - 1000, clock["awake"] - 5000, sig))
            if pgid == leaf.pid and sig:
                leaf.returncode = -sig

        def kill(pid, sig):
            if pid < 0:
                return killpg(-pid, sig)
            if pid == leaf.pid and sig:
                kills.append((clock["wall"] - 1000, clock["awake"] - 5000, sig))
                leaf.returncode = -sig

        monkeypatch.setattr(os, "killpg", killpg)
        monkeypatch.setattr(os, "kill", kill)

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["/fake/awake-clock"]:
                awake_runs.append(args)
                return 0, f"{clock['awake']}\n\n"
            if "--show-toplevel" in args:
                return 0, f"{work}\n"
            if args[:1] == ["git"]:
                return 0, "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return 0, f"{clock['wall']}\n"
            if args[:3] == ["stat", "-c", "%Y"]:
                return 0, "1000\n"
            if args[:1] == ["stat"]:
                return 1, ""
            return 0, ""

        def run(args, *_, **kwargs):
            code, out = answer(args)
            out = as_asked(out, kwargs)
            if code and kwargs.get("check"):
                raise subprocess.CalledProcessError(code, args, out)
            return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

        def check_output(args, *_, **kwargs):
            code, out = answer(args)
            if code:
                raise subprocess.CalledProcessError(code, args)
            return as_asked(out, kwargs)

        def popen(args, *_, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                return leaf
            raise AssertionError(f"unexpected Popen: {args}")

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", check_output)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)

        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Runaway:
            code = "<never ended>"
        except Exception as e:
            code = f"<raised {type(e).__name__}>"
        _, err = capsysbinary.readouterr()
        exitfile = work / ".tdd" / "develop-red.exit"
        return {"code": code, "kills": kills[:1], "sleeps": clock["sleeps"], "clocks": set(clocks),
                "awake_runs": len(awake_runs), "err": err.splitlines(),
                "status": [l.decode() for l in err.splitlines() if l.startswith(b"supervise[")][-1:],
                "exit": exitfile.read_bytes() if exitfile.exists() else None}

    quiet = {"VERI_HEARTBEAT": "100000"}
    term = signal.SIGTERM
    fired = [watch({**quiet, "VERI_TIMEOUT": "10"}, 1),
             watch({**quiet, "VERI_TIMEOUT": "10", "VERI_AWAKE_CLOCK": ""}, 1, uptime=False),
             watch({**quiet, "VERI_TIMEOUT": "10", "VERI_AWAKE_CLOCK": "/fake/awake-clock"}, 1),
             watch({**quiet, "VERI_TIMEOUT": "010"}, 1),
             watch({**quiet, "VERI_ISSUE": "7"}, 1, settled="010\n"),
             watch({**quiet, "VERI_ISSUE": "7"}, 100),
             watch({**quiet, "VERI_TIMEOUT": "11", "VERI_ISSUE": "7"}, 1, settled="3\n")]
    assert [(r["code"], r["kills"], r["status"], r["exit"]) for r in fired] == [
        (2, [(10, 10, term)], ["supervise[develop-red]: killed-stuck — hard timeout 10s exceeded"], b"2\n"),
        (2, [(10, 10, term)], ["supervise[develop-red]: killed-stuck — hard timeout 10s exceeded"], b"2\n"),
        (2, [(10, 10, term)], ["supervise[develop-red]: killed-stuck — hard timeout 10s exceeded"], b"2\n"),
        (2, [(10, 10, term)], ["supervise[develop-red]: killed-stuck — hard timeout 010s exceeded"], b"2\n"),
        (2, [(10, 10, term)], ["supervise[develop-red]: killed-stuck — hard timeout 010s exceeded"], b"2\n"),
        (2, [(900, 900, term)], ["supervise[develop-red]: killed-stuck — hard timeout 900s exceeded"], b"2\n"),
        (2, [(11, 11, term)], ["supervise[develop-red]: killed-stuck — hard timeout 11s exceeded"], b"2\n")]
    assert [(r["clocks"], r["awake_runs"] > 0) for r in fired[:3]] == [
        ({uptime_raw}, False), ({time.CLOCK_MONOTONIC}, False), (set(), True)]

    suspended = watch({"VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "100000"}, 1, jump=100)
    assert (suspended["code"], suspended["kills"], suspended["status"]) == (
        2, [(106, 6, term)], ["supervise[develop-red]: killed-stuck — no heartbeat for 6s (window 5s)"])

    broken = {value: watch({**quiet, "VERI_TIMEOUT": value}, 100, rc_after=3) for value in ("1.5",)}
    assert {value: (r["code"], r["kills"], r["status"], len([l for l in r["err"] if value.encode() in l]))
            for value, r in broken.items()} == {
        "1.5": (2, [], [], 1)}

    word = watch({**quiet, "VERI_TIMEOUT": "abc"}, 100)
    assert (word["code"], word["sleeps"], word["kills"], word["exit"]) == (2, 0, [], None)


def test_main_reads_a_veri_timeout_with_leading_zeros_as_decimal_010_a_10s_cap_and_08_an_8s_cap_that_fires_1198(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def capped_leaf(timeout):
        work = tmp_path / timeout
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_HEARTBEAT="100000", VERI_STUCK_RETRIES="0", VERI_TIMEOUT=timeout)
        clock = {"wall": 1000, "awake": 5000, "sleeps": 0}
        kills = []

        leaf = StubLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 2000:
                raise Runaway()
            clock["wall"] += 1
            clock["awake"] += 1

        monkeypatch.setattr(time, "sleep", sleep)
        monkeypatch.setattr(time, "clock_gettime", lambda *_: clock["awake"] + 0.5)

        def killpg(pgid, sig):
            kills.append((clock["awake"] - 5000, sig))
            if pgid == leaf.pid and sig:
                leaf.returncode = -sig

        def kill(pid, sig):
            if pid < 0:
                return killpg(-pid, sig)
            if pid == leaf.pid and sig:
                kills.append((clock["awake"] - 5000, sig))
                leaf.returncode = -sig

        monkeypatch.setattr(os, "killpg", killpg)
        monkeypatch.setattr(os, "kill", kill)

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["git"]:
                return 0, "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return 0, f"{clock['wall']}\n"
            if args[:3] == ["stat", "-c", "%Y"]:
                return 0, "1000\n"
            if args[:1] == ["stat"]:
                return 1, ""
            return 0, ""

        def run(args, *_, **kwargs):
            code, out = answer(args)
            out = as_asked(out, kwargs)
            if code and kwargs.get("check"):
                raise subprocess.CalledProcessError(code, args, out)
            return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

        def check_output(args, *_, **kwargs):
            code, out = answer(args)
            if code:
                raise subprocess.CalledProcessError(code, args)
            return as_asked(out, kwargs)

        def popen(args, *_, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                return leaf
            raise AssertionError(f"unexpected Popen: {args}")

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", check_output)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)

        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Runaway:
            code = "<never ended>"
        capsysbinary.readouterr()
        return code, kills[:1]

    assert {value: capped_leaf(value) for value in ("010", "08")} == {
        "010": (2, [(10, signal.SIGTERM)]),
        "08": (2, [(8, signal.SIGTERM)])}


def test_main_reads_a_settled_timeout_with_leading_zeros_as_decimal_010_a_10s_cap_1198(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1198-timeout").write_text("010\n")
    clean_env(monkeypatch, VERI_HEARTBEAT="100000", VERI_STUCK_RETRIES="0", VERI_ISSUE="1198")
    clock = {"wall": 1000, "awake": 5000, "sleeps": 0}
    kills = []

    leaf = StubLeaf()

    def sleep(_):
        clock["sleeps"] += 1
        if clock["sleeps"] > 2000:
            raise Runaway()
        clock["wall"] += 1
        clock["awake"] += 1

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: clock["awake"] + 0.5)

    def killpg(pgid, sig):
        kills.append((clock["awake"] - 5000, sig))
        if pgid == leaf.pid and sig:
            leaf.returncode = -sig

    def kill(pid, sig):
        if pid < 0:
            return killpg(-pid, sig)
        if pid == leaf.pid and sig:
            kills.append((clock["awake"] - 5000, sig))
            leaf.returncode = -sig

    monkeypatch.setattr(os, "killpg", killpg)
    monkeypatch.setattr(os, "kill", kill)

    def answer(args):
        args = [str(a) for a in args]
        if args[:3] == ["git", "rev-parse", "--show-toplevel"]:
            return 0, f"{tmp_path}\n"
        if args[:1] == ["git"]:
            return 0, "0123456789abcdef0123456789abcdef01234567\n"
        if args[:1] == ["date"]:
            return 0, f"{clock['wall']}\n"
        if args[:3] == ["stat", "-c", "%Y"]:
            return 0, "1000\n"
        if args[:1] == ["stat"]:
            return 1, ""
        return 0, ""

    def run(args, *_, **kwargs):
        code, out = answer(args)
        out = as_asked(out, kwargs)
        if code and kwargs.get("check"):
            raise subprocess.CalledProcessError(code, args, out)
        return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

    def check_output(args, *_, **kwargs):
        code, out = answer(args)
        if code:
            raise subprocess.CalledProcessError(code, args)
        return as_asked(out, kwargs)

    def popen(args, *_, **kwargs):
        if list(args[:2]) == ["/bin/sh", "-c"]:
            return leaf
        raise AssertionError(f"unexpected Popen: {args}")

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", check_output)
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
    monkeypatch.setattr(subprocess, "Popen", popen)

    try:
        code = supervise.main(["develop-red", "leaf-hang"])
    except Runaway:
        code = "<never ended>"
    capsysbinary.readouterr()

    assert (code, kills[:1]) == (2, [(10, signal.SIGTERM)])


def test_main_kills_the_leaf_by_term_to_its_group_else_its_pid_then_five_reaping_polls_of_veri_kill_poll_then_kill_and_its_rounds_sleep_veri_poll_an_invalid_one_polling_without_pause(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def kill_once(env, group_raises=False, dies_on_term=False):
        work = tmp_path / f"k{len(list(tmp_path.iterdir()))}"
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_STUCK_RETRIES="0", VERI_HEARTBEAT="3",
                  VERI_KILL_POLL="0.25", **env)
        clock = {"wall": 1000, "dates": 0}
        events = []

        leaf = StubLeaf(on_poll=lambda: events.append(("poll",)))

        def signalled(how, target, sig):
            events.append((how, target, sig))
            if how == "group" and group_raises:
                raise ProcessLookupError(3, "No such process")
            if sig == signal.SIGKILL or (sig == signal.SIGTERM and dies_on_term):
                leaf.returncode = -sig

        def killpg(pgid, sig):
            signalled("group", pgid, sig)

        def kill(pid, sig):
            if pid < 0:
                return signalled("group", -pid, sig)
            signalled("pid", pid, sig)

        monkeypatch.setattr(os, "killpg", killpg)
        monkeypatch.setattr(os, "kill", kill)
        monkeypatch.setattr(time, "sleep", lambda secs: events.append(("sleep", float(secs))))
        monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["git"]:
                return 0, "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                clock["dates"] += 1
                if clock["dates"] > 2000:
                    raise Runaway()
                clock["wall"] += 1
                return 0, f"{clock['wall']}\n"
            if args[:1] == ["stat"]:
                return 0, "1000\n"
            return 0, ""

        def run(args, *_, **kwargs):
            code, out = answer(args)
            out = as_asked(out, kwargs)
            return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

        def popen(args, *_, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                return leaf
            raise AssertionError(f"unexpected Popen: {args}")

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: as_asked(answer(args)[1], k))
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)

        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Runaway:
            code = "<never ended>"
        except Exception as error:
            code = repr(error)
        _, err = capsysbinary.readouterr()
        first = next((i for i, e in enumerate(events) if e[0] in ("group", "pid")), len(events))
        return {
            "code": code,
            "kill": events[first:],
            "round sleeps": sorted({e[1] for e in events[:first] if e[0] == "sleep"}),
            "rounds slept": sum(1 for e in events[:first] if e[0] == "sleep"),
            "invalid lines": sum(1 for line in err.splitlines() if b"abc" in line),
            "zero signals": [e for e in events if e[0] in ("group", "pid") and e[2] == 0],
        }

    grace = [("poll",), ("sleep", 0.25)] * 5
    term, kill = signal.SIGTERM, signal.SIGKILL
    stubborn = kill_once({})
    no_group = kill_once({}, group_raises=True)
    obliging = kill_once({"VERI_POLL": "0.5"}, dies_on_term=True)
    invalid = kill_once({"VERI_POLL": "abc"})

    assert [(r["code"], r["kill"], r["round sleeps"], r["zero signals"])
            for r in (stubborn, no_group, obliging)] == [
        (2, [("group", 4242, term), *grace, ("group", 4242, kill)], [1.0], []),
        (2, [("group", 4242, term), ("pid", 4242, term), *grace, ("group", 4242, kill), ("pid", 4242, kill)],
         [1.0], []),
        (2, [("group", 4242, term), ("poll",)], [0.5], []),
    ]
    assert stubborn["rounds slept"] > 0
    assert (invalid["code"], invalid["kill"], invalid["round sleeps"], invalid["invalid lines"]) == (
        2, [("group", 4242, term), *grace, ("group", 4242, kill)], [], stubborn["rounds slept"])


def test_main_ignores_a_kill_whose_group_and_pid_signals_both_raise_and_still_ends_killed_stuck_writing_2_to_its_exit_file(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.chdir(tmp_path)
    clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_STUCK_RETRIES="0", VERI_HEARTBEAT="3",
              VERI_KILL_POLL="0.25")
    clock = {"wall": 1000, "dates": 0}

    def gone(*_):
        raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "killpg", gone)
    monkeypatch.setattr(os, "kill", gone)
    monkeypatch.setattr(time, "sleep", lambda secs: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

    def answer(args):
        args = [str(a) for a in args]
        if args[:1] == ["git"]:
            return "0123456789abcdef0123456789abcdef01234567\n"
        if args[:1] == ["date"]:
            clock["dates"] += 1
            if clock["dates"] > 2000:
                raise Runaway()
            clock["wall"] += 1
            return f"{clock['wall']}\n"
        if args[:1] == ["stat"]:
            return "1000\n"
        return ""

    def run(args, *_, **kwargs):
        out = as_asked(answer(args), kwargs)
        return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

    def popen(args, *_, **kwargs):
        if list(args[:2]) == ["/bin/sh", "-c"]:
            return StubLeaf()
        raise AssertionError(f"unexpected Popen: {args}")

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: as_asked(answer(args), k))
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: 0)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: 0)
    monkeypatch.setattr(subprocess, "Popen", popen)

    try:
        code = supervise.main(["develop-red", "leaf-hang"])
    except Runaway:
        code = "<never ended>"
    except Exception as error:
        code = repr(error)
    _, err = capsysbinary.readouterr()
    exitfile = tmp_path / ".tdd" / "develop-red.exit"

    assert (code, exitfile.read_bytes() if exitfile.exists() else None, b"Traceback" in err) == (2, b"2\n", False)


def test_main_reports_a_killed_leaf_whose_log_ends_in_a_result_record_with_the_leafs_own_outcome_appending_its_result_text_and_otherwise_stays_killed_stuck(
        monkeypatch, tmp_path, capfdbinary, supervise):
    import re
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def killed(label, log_text, **env):
        work = tmp_path / label
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_HEARTBEAT="3", VERI_KILL_POLL="0.25", **env)
        clock = {"wall": 1000, "dates": 0}
        launched, ran = [], []

        leaf = StubLeaf()

        def signalled(*_):
            leaf.returncode = -signal.SIGTERM

        monkeypatch.setattr(os, "killpg", signalled)
        monkeypatch.setattr(os, "kill", signalled)
        monkeypatch.setattr(time, "sleep", lambda secs: None)
        monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

        def answer(args):
            args = [str(a) for a in args]
            ran.append(args)
            if args[:1] == ["git"]:
                return "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                clock["dates"] += 1
                if clock["dates"] > 2000:
                    raise Runaway()
                clock["wall"] += 1
                return f"{clock['wall']}\n"
            if args[:1] == ["stat"]:
                return "1000\n"
            return ""

        def run(args, *_, **kwargs):
            out = as_asked(answer(args), kwargs)
            return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

        def popen(args, *_, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                launched.append(list(args))
                pathlib.Path(args[4]).write_bytes(log_text)
                return leaf
            raise AssertionError(f"unexpected Popen: {args}")

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: as_asked(answer(args), k))
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)

        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Runaway:
            code = "<never ended>"
        except Exception as error:
            code = repr(error)
        out, err = capfdbinary.readouterr()
        log = work / ".tdd" / "develop-red.log"
        return {"code": code, "err": re.sub(r"Traceback \(most recent call last\):\n(?:  .*\n)+(\w+: .*\n)", r"harvest: \1",
                                           err.decode(errors="replace")),
                "appended": log.read_bytes()[len(log_text):] if log.exists() else None,
                "stdout is log": log.exists() and out == log.read_bytes(),
                "launches": len(launched),
                "preserved": [a for a in ran if "update-ref" in a]}

    cause = "no heartbeat for 4s (window 3s)"

    def recovered(outcome):
        return (f"supervise[develop-red]: killed after the leaf had already written its result ({cause})"
                f" — reporting the leaf's own {outcome}\nharvest-usage.sh: the closing result record in .tdd/develop-red.log carries no usage — no usage event appended for develop-red\nsupervise[develop-red]: {outcome}\n")

    stuck = ("harvest-usage.sh: no closing result record in .tdd/develop-red.log \u2014 no usage event appended"
             f" for develop-red\nsupervise[develop-red]: killed-stuck \u2014 {cause}\n")
    undecodable_stuck = ("harvest-usage.sh: .tdd/develop-red.log is not valid UTF-8 \u2014 no usage event appended"
                         f" for develop-red\nsupervise[develop-red]: killed-stuck \u2014 {cause}\n")
    may_retry_and_preserve = {"VERI_STUCK_RETRIES": "1", "VERI_ISSUE": "1073", "VERI_STEP": "24"}
    erred = killed("erred", b'chatter\n{"type":"result","is_error":true,"result":"boom"}\n',
                   **may_retry_and_preserve)
    done = killed("done", b'{"type":"result","is_error":true,"result":"early"}\n'
                          b'{"type":"result","is_error":0,"result":"VERDICT: PASS"}\n', **may_retry_and_preserve)
    no_record = killed("none", b'{"type":"assistant"}\nstill going\n', VERI_STUCK_RETRIES="0")
    undecodable = killed("undecodable", b'\xff\xfe\n{"type":"result","is_error":false,"result":"x"}\n',
                         VERI_STUCK_RETRIES="0")
    unextractable = killed("unextractable", b'{"type":"result","is_error":false,"result":5}\n',
                           **may_retry_and_preserve)

    assert [(r["code"], r["err"], r["appended"], r["stdout is log"], r["launches"], r["preserved"])
            for r in (erred, done, no_record, undecodable, unextractable)] == [
        (1, recovered("failure"), b"\nboom\n", True, 1, []),
        (0, recovered("success"), b"\nVERDICT: PASS\n", True, 1, []),
        (2, stuck, b"", True, 1, []),
        (2, undecodable_stuck, b"", True, 1, []),
        (0, recovered("success"), b"", True, 1, []),
    ]


def test_main_keeps_a_killed_leaf_whose_log_cannot_be_opened_killed_stuck_writing_2_to_its_exit_file_and_never_raising(
        monkeypatch, tmp_path, capfdbinary, supervise):
    import re
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.chdir(tmp_path)
    clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_STUCK_RETRIES="0", VERI_HEARTBEAT="3",
              VERI_KILL_POLL="0.25")
    clock = {"wall": 1000, "dates": 0}

    leaf = StubLeaf()

    def signalled(*_):
        leaf.returncode = -signal.SIGTERM

    monkeypatch.setattr(os, "killpg", signalled)
    monkeypatch.setattr(os, "kill", signalled)
    monkeypatch.setattr(time, "sleep", lambda secs: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

    def answer(args):
        args = [str(a) for a in args]
        if args[:1] == ["git"]:
            return "0123456789abcdef0123456789abcdef01234567\n"
        if args[:1] == ["date"]:
            clock["dates"] += 1
            if clock["dates"] > 2000:
                raise Runaway()
            clock["wall"] += 1
            return f"{clock['wall']}\n"
        if args[:1] == ["stat"]:
            return "1000\n"
        return ""

    def run(args, *_, **kwargs):
        out = as_asked(answer(args), kwargs)
        return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

    def popen(args, *_, **kwargs):
        if list(args[:2]) == ["/bin/sh", "-c"]:
            log = pathlib.Path(args[4])
            log.unlink()
            log.mkdir()
            return leaf
        raise AssertionError(f"unexpected Popen: {args}")

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: as_asked(answer(args), k))
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: 0)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: 0)
    monkeypatch.setattr(subprocess, "Popen", popen)

    try:
        code = supervise.main(["develop-red", "leaf-hang"])
    except Runaway:
        code = "<never ended>"
    except Exception as error:
        code = repr(error)
    _, err = capfdbinary.readouterr()
    exitfile = tmp_path / ".tdd" / "develop-red.exit"

    err = re.sub(r"Traceback \(most recent call last\):\n(?:  .*\n)+(\w+: .*\n)", r"harvest: \1", err.decode(errors="replace"))

    assert (code, exitfile.read_bytes() if exitfile.exists() else None, err) == (
        2, b"2\n",
        "supervise[develop-red]: [Errno 21] Is a directory: '.tdd/develop-red.log'\n"
        "harvest-usage.sh: .tdd/develop-red.log is a directory \u2014 no usage event appended for develop-red\n"
        "supervise[develop-red]: killed-stuck \u2014 no heartbeat for 4s (window 3s)\n"
        "supervise[develop-red]: [Errno 21] Is a directory: '.tdd/develop-red.log'\n")


def test_main_preserves_each_killed_attempt_when_issue_step_and_head_are_there_and_retries_a_killed_leaf_while_tries_are_below_veri_stuck_retries_read_as_bash_arithmetic(
        monkeypatch, tmp_path, capsysbinary, supervise, events):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    preserver = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(supervise.__file__))),
                             "preserve-attempt.sh")

    def stuck(label, ends_at=None, preserve_rc=0, head_ok=True, **env):
        work = tmp_path / label
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_HEARTBEAT="3", VERI_KILL_POLL="0.25", **env)
        clock = {"wall": 1000, "dates": 0}
        leaves, preserved = [], []

        def signalled(*_):
            leaves[-1].returncode = -signal.SIGTERM

        monkeypatch.setattr(os, "killpg", signalled)
        monkeypatch.setattr(os, "kill", signalled)
        monkeypatch.setattr(time, "sleep", lambda secs: None)
        monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

        def run(args, *_, **kwargs):
            words = [str(a) for a in args]
            code, out = 0, ""
            if words[:1] == ["git"]:
                if words[1:] == ["rev-parse", "--verify", "-q", "HEAD"]:
                    code = 0 if head_ok else 1
                out = "0123456789abcdef0123456789abcdef01234567\n" if code == 0 else ""
                if "--show-toplevel" in words:
                    out = os.getcwd() + "\n"
                elif "commit-tree" in words:
                    out = "c" * 40 + "\n"
                elif "update-ref" in words:
                    preserved.append(words[2:])
                    code, out = preserve_rc, ""
            elif words[:1] == ["date"]:
                clock["dates"] += 1
                if clock["dates"] > 2000:
                    raise Runaway()
                clock["wall"] += 1
                out = f"{clock['wall']}\n"
            elif words[:1] == ["stat"]:
                out = "1000\n"
            elif words and words[0] == preserver:
                raise AssertionError(f"preserve-attempt.sh started as a process: {words}")
            out = as_asked(out, kwargs) if kwargs.get("stdout") == subprocess.PIPE else None
            return subprocess.CompletedProcess(args, code, out, None)

        def popen(args, *_, **kwargs):
            if list(args[:2]) != ["/bin/sh", "-c"]:
                raise AssertionError(f"unexpected Popen: {args}")
            leaf = StubLeaf()
            leaves.append(leaf)
            if len(leaves) == ends_at:
                pathlib.Path(args[5]).write_text("0\n")
                leaf.returncode = 0
            return leaf

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: run(args, **k).stdout)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)
        events.refuse_event_sh()

        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Runaway:
            code = "<never ended>"
        except Exception as error:
            code = repr(error)
        out, err = capsysbinary.readouterr()
        return {"code": code, "launches": len(leaves), "preserved": preserved,
                "retries": [r for r in events.records(work) if r["event"] == "retry"],
                "refused": [r for r in events.records(work) if r["event"] == "launch-refused"],
                "out": out, "err": err.decode(errors="replace")}

    def kept(*attempts):
        return [[f"refs/veri/attempts/1073/27/develop-red-{a}", "c" * 40] for a in attempts]

    retry = {"issue": "1073", "actor": "developer", "phase": "red", "step": "27", "event": "retry", "attempt": "1",
             "skill_commit": "0123456789abcdef0123456789abcdef01234567", "cause": "no heartbeat for 4s (window 3s)"}
    issue_step = {"VERI_ISSUE": "1073", "VERI_STEP": "27"}

    default = stuck("default", **issue_step)
    assert (default["code"], default["launches"], default["preserved"], default["retries"], default["out"]) == (
        2, 2, kept(1, 2), [retry], b"")
    assert "supervise[develop-red]: retry 1/1 after killed-stuck\n" in default["err"]

    failing = stuck("failing", preserve_rc=1, VERI_STUCK_RETRIES="0", **issue_step)
    assert (failing["code"], failing["preserved"]) == (2, kept(1))
    assert ("supervise[develop-red]: could not preserve the stuck attempt"
            " (issue 1073 step 27 develop-red attempt 1)\n") in failing["err"]

    empty_step = stuck("no-step", VERI_STUCK_RETRIES="0", VERI_ISSUE="1073", VERI_STEP="")
    assert (empty_step["code"], empty_step["launches"], empty_step["preserved"], empty_step["out"]) == (2, 0, [], b"")
    assert len(empty_step["err"].splitlines()) == 1 and "VERI_STEP" in empty_step["err"], empty_step["err"]
    assert [(r["name"], bool(r["reason"])) for r in empty_step["refused"]] == [("develop-red", True)], empty_step["refused"]

    unpreserved = [stuck("no-issue", VERI_STUCK_RETRIES="0", VERI_ISSUE="", VERI_STEP="27"),
                   stuck("no-head", head_ok=False, VERI_STUCK_RETRIES="0", **issue_step)]
    assert [(r["code"], r["launches"], r["preserved"]) for r in unpreserved] == [(2, 1, [])] * 2

    budgets = {retries: stuck(f"budget{retries}", VERI_STUCK_RETRIES=retries, **issue_step)
               for retries in ("0", "-1", "010", "abc")}
    budgets["08"] = stuck("budget08", ends_at=4, VERI_STUCK_RETRIES="08", **issue_step)
    assert {k: (r["code"], r["launches"], r["preserved"], len(r["retries"])) for k, r in budgets.items()} == {
        "0": (2, 1, kept(1), 0),
        "-1": (2, 0, [], 0),
        "010": (2, 11, kept(*range(1, 12)), 10),
        "abc": (2, 0, [], 0),
        "08": (0, 4, kept(1, 2, 3), 3),
    }


def test_main_reads_veri_stuck_retries_with_leading_zeros_as_decimal_08_eight_retries_then_killed_stuck_1198(
        monkeypatch, tmp_path, capsysbinary, supervise, events):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.chdir(tmp_path)
    clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_HEARTBEAT="3", VERI_KILL_POLL="0.25",
              VERI_STUCK_RETRIES="08")
    clock = {"wall": 1000, "dates": 0}
    leaves = []

    def signalled(*_):
        leaves[-1].returncode = -signal.SIGTERM

    monkeypatch.setattr(os, "killpg", signalled)
    monkeypatch.setattr(os, "kill", signalled)
    monkeypatch.setattr(time, "sleep", lambda secs: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

    def run(args, *_, **kwargs):
        words = [str(a) for a in args]
        out = ""
        if words[:1] == ["git"]:
            out = "0123456789abcdef0123456789abcdef01234567\n"
        elif words[:1] == ["date"]:
            clock["dates"] += 1
            if clock["dates"] > 2000:
                raise Runaway()
            clock["wall"] += 1
            out = f"{clock['wall']}\n"
        elif words[:1] == ["stat"]:
            out = "1000\n"
        out = as_asked(out, kwargs) if kwargs.get("stdout") == subprocess.PIPE else None
        return subprocess.CompletedProcess(args, 0, out, None)

    def popen(args, *_, **kwargs):
        if list(args[:2]) != ["/bin/sh", "-c"]:
            raise AssertionError(f"unexpected Popen: {args}")
        leaves.append(StubLeaf())
        return leaves[-1]

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: run(args, **k).stdout)
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, **k).returncode)
    monkeypatch.setattr(subprocess, "Popen", popen)
    events.refuse_event_sh()

    try:
        code = supervise.main(["develop-red", "leaf-hang"])
    except Runaway:
        code = "<never ended>"
    capsysbinary.readouterr()

    assert (code, len(leaves), len([r for r in events.records() if r["event"] == "retry"])) == (2, 9, 8)


def test_main_refuses_a_veri_heartbeat_not_a_non_negative_decimal_integer_with_exit_2_naming_it_starting_nothing_but_git_1198(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    answers = {}
    for n, value in enumerate(("abc", "1.5", "-1")):
        work = tmp_path / f"heartbeat-{n}"
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_HEARTBEAT=value)
        calls = fake_git_only(monkeypatch, work)
        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Launched:
            code = "<launched>"
        out, err = capsysbinary.readouterr()
        answers[value] = (code, out, err, all(c[0] == "git" for c in calls))

    assert answers == {
        value: (2, b"", f"supervise: VERI_HEARTBEAT is not a number: '{value}'\n".encode(), True)
        for value in ("abc", "1.5", "-1")
    }


def test_main_refuses_a_veri_timeout_not_a_non_negative_decimal_integer_with_exit_2_naming_it_starting_nothing_but_git_1198(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    answers = {}
    for n, value in enumerate(("abc", "1.5", "-1")):
        work = tmp_path / f"timeout-{n}"
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT=value)
        calls = fake_git_only(monkeypatch, work)
        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Launched:
            code = "<launched>"
        out, err = capsysbinary.readouterr()
        answers[value] = (code, out, err, all(c[0] == "git" for c in calls))

    assert answers == {
        value: (2, b"", f"supervise: VERI_TIMEOUT is not a number: '{value}'\n".encode(), True)
        for value in ("abc", "1.5", "-1")
    }


def test_main_refuses_a_settled_timeout_not_a_non_negative_decimal_integer_with_exit_2_naming_its_path_starting_nothing_but_git_1198(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    answers = {}
    for n, value in enumerate(("abc", "1.5")):
        work = tmp_path / f"settled-{n}"
        (work / ".tdd").mkdir(parents=True)
        (work / ".tdd" / "issue-1198-timeout").write_text(f"{value}\n")
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_ISSUE="1198")
        calls = fake_git_only(monkeypatch, work)
        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Launched:
            code = "<launched>"
        out, err = capsysbinary.readouterr()
        answers[value] = (code, out, err, all(c[0] == "git" for c in calls))

    assert answers == {
        value: (2, b"",
                f"supervise: {tmp_path}/settled-{n}/.tdd/issue-1198-timeout is not a number: '{value}'\n".encode(),
                True)
        for n, value in enumerate(("abc", "1.5"))
    }


def test_main_refuses_a_veri_stuck_retries_not_a_non_negative_decimal_integer_with_exit_2_naming_it_starting_nothing_but_git_1198(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    answers = {}
    for n, value in enumerate(("abc", "1.5", "-1")):
        work = tmp_path / f"retries-{n}"
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_STUCK_RETRIES=value)
        calls = fake_git_only(monkeypatch, work)
        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except Launched:
            code = "<launched>"
        out, err = capsysbinary.readouterr()
        answers[value] = (code, out, err, all(c[0] == "git" for c in calls))

    assert answers == {
        value: (2, b"", f"supervise: VERI_STUCK_RETRIES is not a number: '{value}'\n".encode(), True)
        for value in ("abc", "1.5", "-1")
    }


def test_main_refuses_a_launch_while_the_leaf_recorded_in_leaf_owner_is_alive_and_records_itself_there_only_for_a_watched_name_not_a_conductor(
        monkeypatch, tmp_path, capsysbinary, supervise, events):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    me = os.getpid()

    def supervised(label, name, owner=None, owner_exit=None, dead=()):
        work = tmp_path / label
        tdd = work / ".tdd"
        tdd.mkdir(parents=True)
        if owner is not None:
            (tdd / "leaf.owner").write_text(owner)
        if owner_exit is not None:
            (tdd / f"{owner_exit}.exit").write_text("0\n")
        monkeypatch.chdir(work)
        calls = fake_git_only(monkeypatch, work)
        events.refuse_event_sh()
        probed = []

        def kill(pid, sig):
            probed.append((pid, sig))
            if pid in dead:
                raise ProcessLookupError(pid)

        monkeypatch.setattr(os, "kill", kill)
        try:
            code = supervise.main([name, "true"])
        except Launched as launched:
            code = ("launched", launched.args[0][0])
        out, err = capsysbinary.readouterr()

        def read(path):
            path = tdd / path
            return path.read_text() if path.exists() else None

        return (code, out, err.decode().splitlines()[-1:], read(f"{name}.exit"), read(f"{name}.pid"),
                read("leaf.owner"), probed,
                ["git", "-C", supervise.HERE, "rev-parse", "HEAD"] in calls,
                [(r["event"], r["actor"], r["name"]) for r in events.records(work)])

    answers = {
        "alive": supervised("alive", "verify-red", "4242 develop-red\nignored line\n"),
        "alive-same-name": supervised("alive-same-name", "develop-red", "4242 develop-red\n"),
        "alive-no-owner-name": supervised("alive-no-owner-name", "verify-red", "4242\n"),
        "alive-refused-role": supervised("alive-refused-role", "bogus-x", "4242 develop-red\n"),
        "alive-zero": supervised("alive-zero", "verify-red", "0 develop-red\n"),
        "alive-negative": supervised("alive-negative", "verify-red", "-7 develop-red\n"),
        "owner-exit": supervised("owner-exit", "verify-red", "4242 develop-red\n", owner_exit="develop-red"),
        "empty-pid": supervised("empty-pid", "verify-red", "\n"),
        "word-pid": supervised("word-pid", "verify-red", "abc develop-red\n"),
        "dead": supervised("dead", "verify-red", "4242 develop-red\n", dead=(4242,)),
        "none-watched": supervised("none-watched", "develop-red"),
        "none-verdict": supervised("none-verdict", "verdict-red"),
        "none-conductor": supervised("none-conductor", "conductor-1"),
        "alive-verdict": supervised("alive-verdict", "verdict-red", "4242 develop-red\n"),
    }

    launched, mine, verifier = ("launched", "date"), f"{me}\n", [("launch", "verifier", "verify-red")]
    assert answers == {
        "alive": (2, b"", [REFUSAL.format("verify-red", "develop-red", 4242)], "2\n", None,
                  "4242 develop-red\nignored line\n", [(4242, 0)], True, []),
        "alive-same-name": (2, b"", [REFUSAL.format("develop-red", "develop-red", 4242)], None, None,
                            "4242 develop-red\n", [(4242, 0)], True, []),
        "alive-no-owner-name": (2, b"", [REFUSAL.format("verify-red", "?", 4242)], "2\n", None,
                                "4242\n", [(4242, 0)], True, []),
        "alive-refused-role": (2, b"", [REFUSAL.format("bogus-x", "develop-red", 4242)], "2\n", None,
                               "4242 develop-red\n", [(4242, 0)], True, []),
        "alive-zero": (launched, b"", [], None, mine, f"{me} verify-red\n", [], True, verifier),
        "alive-negative": (launched, b"", [], None, mine, f"{me} verify-red\n", [], True, verifier),
        "owner-exit": (launched, b"", [], None, mine, f"{me} verify-red\n", [], True, verifier),
        "empty-pid": (launched, b"", [], None, mine, f"{me} verify-red\n", [], True, verifier),
        "word-pid": (launched, b"", [], None, mine, f"{me} verify-red\n", [], True, verifier),
        "dead": (launched, b"", [], None, mine, f"{me} verify-red\n", [(4242, 0)], True, verifier),
        "none-watched": (launched, b"", [], None, mine, f"{me} develop-red\n", [], True,
                         [("launch", "developer", "develop-red")]),
        "none-verdict": (launched, b"", [], None, mine, None, [], True, []),
        "none-conductor": (launched, b"", [], None, mine, None, [], True, [("launch", "conductor", "conductor-1")]),
        "alive-verdict": (2, b"", [REFUSAL.format("verdict-red", "develop-red", 4242)], "2\n", None,
                          "4242 develop-red\n", [(4242, 0)], True, []),
    }


def test_main_treats_a_leaf_owner_pid_below_1_as_stale_and_launches_1200(
        monkeypatch, tmp_path, capsysbinary, supervise, events):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    me = os.getpid()
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)

    def supervised(owner_pid):
        work = tmp_path / owner_pid
        tdd = work / ".tdd"
        tdd.mkdir(parents=True)
        (tdd / "leaf.owner").write_text(f"{owner_pid} develop-red\n")
        monkeypatch.chdir(work)
        fake_git_only(monkeypatch, work)
        events.refuse_event_sh()
        try:
            code = supervise.main(["verify-red", "true"])
        except Launched as launched:
            code = ("launched", launched.args[0][0])
        _, err = capsysbinary.readouterr()
        exitfile = tdd / "verify-red.exit"
        return (code, err, exitfile.exists(), (tdd / "leaf.owner").read_text(),
                [(r["event"], r["actor"], r["name"]) for r in events.records(work)])

    assert {pid: supervised(pid) for pid in ("0", "-7")} == {
        pid: (("launched", "date"), b"", False, f"{me} verify-red\n", [("launch", "verifier", "verify-red")])
        for pid in ("0", "-7")
    }


class NoHandler(BaseException):
    """Raised by the fake signal delivery when main installed no handler for the signal sent."""


def test_main_restores_sigint_then_traps_term_int_and_hup_after_the_stale_exit_goes_unless_ignored_at_start_and_the_trap_kills_the_last_leaf_writes_2_and_exits_2_silently(
        monkeypatch, tmp_path, capsysbinary, supervise, events):
    import re
    import signal
    import time
    term, sigint, hup = signal.SIGTERM, signal.SIGINT, signal.SIGHUP

    def supervised(label, start, sent, deliver_at):
        work = tmp_path / label
        tdd = work / ".tdd"
        tdd.mkdir(parents=True)
        exitfile = tdd / "develop-red.exit"
        exitfile.write_text("1\n")
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="5000", VERI_STUCK_RETRIES="1", VERI_HEARTBEAT="3",
                  VERI_KILL_POLL="0.25")
        dispositions = dict(start)
        installs = []

        def install(sig, handler):
            installs.append((sig, handler, exitfile.exists()))
            previous, dispositions[sig] = dispositions.get(sig, signal.SIG_DFL), handler
            return previous

        monkeypatch.setattr(signal, "signal", install)
        monkeypatch.setattr(signal, "getsignal", lambda sig: dispositions.get(sig, signal.SIG_DFL))

        def exit_now(code):
            raise SystemExit(code)

        monkeypatch.setattr(os, "_exit", exit_now)
        clock = {"wall": 1000, "dates": 0}
        signals = []
        leaves = []

        def signalled(how, target, sig):
            signals.append((how, target, sig))
            for leaf in leaves:
                if leaf.pid == target and sig in (term, signal.SIGKILL):
                    leaf.returncode = -sig

        monkeypatch.setattr(os, "killpg", lambda pgid, sig: signalled("group", pgid, sig))
        monkeypatch.setattr(os, "kill", lambda pid, sig: signalled("group", -pid, sig) if pid < 0
                            else signalled("pid", pid, sig))

        def deliver():
            handler = dispositions.get(sent, signal.SIG_DFL)
            signals.append(("delivered", sent))
            if not callable(handler) or handler is signal.default_int_handler:
                raise NoHandler(sent)
            handler(sent, None)

        def sleep(_):
            if deliver_at == "second leaf" and len(leaves) == 2:
                deliver()

        monkeypatch.setattr(time, "sleep", sleep)
        monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["wall"] + 4000))

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["git"]:
                return "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                if deliver_at == "first date":
                    deliver()
                clock["dates"] += 1
                if clock["dates"] > 2000:
                    raise Runaway()
                clock["wall"] += 1
                return f"{clock['wall']}\n"
            if args[:1] == ["stat"]:
                return "1000\n"
            return ""

        def run(args, *_, **kwargs):
            out = as_asked(answer(args), kwargs)
            return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

        def popen(args, *_, **kwargs):
            if list(args[:2]) != ["/bin/sh", "-c"]:
                raise AssertionError(f"unexpected Popen: {args}")
            leaf = StubLeaf(4242 + len(leaves))
            leaves.append(leaf)
            if len(leaves) == 2:
                exitfile.write_text("0\n")
            return leaf

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: as_asked(answer(args), k))
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: 0)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: 0)
        monkeypatch.setattr(subprocess, "Popen", popen)
        events.refuse_event_sh()

        try:
            code = supervise.main(["develop-red", "leaf-hang"])
        except SystemExit as exited:
            code = ("exited", exited.code)
        except NoHandler as missing:
            code = ("no handler", missing.args[0])
        except Runaway:
            code = "<never ended>"
        out, err = capsysbinary.readouterr()
        delivered = next((i for i, e in enumerate(signals) if e[0] == "delivered"), len(signals))
        trapped = [(sig, present) for sig, handler, present in installs
                   if callable(handler) and handler is not signal.default_int_handler]
        return {
            "code": code,
            "first install": installs[0][::2] if installs else None,
            "defaults set": [(sig, present) for sig, handler, present in installs if handler is signal.SIG_DFL],
            "trapped": sorted(trapped),
            "one handler": len({handler for _, handler, _ in installs if callable(handler)}) <= 1,
            "kills after delivery": signals[delivered + 1:],
            "exit file": exitfile.read_text() if exitfile.exists() else None,
            "stdout": out,
            "status lines": [line for line in err.splitlines()
                             if re.match(rb"supervise\[develop-red\]: (success|failure|killed-stuck)", line)],
            "events": [r["event"] for r in events.records(work)],
            "harvest diagnostics": [line for line in err.splitlines() if line.startswith(b"harvest-usage.sh:")],
        }

    default = {sigint: signal.default_int_handler, term: signal.SIG_DFL, hup: signal.SIG_DFL}
    ignoring = {sigint: signal.SIG_IGN, term: signal.SIG_DFL, hup: signal.SIG_IGN}
    answers = {
        "term mid second leaf": supervised("term", default, term, "second leaf"),
        "hup before any leaf": supervised("hup", default, hup, "first date"),
        "int mid second leaf": supervised("int", default, sigint, "second leaf"),
        "term with int and hup ignored": supervised("ignored", ignoring, term, "first date"),
    }

    silent = {"stdout": b"", "status lines": [], "harvest diagnostics": []}
    trapped_all = [(hup, False), (sigint, False), (term, False)]
    assert answers == {
        "term mid second leaf": {
            "code": ("exited", 2), "first install": (sigint, True),
            "defaults set": [(sigint, True)], "trapped": trapped_all, "one handler": True,
            "kills after delivery": [("group", 4243, term)], "exit file": "2\n", "events": ["launch", "retry"],
            **silent},
        "hup before any leaf": {
            "code": ("exited", 2), "first install": (sigint, True),
            "defaults set": [(sigint, True)], "trapped": trapped_all, "one handler": True,
            "kills after delivery": [], "exit file": "2\n", "events": ["launch"], **silent},
        "int mid second leaf": {
            "code": ("exited", 2), "first install": (sigint, True),
            "defaults set": [(sigint, True)], "trapped": trapped_all, "one handler": True,
            "kills after delivery": [("group", 4243, term)], "exit file": "2\n", "events": ["launch", "retry"],
            **silent},
        "term with int and hup ignored": {
            "code": ("exited", 2), "first install": (term, False),
            "defaults set": [], "trapped": [(term, False)], "one handler": True,
            "kills after delivery": [], "exit file": "2\n", "events": ["launch"], **silent},
    }


def test_main_hands_the_leaf_its_dispositions_through_a_preexec_survives_a_closed_stdout_and_names_each_failing_tdd_write_then_goes_on_to_its_exit(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import errno
    import pathlib
    import re
    import signal
    import time
    term, sigint, hup, pipe, xfsz = signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGPIPE, signal.SIGXFSZ
    monkeypatch.setattr(time, "sleep", lambda *_: None)

    def supervised(label, name, start, prepare=lambda work: None, stdout=None):
        work = tmp_path / label
        tdd = work / ".tdd"
        tdd.mkdir(parents=True)
        prepare(work)
        monkeypatch.chdir(work)
        clean_env(monkeypatch)
        dispositions = dict(start)

        def install(sig, handler):
            previous, dispositions[sig] = dispositions.get(sig, signal.SIG_DFL), handler
            return previous

        monkeypatch.setattr(signal, "signal", install)
        monkeypatch.setattr(signal, "getsignal", lambda sig: dispositions.get(sig, signal.SIG_DFL))
        handed = []

        def popen(args, *_, **kwargs):
            if list(args[:2]) != ["/bin/sh", "-c"]:
                raise AssertionError(f"unexpected Popen: {args}")
            parent = dict(dispositions)
            preexec = kwargs.get("preexec_fn")
            if preexec is None:
                child = "no preexec"
            else:
                preexec()
                child = {sig: dispositions.get(sig) for sig in (pipe, xfsz, term, sigint, hup)}
            dispositions.clear()
            dispositions.update(parent)
            handed.append((kwargs.get("restore_signals", "absent"), kwargs.get("process_group"), child))
            rc = pathlib.Path(f".tdd/{name}.rc")
            if rc.is_dir():
                rc.rmdir()
            rc.write_text("0\n")
            log = pathlib.Path(f".tdd/{name}.log")
            if log.is_file():
                log.write_bytes(b"leaf out\n")
            return StubLeaf(4242, returncode=0)

        def run(args, *_, **kwargs):
            args = [str(a) for a in args]
            out = "0123456789abcdef0123456789abcdef01234567\n" if args[:1] == ["git"] else (
                "1000\n" if args[:1] in (["date"], ["stat"]) else "")
            out = as_asked(out, kwargs)
            return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: run(args, *a, **k).stdout)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: 0)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: 0)
        monkeypatch.setattr(subprocess, "Popen", popen)
        if stdout is not None:
            monkeypatch.setattr(sys, "stdout", stdout)
        try:
            code = supervise.main([name, "leaf"])
        except Exception as error:
            code = ("raised", type(error).__name__)
        finally:
            monkeypatch.undo()
            monkeypatch.setattr(time, "sleep", lambda *_: None)
        _, err = capsysbinary.readouterr()
        exitfile = tdd / f"{name}.exit"
        return code, err, exitfile.read_text() if exitfile.is_file() else None, handed

    started = {sigint: signal.default_int_handler, term: signal.SIG_DFL, hup: signal.SIG_DFL,
               pipe: signal.SIG_IGN, xfsz: signal.SIG_IGN}
    detached = {**started, sigint: signal.SIG_IGN, hup: signal.SIG_IGN}

    class Closed:
        """A stdout whose reader has gone: every write and flush is a broken pipe."""

        def write(self, *_):
            raise BrokenPipeError(errno.EPIPE, "Broken pipe")

        flush = write

        @property
        def buffer(self):
            return self

    probe = tmp_path / "probe"
    probe.mkdir()
    try:
        open(probe, "w")
    except OSError as error:
        not_writable = error.strerror
    try:
        os.remove(probe)
    except OSError as error:
        not_removable = error.strerror

    def unmakeable(work):
        for path in ("develop-red.log", "develop-red.rc", "develop-red.pid", "leaf.owner"):
            (work / ".tdd" / path).mkdir()

        def refuse_tdd(path, *_, **__):
            if os.path.basename(os.fspath(path)) == ".tdd":
                raise PermissionError(errno.EACCES, "Permission denied", os.fspath(path))
            return None

        monkeypatch.setattr(os, "makedirs", refuse_tdd)
        monkeypatch.setattr(os, "mkdir", refuse_tdd)
        monkeypatch.setattr(pathlib.Path, "mkdir", lambda self, *a, **k: refuse_tdd(self))

    preexec_plain = supervised("plain", "verdict-red", started)
    preexec_detached = supervised("detached", "verdict-red", detached)
    closed = supervised("closed", "verdict-red", started, stdout=Closed())
    failing = supervised("failing", "develop-red", started, prepare=unmakeable)

    def named(path, strerror):
        pattern = rb"supervise\[develop-red\]: could not \S.* " + re.escape(path.encode()) + b": " + \
            re.escape(strerror.encode())
        return any(re.fullmatch(pattern, line) for line in failing[1].splitlines())

    answers = {
        "plain": (preexec_plain[0], preexec_plain[2], preexec_plain[3]),
        "detached": (preexec_detached[0], preexec_detached[2], preexec_detached[3]),
        "closed stdout": closed[:3],
        "failing writes": (failing[0], failing[2], {
            ".tdd": named(".tdd", "Permission denied"),
            ".tdd/develop-red.log": named(".tdd/develop-red.log", not_writable),
            ".tdd/develop-red.rc": named(".tdd/develop-red.rc", not_removable),
            ".tdd/develop-red.pid": named(".tdd/develop-red.pid", not_writable),
            ".tdd/leaf.owner": named(".tdd/leaf.owner", not_writable),
        }),
    }

    assert answers == {
        "plain": (0, "0\n", [(False, 0, {pipe: signal.SIG_DFL, xfsz: signal.SIG_IGN, term: signal.SIG_DFL,
                                          sigint: signal.SIG_DFL, hup: signal.SIG_DFL})]),
        "detached": (0, "0\n", [(False, 0, {pipe: signal.SIG_DFL, xfsz: signal.SIG_IGN, term: signal.SIG_DFL,
                                             sigint: signal.SIG_IGN, hup: signal.SIG_IGN})]),
        "closed stdout": (0, b"supervise[verdict-red]: success\n", "0\n"),
        "failing writes": (0, "0\n", {".tdd": True, ".tdd/develop-red.log": True, ".tdd/develop-red.rc": True,
                                      ".tdd/develop-red.pid": True, ".tdd/leaf.owner": True}),
    }


def fake_clocked_leaf(monkeypatch, work, name, silent, ends_at, launches=None, lag=0):
    clock = {"wall": 1000, "awake": 5000}

    def sleep(_):
        clock["wall"] += 1
        clock["awake"] += 1
        if clock["wall"] > 5000:
            raise AssertionError("never ended")
        if clock["wall"] >= ends_at:
            (work / ".tdd" / f"{name}.rc").write_text("0\n")

    def ended():
        if leaf.returncode is None and clock["wall"] >= ends_at:
            leaf.returncode = 0

    leaf = StubLeaf(on_poll=ended)

    def stop(_pid, sig):
        if sig:
            leaf.returncode = -sig

    def answer(args):
        args = [str(a) for a in args]
        if args[:1] == ["git"]:
            return "0123456789abcdef0123456789abcdef01234567\n"
        if args[:1] == ["date"]:
            return f"{clock['wall']}\n"
        if args[:1] == ["stat"]:
            return "1000\n" if silent else f"{clock['wall'] - (lag if clock['wall'] > 1002 else 0)}\n"
        return ""

    def popen(args, *_, **k):
        if launches is not None:
            launches.append(name)
        return leaf

    install_awake_fakes(monkeypatch, clock, leaf, sleep, stop, answer)
    monkeypatch.setattr(subprocess, "Popen", popen)


def test_cli_does_not_read_a_logs_real_lag_nor_a_verdict_wrappers_silence_as_a_hung_leaf_60s_of_lag_with_1s_of_progress_against_a_5s_window_and_6s_of_inner_progress_against_a_2s_window_exit_0(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    lagging = tmp_path / "reallag"
    lagging.mkdir()
    fake_clocked_leaf(monkeypatch, lagging, "reallag", silent=False, ends_at=1010, lag=60)
    lag_code, _, lag_err = run_cli(supervise, ["reallag", "leaf"], cwd=lagging,
                                   env={"VERI_STUCK_RETRIES": "0", "VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "30"})
    wrapped = tmp_path / "quiet-wrapper"
    (wrapped / ".tdd").mkdir(parents=True)
    reason = "The test pins the criterion as observable behavior.\n"
    (wrapped / ".tdd" / "verify-red.reason").write_text(reason)
    (wrapped / ".tdd" / "verdict-red.exit").write_text("0\n")
    fake_clocked_leaf(monkeypatch, wrapped, "verdict-red", silent=True, ends_at=1006)
    wrap_code, _, wrap_err = run_cli(supervise, ["verdict-red", "leaf"], cwd=wrapped,
                                     env={"VERI_STUCK_RETRIES": "0", "VERI_HEARTBEAT": "2", "VERI_TIMEOUT": "30"})
    assert [
        (lag_code, lag_err.splitlines()[-1:], (lagging / ".tdd" / "reallag.exit").read_text()),
        (wrap_code, wrap_err.splitlines()[-1:], (wrapped / ".tdd" / "verdict-red.exit").read_text(),
         (wrapped / ".tdd" / "verify-red.reason").read_text()),
    ] == [
        (0, ["supervise[reallag]: success"], "0\n"),
        (0, ["supervise[verdict-red]: success"], "0\n", reason),
    ]


class AwakeLeaf:
    pid = 4242
    returncode = None
    args = []

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode


def install_awake_fakes(monkeypatch, clock, leaf, sleep, stop, answer, popen=None):
    import time
    real_run, real_check_output = subprocess.run, subprocess.check_output
    real_call, real_check_call = subprocess.call, subprocess.check_call
    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: float(clock["awake"]))
    monkeypatch.setattr(os, "killpg", stop)
    monkeypatch.setattr(os, "kill", stop)

    def run(args, *a, **k):
        out = answer(args)
        if out is None:
            return real_run(args, *a, **k)
        return subprocess.CompletedProcess(args, 0, as_asked(out, k), as_asked("", k))

    def check_output(args, *a, **k):
        out = answer(args)
        return real_check_output(args, *a, **k) if out is None else as_asked(out, k)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", check_output)
    def call(args, *a, **k):
        return real_call(args, *a, **k) if answer(args) is None else 0

    def check_call(args, *a, **k):
        return real_check_call(args, *a, **k) if answer(args) is None else 0

    monkeypatch.setattr(subprocess, "call", call)
    monkeypatch.setattr(subprocess, "check_call", check_call)
    monkeypatch.setattr(subprocess, "Popen", popen or (lambda *a, **k: leaf))


def test_cli_does_not_read_a_suspend_as_silence_or_runtime_a_3s_suspend_against_a_2s_heartbeat_with_the_awake_clock_set_or_unset_a_3s_suspend_past_a_2s_timeout_and_an_hour_against_the_defaults_each_ending_in_the_leafs_own_exit_3(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def sleep_through(awake_clock, heartbeat, timeout, suspended):
        work = tmp_path / f"asleep-{len(list(tmp_path.iterdir()))}"
        (work / ".tdd").mkdir(parents=True)
        clean_env(monkeypatch, VERI_STUCK_RETRIES="0", VERI_HEARTBEAT=str(heartbeat), VERI_TIMEOUT=str(timeout),
                  **({"VERI_AWAKE_CLOCK": "/fake/awake-clock"} if awake_clock else {}))
        clock = {"wall": 1000, "awake": 5000, "sleeps": 0}
        kills = []

        leaf = AwakeLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 50:
                raise AssertionError("never ended")
            clock["wall"] += 1 + (suspended if clock["sleeps"] == 1 else 0)
            clock["awake"] += 1
            if clock["sleeps"] == 2:
                (work / ".tdd" / "suspended.log").write_text("leaf: awake again\n")
                (work / ".tdd" / "suspended.rc").write_text("3\n")
                leaf.returncode = 3

        def stop(_pid, sig):
            if sig:
                kills.append(sig)
                leaf.returncode = -sig

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["/fake/awake-clock"]:
                return f"{clock['awake']}\n"
            if args[:1] == ["git"]:
                return "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return f"{clock['wall']}\n"
            if args[:3] == ["stat", "-c", "%Y"]:
                return "1000\n"
            return ""

        install_awake_fakes(monkeypatch, clock, leaf, sleep, stop, answer)
        code, out, _ = run_cli(supervise, ["suspended", "leaf"], cwd=work)
        rc = work / ".tdd" / "suspended.rc"
        return (code, out, kills, rc.read_text() if rc.exists() else None)

    woke = (1, "leaf: awake again\n", [], "3\n")
    assert [sleep_through(True, 2, 30, 3), sleep_through(False, 2, 30, 3), sleep_through(True, 30, 2, 3),
            sleep_through(True, 180, 900, 3600)] == [woke, woke, woke, woke]


def test_cli_counts_awake_time_a_leaf_silent_1s_then_3s_against_a_2s_heartbeat_and_a_noisy_one_past_a_4s_timeout_with_or_without_load_stretching_the_wall_clock_3s_survives_the_first_and_is_killed_exit_2(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def run_until_killed(name, silent, heartbeat, timeout, load):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        clean_env(monkeypatch, VERI_STUCK_RETRIES="0", VERI_HEARTBEAT=str(heartbeat), VERI_TIMEOUT=str(timeout))
        clock = {"wall": 1000, "awake": 5000, "sleeps": 0, "killed_at": None}

        leaf = AwakeLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 50:
                raise AssertionError("never ended")
            clock["wall"] += 1 + (3 if load and clock["sleeps"] == 2 else 0)
            clock["awake"] += 1

        def stop(_pid, sig):
            if sig:
                if clock["killed_at"] is None:
                    clock["killed_at"] = clock["sleeps"]
                leaf.returncode = -sig

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["git"]:
                return "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return f"{clock['wall']}\n"
            if args[:3] == ["stat", "-c", "%Y"]:
                return "1000\n" if silent else f"{clock['wall']}\n"
            return ""

        install_awake_fakes(monkeypatch, clock, leaf, sleep, stop, answer)
        code, _, err = run_cli(supervise, [name, "leaf"], cwd=work)
        return code, clock["killed_at"], [line for line in err.splitlines() if "killed-stuck" in line or "no heartbeat" in line
                                          or "hard timeout" in line]

    assert [run_until_killed("silent", True, 2, 30, False), run_until_killed("runaway", False, 30, 4, False),
            run_until_killed("loaded", False, 30, 4, True)] == [
        (2, 3, ["supervise[silent]: killed-stuck — no heartbeat for 3s (window 2s)"]),
        (2, 4, ["supervise[runaway]: killed-stuck — hard timeout 4s exceeded"]),
        (2, 4, ["supervise[loaded]: killed-stuck — hard timeout 4s exceeded"]),
    ]


def test_cli_settles_the_hard_timeout_from_veri_timeout_else_the_issue_file_from_the_worktree_root_else_900_a_leaf_busy_10s_is_killed_at_3s_or_5s_or_finishes_exit_0_954(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def busy_ten(name, issue, explicit, subdir=None, record="3\n"):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        (work / ".tdd" / f"issue-{'954' if issue else ''}-timeout").write_text(record)
        (work / "src" / "deep").mkdir(parents=True)
        env = {"VERI_STUCK_RETRIES": "0", "VERI_HEARTBEAT": "30"}
        env.update({"VERI_ISSUE": "954"} if issue else {})
        env.update({"VERI_TIMEOUT": "5"} if explicit else {})
        clean_env(monkeypatch)
        clock = {"wall": 1000, "awake": 5000, "sleeps": 0}
        leaf = AwakeLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 50:
                raise AssertionError("never ended")
            clock["wall"] += 1
            clock["awake"] += 1
            if clock["sleeps"] == 10:
                (work / ".tdd" / "busy.log").write_text("leaf: finished on its own\n")
                (work / ".tdd" / "busy.rc").write_text("0\n")
                leaf.returncode = 0

        def stop(_pid, sig):
            if sig:
                leaf.returncode = -sig

        def answer(args):
            args = [str(a) for a in args]
            if "--show-toplevel" in args:
                return f"{work}\n"
            if args[:1] == ["git"]:
                return "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return f"{clock['wall']}\n"
            if args[:3] == ["stat", "-c", "%Y"]:
                return f"{clock['wall']}\n"
            return ""

        install_awake_fakes(monkeypatch, clock, leaf, sleep, stop, answer)
        code, _, err = run_cli(supervise, ["busy", "leaf"], env=env, cwd=work / (subdir or ""))
        return code, [line for line in err.splitlines() if "hard timeout" in line]

    assert [busy_ten("settled", True, False), busy_ten("unissued", False, False),
            busy_ten("subdir", True, False, subdir="src/deep"), busy_ten("explicit", True, True)] == [
        (2, ["supervise[busy]: killed-stuck — hard timeout 3s exceeded"]),
        (0, []),
        (2, ["supervise[busy]: killed-stuck — hard timeout 3s exceeded"]),
        (2, ["supervise[busy]: killed-stuck — hard timeout 5s exceeded"]),
    ]


REAL_LEAF_ENV = {"VERI_STUCK_RETRIES": "0", "VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "10"}


def prepare_real_leaf(monkeypatch, tmp_path, name):
    import time
    work = tmp_path / name
    work.mkdir()
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    fake_leaf_launch(monkeypatch)
    return work


def test_cli_reports_a_leafs_outcome_through_run_cli_success_and_failure_with_its_output_a_slow_but_alive_leaf_surviving_the_heartbeat_and_the_exit_record_of_0_1_and_2(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)

    def real_leaf(name, script):
        work = prepare_real_leaf(monkeypatch, tmp_path, name)
        code, out, err = run_cli(supervise, [name, "sh", "-c", script], cwd=work, env=REAL_LEAF_ENV)
        return code, out, err.splitlines()[-1:], (work / ".tdd" / f"{name}.exit").read_bytes()

    def clocked_leaf(name, silent, ends_at):
        work = tmp_path / name
        work.mkdir()
        fake_clocked_leaf(monkeypatch, work, name, silent, ends_at)
        code, _, err = run_cli(supervise, [name, "leaf"], cwd=work,
                               env={"VERI_STUCK_RETRIES": "0", "VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "5000"})
        return code, err.splitlines()[-1:], (work / ".tdd" / f"{name}.exit").read_bytes()

    assert [
        real_leaf("ok", "echo 'leaf: did the work'; exit 0"),
        real_leaf("fail", "echo 'leaf: blew up'; exit 3"),
        clocked_leaf("develop-slow", silent=False, ends_at=1030),
        clocked_leaf("develop-hang", silent=True, ends_at=10 ** 9),
    ] == [
        (0, "leaf: did the work\n", [b"supervise[ok]: success".decode()], b"0\n"),
        (1, "leaf: blew up\n", [b"supervise[fail]: failure".decode()], b"1\n"),
        (0, [b"supervise[develop-slow]: success".decode()], b"0\n"),
        (2, [b"supervise[develop-hang]: killed-stuck \xe2\x80\x94 no heartbeat for 6s (window 5s)".decode()], b"2\n"),
    ]


def test_cli_kills_a_hung_or_runaway_leaf_stuck_on_the_default_180s_or_an_explicit_window_once_under_an_ambient_veri_stuck_retries_leaving_no_usage_event_and_exiting_and_recording_2(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch, VERI_STUCK_RETRIES="3")
    launches = []

    def killed_leaf(name, silent, **env):
        work = tmp_path / name
        work.mkdir()
        fake_clocked_leaf(monkeypatch, work, name, silent, 10 ** 9, launches)
        monkeypatch.delenv("VERI_HEARTBEAT", raising=False)
        code, _, err = run_cli(supervise, [name, "leaf"], cwd=work, env={"VERI_STUCK_RETRIES": "0", **env})
        events = work / ".tdd" / "events.jsonl"
        usage = [line for line in (events.read_text().splitlines() if events.exists() else [])
                 if json.loads(line).get("event") == "usage"]
        lines = err.splitlines()
        return (code, [line for line in lines if line.startswith(f"supervise[{name}]")],
                [line for line in lines if "retry" in line], launches.count(name), usage,
                (work / ".tdd" / f"{name}.exit").read_bytes())

    hung = killed_leaf("hung", True, VERI_HEARTBEAT="5", VERI_TIMEOUT="5000")
    runaway = killed_leaf("runaway", False, VERI_HEARTBEAT="5000", VERI_TIMEOUT="7")
    unset = killed_leaf("unset", True, VERI_TIMEOUT="5000")
    assert [hung, runaway, unset] == [
        (2, ["supervise[hung]: killed-stuck — no heartbeat for 6s (window 5s)"], [], 1, [], b"2\n"),
        (2, ["supervise[runaway]: killed-stuck — hard timeout 7s exceeded"], [], 1, [], b"2\n"),
        (2, ["supervise[unset]: killed-stuck — no heartbeat for 181s (window 180s)"], [], 1, [], b"2\n"),
    ]


def test_cli_appends_one_retry_event_carrying_the_kill_cause_per_relaunch_and_one_exit_event_carrying_the_0_1_2_status_the_kill_cause_and_the_attempts_wall_seconds(
        monkeypatch, tmp_path, supervise, run_cli, events):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)

    def kept(work):
        return [r for r in events.records(work) if r["event"] in ("retry", "exit")]

    def real_leaf(name, script):
        work = prepare_real_leaf(monkeypatch, tmp_path, name)
        events.refuse_event_sh()
        run_cli(supervise, [name, "sh", "-c", script], cwd=work, env=REAL_LEAF_ENV)
        return kept(work)

    def hung_leaf(name, retries):
        work = tmp_path / name
        work.mkdir()
        fake_clocked_leaf(monkeypatch, work, name, True, 10 ** 9)
        launching = subprocess.Popen

        def popen(*a, **k):
            leaf = launching(*a, **k)
            leaf.returncode = None
            return leaf

        monkeypatch.setattr(subprocess, "Popen", popen)
        events.refuse_event_sh()
        run_cli(supervise, [name, "leaf"], cwd=work,
                env={"VERI_STUCK_RETRIES": retries, "VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "5000"})
        return kept(work)

    def shape(records):
        return [{k: v if k != "secs" else "n" if v.isdigit() else v for k, v in r.items()} for r in records]

    cause = "no heartbeat for 6s (window 5s)"
    def context(phase):
        return {"issue": "", "actor": "developer", "phase": phase, "step": "", "attempt": "1",
                "skill_commit": "0123456789abcdef0123456789abcdef01234567"}

    ok = real_leaf("develop-ok", "exit 0")
    failed = real_leaf("develop-fail", "exit 3")
    hung = hung_leaf("develop-hung", "0")
    retried = hung_leaf("develop-retried", "1")
    assert shape(ok) == [{**context("ok"), "event": "exit", "status": "0", "secs": "n"}]
    assert shape(failed) == [{**context("fail"), "event": "exit", "status": "1", "secs": "n"}]
    assert shape(hung) == [{**context("hung"), "event": "exit", "status": "2", "cause": cause, "secs": "n"}]
    assert int(hung[0]["secs"]) >= 5
    assert shape(retried)[:1] == [{**context("retried"), "event": "retry", "cause": cause}]
    assert [r["event"] for r in retried].count("retry") == 1
    assert {k: retried[-1][k] for k in ("event", "status", "cause")} == {"event": "exit", "status": "2", "cause": cause}


def test_cli_ends_a_killed_stuck_leaf_that_succeeds_on_its_retry_in_success_with_the_retrys_output(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    work = tmp_path / "flaky"
    work.mkdir()
    real_popen = subprocess.Popen
    fake_clocked_leaf(monkeypatch, work, "flaky", True, 10 ** 9)
    hanging = subprocess.Popen
    launches = []

    def popen(args, *a, **kwargs):
        launches.append(list(args))
        if len(launches) == 1:
            return hanging(args, *a, **kwargs)
        leaf = real_popen(args, *a, **kwargs)
        leaf.wait()
        return leaf

    monkeypatch.setattr(subprocess, "Popen", popen)
    code, out, err = run_cli(supervise, ["flaky", "sh", "-c", "echo 'leaf: recovered on retry'"], cwd=work,
                             env={"VERI_STUCK_RETRIES": "1", "VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "5000"})
    assert (code, out, err.splitlines()[-1:], (work / ".tdd" / "flaky.exit").read_bytes()) == (
        0, "leaf: recovered on retry\n", ["supervise[flaky]: success"], b"0\n")


def real_kill(tmp_path, supervise, run_cli, name, script, **env):
    import re
    import signal
    work = tmp_path / name
    work.mkdir()
    try:
        code, _, err = run_cli(supervise, [name, "sh", "-c", "ps -o pgid= -p $$ > stub.pgid; " + script], cwd=work,
                               env={"VERI_STUCK_RETRIES": "0", "VERI_POLL": "0.05", "VERI_KILL_POLL": "0.05", **env})
    finally:
        pids = {file: int((work / file).read_text()) for file in ("stub.pid", "child.pid") if (work / file).is_file()}
        group = int((work / "stub.pgid").read_text()) if (work / "stub.pgid").is_file() else None
        survivors = [pid for pid in pids.values() if alive(pid)]
        for pid in survivors:
            os.kill(pid, signal.SIGKILL)
        group_left = group is not None and group_alive(group)
        if group_left:
            os.killpg(group, signal.SIGKILL)
    if survivors or group_left:
        pytest.fail(f"real-kill {name}: recorded pids still alive after supervise returned, killed: {survivors} of {pids}"
                    + (f"; process group {group} still had a member, killed" if group_left else ""))
    return (code, [re.sub(r"for \d+s \(window", "for Ns (window", line) for line in err.splitlines() if line.startswith(f"supervise[{name}]")],
            (work / ".tdd" / f"{name}.exit").read_bytes(),
            {**{file: alive(pid) for file, pid in pids.items()}, "stub.pgid": group is not None and group_alive(group)})


@pytest.mark.process("a real hung and a real runaway leaf, killed by supervise.py's signal to their process group")
def test_cli_kills_a_real_hung_leaf_by_heartbeat_and_a_real_runaway_leaf_by_hard_timeout_leaving_none_of_their_recorded_stub_or_child_pids_nor_any_member_of_their_process_group_alive_1461(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    assert [
        real_kill(tmp_path, supervise, run_cli, "hung", "echo $$ > stub.pid; echo started; sleep 60 & echo $! > child.pid; wait",
                  VERI_HEARTBEAT="1", VERI_TIMEOUT="60"),
        real_kill(tmp_path, supervise, run_cli, "runaway",
                  "echo $$ > stub.pid; sleep 60 & echo $! > child.pid; while true; do echo busy; sleep 0.1; done",
                  VERI_HEARTBEAT="60", VERI_TIMEOUT="1"),
    ] == [
        (2, ["supervise[hung]: killed-stuck — no heartbeat for Ns (window 1s)"], b"2\n",
         {"stub.pid": False, "child.pid": False, "stub.pgid": False}),
        (2, ["supervise[runaway]: killed-stuck — hard timeout 1s exceeded"], b"2\n",
         {"stub.pid": False, "child.pid": False, "stub.pgid": False}),
    ]


@pytest.mark.process("a real runaway leaf whose group supervise.py's kill misses, left for the real-kill case's teardown to kill by its recorded pids")
def test_real_kill_teardown_kills_each_leaked_stub_pid_by_its_recorded_pid_and_fails_naming_every_survivor_1461(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def leader_only(pid, sig):
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass

    monkeypatch.setattr(supervise, "signal_tree", leader_only)
    clean_env(monkeypatch)
    work = tmp_path / "runaway"
    try:
        failure = ""
        try:
            real_kill(tmp_path, supervise, run_cli, "runaway",
                      "echo $$ > stub.pid; sleep 60 & echo $! > child.pid; while true; do echo busy; sleep 0.1; done",
                      VERI_HEARTBEAT="60", VERI_TIMEOUT="1")
        except (AssertionError, pytest.fail.Exception) as failed:
            failure = str(failed)
        pids = [int((work / file).read_text()) for file in ("stub.pid", "child.pid")]
        deadline = time.monotonic() + 5
        while any(alive(pid) for pid in pids) and time.monotonic() < deadline:
            time.sleep(0.05)
        assert ([str(pid) in failure for pid in pids], [alive(pid) for pid in pids]) == ([True, True], [False, False])
    finally:
        for file in ("stub.pid", "child.pid"):
            if (work / file).is_file() and alive(pid := int((work / file).read_text())):
                os.kill(pid, signal.SIGKILL)


@pytest.mark.process("a real leaf tree and a supervisor with TERM ignored, killed by supervise.py's TERM then KILL to the process group (#1199)")
def test_cli_leaves_no_process_of_a_killed_leafs_group_alive_when_the_supervisor_ignores_term_or_the_leader_dies_on_term_while_the_rest_ignore_it_for_silence_or_hard_timeout(
        monkeypatch, tmp_path, supervise, run_cli):
    import re
    import signal
    import time
    real_signal = signal.signal
    clean_env(monkeypatch)

    def settle(pid):
        for _ in range(30):
            if not alive(pid):
                return False
            time.sleep(0.1)
        os.kill(pid, signal.SIGKILL)
        return True

    def run(name, script, pids, **env):
        work = tmp_path / name
        work.mkdir()
        code, _, err = run_cli(supervise, ["develop-red", "sh", "-c", script], cwd=work,
                               env={"VERI_STUCK_RETRIES": "0", "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01", **env})
        left = {}
        for file in pids:
            text = (work / file).read_text().strip() if (work / file).exists() else ""
            left[file] = settle(int(text)) if text else "never recorded"
        why = re.search(r"killed-stuck — (no heartbeat|hard timeout)", err)
        return code, (work / ".tdd" / "develop-red.exit").read_bytes(), why and why.group(1), left

    ignoring_child = "(trap '' TERM; exec sleep 60) & echo $! > child-pid; wait"
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    real_signal(signal.SIGTERM, signal.SIG_IGN)
    try:
        ignored = run("term-ignored", "echo $$ > leaf-pid; exec sleep 60", ["leaf-pid"], VERI_HEARTBEAT="1", VERI_TIMEOUT="60")
    finally:
        real_signal(signal.SIGTERM, signal.SIG_DFL)
    answers = [
        ignored,
        run("silence", f"echo $$ > leaf-pid; {ignoring_child}", ["leaf-pid", "child-pid"], VERI_HEARTBEAT="1", VERI_TIMEOUT="60"),
        run("timeout", f"echo $$ > leaf-pid; {ignoring_child}", ["leaf-pid", "child-pid"], VERI_HEARTBEAT="60", VERI_TIMEOUT="1"),
    ]
    assert answers == [
        (2, b"2\n", "no heartbeat", {"leaf-pid": False}),
        (2, b"2\n", "no heartbeat", {"leaf-pid": False, "child-pid": False}),
        (2, b"2\n", "hard timeout", {"leaf-pid": False, "child-pid": False}),
    ]


SESSION_VARS = ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_HOST_SESSION_ID",
                "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_PID",
                "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_AUTO_BACKGROUND_TASKS")


def leaf_model_chain(monkeypatch, tmp_path, supervise, run_cli, name, extra=(), env=None, cwd=None):
    """supervise decides the model and records the exit with the leaf's start spied; run_leaf then builds claude's argv from that environment, claude's start faked."""
    import io
    import subprocess
    run_leaf = importlib.import_module("veri.run_leaf")
    started = []

    def attempt_once(_started, _name, cmd, log, rcfile, leaf_env, preexec, watch):
        started.append((cmd, leaf_env))
        return "success", "", "0", 0

    clean_env(monkeypatch)
    fake_git_only(monkeypatch, tmp_path)
    monkeypatch.setattr(supervise, "attempt_once", attempt_once)
    work = cwd or tmp_path / name
    work.mkdir(exist_ok=True)
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("pick the model")
    code, _, _ = run_cli(supervise, [name, "run-leaf.sh", str(prompt), *extra], cwd=work, env=dict(env or {}))
    exit_file = (work / ".tdd" / f"{name}.exit").read_text()
    leaf_env = started[0][1]
    launched = []

    class Claude:
        returncode = 0

        def __init__(self, command, env=None, **_):
            launched.append((command, env))
            reader, writer = os.pipe()
            os.write(writer, b'{"type":"result","subtype":"success","is_error":false,"result":"ok"}\n')
            os.close(writer)
            self.stdout = os.fdopen(reader, "rb", buffering=0)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.stdout.close()

    monkeypatch.setattr(subprocess, "Popen", Claude)
    leaf_vars = {k: v for k, v in leaf_env.items() if k == "VERI_LEAF_MODEL" or k in SESSION_VARS or k == "CLAUDE_BIN"}
    leaf_code, _, _ = run_cli(run_leaf, [*started[0][0][1:]], cwd=work, env={"CLAUDE_BIN": "claude", **leaf_vars})
    command, claude_env = launched[0]
    flags = [command[i + 1] for i, a in enumerate(command) if a == "--model"]
    return code, exit_file, leaf_code, flags, command, claude_env


def test_cli_launches_a_supervised_run_leaf_with_model_in_claudes_argv_only_when_the_run_chose_one_and_without_the_callers_session_variables(
        monkeypatch, tmp_path, supervise, run_cli):
    session = {v: "from-the-conductor" for v in SESSION_VARS}
    code, exit_file, leaf_code, flags, command, claude_env = leaf_model_chain(
        monkeypatch, tmp_path, supervise, run_cli, "develop-red", env={**session, "VERI_MODEL": "sonnet"}, cwd=tmp_path / "set")
    today = ["-p", "pick the model", "--output-format", "stream-json", "--verbose"]
    unset = leaf_model_chain(monkeypatch, tmp_path, supervise, run_cli, "develop-red", env=session, cwd=tmp_path / "unset")
    assert [(code, exit_file, leaf_code, command[1:len(today) + 1], flags,
             [v for v in SESSION_VARS if v in claude_env]) for code, exit_file, leaf_code, flags, command, claude_env in
            [(code, exit_file, leaf_code, flags, command, claude_env), unset]] == [
        (0, "0\n", 0, today, ["sonnet"], []),
        (0, "0\n", 0, today, ["sonnet"], []),
    ]
    assert command[-2:] == unset[4][-2:] == ["--model", "sonnet"]


def test_cli_launches_a_revise_leaf_on_veri_model_revise_recording_it_on_the_launch_and_passing_it_as_claudes_model(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    work = tmp_path / "revise"
    code, _, _, flags, _, _ = leaf_model_chain(
        monkeypatch, tmp_path, supervise, run_cli, "revise-green-2",
        env={"VERI_MODEL_DEVELOPER": "sonnet", "VERI_MODEL_REVISE": "opus"}, cwd=work)
    launches = [json.loads(line) for line in (work / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert (code, [e.get("model") for e in launches if e.get("event") == "launch"], flags) == (0, ["opus"], ["opus"])


def test_cli_launches_develop_red_and_verify_green_on_sonnet_and_revise_green_2_and_develop_exhausted_on_opus_when_no_model_variable_is_set(
        monkeypatch, tmp_path, supervise, run_cli):
    names = ["develop-red", "verify-green", "revise-green-2", "develop-exhausted"]
    got = {}
    for n in names:
        code, _, _, flags, _, _ = leaf_model_chain(monkeypatch, tmp_path, supervise, run_cli, n)
        got[n] = (code, flags[0] if flags else None)
    assert got == {
        "develop-red": (0, "sonnet"), "verify-green": (0, "sonnet"),
        "revise-green-2": (0, "opus"), "develop-exhausted": (0, "opus")}


def test_cli_launches_revise_green_1_on_opus_after_a_verify_green_reject_then_the_next_develop_red_and_develop_refactor_on_sonnet_in_the_same_tdd_directory_when_no_model_variable_is_set(
        monkeypatch, tmp_path, supervise, run_cli):
    work = tmp_path / "one-tdd-dir"
    names = ["verify-green", "revise-green-1", "develop-red", "develop-refactor"]
    got = []
    for n in names:
        code, _, _, flags, _, _ = leaf_model_chain(monkeypatch, tmp_path, supervise, run_cli, n, cwd=work)
        got.append((n, code, flags[0] if flags else None))
    assert got == [
        ("verify-green", 0, "sonnet"), ("revise-green-1", 0, "opus"),
        ("develop-red", 0, "sonnet"), ("develop-refactor", 0, "sonnet")]


def test_cli_launches_a_leaf_whose_own_arguments_carry_model_with_exactly_that_one_model_and_no_default_for_a_verifier_and_a_redo_leaf(
        monkeypatch, tmp_path, supervise, run_cli):
    names = ["verify-green", "revise-green-2", "develop-exhausted"]
    got = {}
    for n in names:
        code, _, _, flags, _, _ = leaf_model_chain(monkeypatch, tmp_path, supervise, run_cli, n, extra=["--model", "x"])
        got[n] = (code, flags)
    assert got == {n: (0, ["x"]) for n in names}


@pytest.mark.process("git runs for real, and the launch event is appended in-process: a launch event's skill_commit is the skill clone's own HEAD, or unknown outside a clone")
@pytest.mark.tree_audit("the shell scripts, veri/ and lib/ under scripts/")
def test_cli_records_the_skill_clones_own_head_in_a_launch_events_skill_commit_and_the_literal_unknown_for_a_skill_outside_a_git_clone(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    import shutil
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    skill = pathlib.Path(__file__).resolve().parents[2]
    outside = tmp_path / "nogit-skill"
    outside.mkdir()
    for script in skill.glob("*.sh"):
        shutil.copy(script, outside / script.name)
    shutil.copytree(skill / "veri", outside / "veri")
    shutil.copytree(skill / "lib", outside / "lib")
    head = skill_head()

    def launch_commit(arm, here):
        clean_env(monkeypatch)
        monkeypatch.setattr(supervise, "HERE", str(here))
        work = tmp_path / arm
        work.mkdir()
        code, _, _ = run_cli(supervise, ["develop-red", "sh", "-c", "echo leaf"], cwd=work, env=REAL_LEAF_ENV)
        launches = [json.loads(line) for line in (work / ".tdd" / "events.jsonl").read_text().splitlines()]
        return code, [e.get("skill_commit") for e in launches if e.get("event") == "launch"]

    assert len(head) == 40
    assert [launch_commit("clone", skill), launch_commit("outside", outside)] == [
        (0, [head]),
        (0, ["unknown"]),
    ]


def test_cli_recovers_a_killed_leaf_from_a_terminal_result_record_in_its_log_with_the_leafs_own_outcome_launched_once_its_stdout_ending_in_the_result_text_and_stays_killed_stuck_without_one(
        monkeypatch, tmp_path, supervise, run_cli):
    import re
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    launches = []

    def killed_leaf(name, log_text, retries):
        work = tmp_path / name
        work.mkdir()
        fake_clocked_leaf(monkeypatch, work, name, True, 10 ** 9)
        hanging = subprocess.Popen

        def popen(args, *a, **kwargs):
            launches.append(name)
            pathlib.Path(args[4]).write_bytes(log_text)
            return hanging(args, *a, **kwargs)

        monkeypatch.setattr(subprocess, "Popen", popen)
        env = {"VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "5000"}
        if retries is not None:
            env["VERI_STUCK_RETRIES"] = retries
        code, out, err = run_cli(supervise, [name, "leaf"], cwd=work, env=env)
        return code, out, err.splitlines()[-1:], launches.count(name), (work / ".tdd" / f"{name}.rc").exists()

    verdict = (b'{"type":"assistant","message":{"content":[]}}\n'
               b'{"type":"result","subtype":"success","is_error":false,'
               b'"result":"VERDICT: PASS\\nREASON: the new case fails on the eight checks"}\n')
    failed = b'{"type":"result","subtype":"error_during_execution","is_error":true,"result":"the suite did not finish"}\n'
    unfinished = b'{"type":"system","subtype":"init"}\n{"type":"assistant","message":{"content":[]}}\n'

    ok = killed_leaf("verify-ok", verdict, None)
    erred = killed_leaf("verify-err", failed, None)
    none = killed_leaf("verify-none", unfinished, "0")
    assert [ok[0], ok[2], ok[3], ok[4]] == [0, ["supervise[verify-ok]: success"], 1, False]
    assert [erred[0], erred[2], erred[3], erred[4]] == [1, ["supervise[verify-err]: failure"], 1, False]
    assert none[:1] == (2,) and none[2] == [
        "supervise[verify-none]: killed-stuck — no heartbeat for 6s (window 5s)"]
    assert ok[1].endswith("\nVERDICT: PASS\nREASON: the new case fails on the eight checks\n")
    assert erred[1].endswith("\nthe suite did not finish\n")
    head = []
    for line in (pathlib.Path(supervise.__file__).parents[1] / "supervise.sh").read_text().splitlines()[1:]:
        if not line.startswith("#"):
            break
        head.append(re.sub(r"^# ?", "", line))
    text = " ".join(head)
    assert re.search(r"(finish|complete)[a-z]* .{0,120}before .{0,80}(rc file|rcfile|\.rc)", text)
    assert re.search(r"kill.{0,160}not proof", text)


@pytest.mark.process("git and preserve-attempt.sh run for real: a killed-stuck leaf's attempts are written as git refs")
def test_cli_records_its_own_pid_before_the_leaf_launches_and_preserves_the_relaunched_attempt_and_the_final_one_each_as_its_own_tree_and_log(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    for key in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "EMAIL"):
        monkeypatch.delenv(key, raising=False)
    for key, value in {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_COUNT": "1",
                       "GIT_CONFIG_KEY_0": "user.useConfigOnly", "GIT_CONFIG_VALUE_0": "true"}.items():
        monkeypatch.setenv(key, value)
    real_run, real_check_output, real_popen = subprocess.run, subprocess.check_output, subprocess.Popen
    work = tmp_path / "preserve"
    work.mkdir()
    git = ["git", "-C", str(work), "-c", "user.name=veri", "-c", "user.email=veri@example.test"]
    real_run([*git, "init", "-q", "-b", "main"], check=True)
    real_run([*git, "config", "user.name", "veri"], check=True)
    real_run([*git, "config", "user.email", "veri@example.test"], check=True)
    (work / ".gitignore").write_text(".tdd/\n")
    (work / "src.txt").write_text("the step this leaf never finished\n")
    real_run([*git, "add", "-A"], check=True)
    real_run([*git, "commit", "-q", "-m", "initial"], check=True)

    clock = {"wall": 1000, "awake": 5000}
    seen_pids, leaf_box = [], []

    def sleep(_):
        clock["wall"] += 1
        clock["awake"] += 1
        if clock["wall"] > 5000:
            raise AssertionError("never ended")

    def answer(args):
        words = [str(a) for a in args]
        if words[:1] == ["date"]:
            return f"{clock['wall']}\n"
        if words[:1] == ["stat"]:
            return "1000\n"
        return None

    def popen(args, *a, **kwargs):
        if list(args[:2]) != ["/bin/sh", "-c"]:
            return real_popen(args, *a, **kwargs)
        pidfile = work / ".tdd" / "develop-red.pid"
        seen_pids.append(pidfile.read_text().strip() if pidfile.exists() else "<missing>")
        attempts = work / "attempts.txt"
        with attempts.open("a") as f:
            f.write("run\n")
        number = len(attempts.read_text().splitlines())
        pathlib.Path(args[4]).write_text(f"leaf: attempt {number}\n")
        leaf = StubLeaf()
        leaf_box.append(leaf)
        return leaf

    def stop(_pid, sig):
        if sig:
            leaf_box[-1].returncode = -sig

    install_awake_fakes(monkeypatch, clock, None, sleep, stop, answer, popen)

    code, _, _ = run_cli(supervise, ["develop-red", "leaf"], cwd=work, env={
        "VERI_ISSUE": "409", "VERI_STEP": "6", "VERI_HEARTBEAT": "1", "VERI_TIMEOUT": "5000"})

    refs = real_run([*git, "for-each-ref", "--format=%(refname)", "refs/veri/attempts/409/6/"],
                    capture_output=True, text=True).stdout.split()
    trees = sorted(len(real_run([*git, "show", f"{ref}:attempts.txt"], capture_output=True, text=True)
                       .stdout.splitlines()) for ref in refs)
    copies = sorted((work / ".tdd" / "attempts").glob("6-develop-red-*.log"))
    logged = sorted(c.read_text().split("leaf: attempt ")[1].split()[0] for c in copies)
    assert (code, seen_pids, len(refs), trees, len(copies), logged) == (
        2, [str(os.getpid()), str(os.getpid())], 2, [1, 2], 2, ["1", "2"])


@pytest.mark.process("a real TERM, INT and HUP delivered to the supervising process, a real leaf, and wait-leaf.sh run against a live supervisor.sh")
def test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    import threading
    import time
    clean_env(monkeypatch)
    sigs = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
    saved = {sig: signal.getsignal(sig) for sig in sigs}
    window = LIVE_LEAF_WINDOW
    held = "echo $$ > leaf-pid; exec sleep 60"

    def exit_now(code):
        raise SystemExit(code)

    monkeypatch.setattr(os, "_exit", exit_now)

    def leaf_pid(work):
        for _ in range(500):
            text = (work / "leaf-pid").read_text() if (work / "leaf-pid").exists() else ""
            if text.strip():
                return int(text)
            time.sleep(0.02)
        raise AssertionError("the leaf never started")

    def sent(work, sig, then=None):
        def deliver():
            leaf_pid(work)
            os.kill(os.getpid(), sig)
            if then:
                time.sleep(0.2)
                then()

        threading.Thread(target=deliver, daemon=True).start()

    def killed_by(label, sig):
        work = tmp_path / label
        work.mkdir()
        sent(work, sig)
        code, _, _ = run_cli(supervise, ["develop-red", "sh", "-c", held], cwd=work, env=window)
        pid = int((work / "leaf-pid").read_text())
        for _ in range(20):
            if not alive(pid):
                break
            time.sleep(0.1)
        left = alive(pid)
        if left:
            os.kill(pid, signal.SIGKILL)
        return code, (work / ".tdd" / "develop-red.exit").read_text(), left

    def ignored_int():
        work = tmp_path / "ignored-int"
        work.mkdir()
        release = work / "release"
        os.mkfifo(release)

        def let_go():
            fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
            os.write(fd, b"go\n")
            os.close(fd)

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        sent(work, signal.SIGINT, then=let_go)
        code, _, _ = run_cli(supervise, ["develop-red", "sh", "-c",
                                         "echo $$ > leaf-pid; read _ < release; echo leaf-released"],
                             cwd=work, env=window)
        return code, (work / ".tdd" / "develop-red.exit").read_text(), "leaf-released" in (
            work / ".tdd" / "develop-red.log").read_text()

    def waited_on_live():
        work = tmp_path / "wait-live"
        work.mkdir()
        sup = subprocess.Popen([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", held], cwd=work,
                               env={**os.environ, **window}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pid = None
        try:
            pid = leaf_pid(work)
            waited = subprocess.run([str(SCRIPTS / "wait-leaf.sh"), "develop-red", "0"], cwd=work,
                                    env={**os.environ, "VERI_POLL": "0.02"}, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE, text=True)
        finally:
            sup.send_signal(signal.SIGTERM)
            sup.wait()
            if pid and alive(pid):
                os.kill(pid, signal.SIGKILL)
        return waited.returncode, waited.stderr

    try:
        answers = [killed_by(f"signal-{sig.name}", sig) for sig in sigs]
        for sig in sigs:
            signal.signal(sig, saved[sig])
        answers.append(ignored_int())
        answers.append(waited_on_live())
    finally:
        for sig in sigs:
            signal.signal(sig, saved[sig])

    assert answers == [(2, "2\n", False), (2, "2\n", False), (2, "2\n", False), (0, "0\n", True), (3, "")]


@pytest.mark.process("supervise.sh run for real through a symlink to the skill directory from another cwd, with real preserve-attempt.sh and git; every event is appended in-process")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_in_place_with_events_usage_and_the_preserved_attempt_in_the_callers_tdd_the_skill_clones_head_and_no_tdd_beside_the_skill(
        monkeypatch, tmp_path):
    import json
    clean_env(monkeypatch)
    for key in ("VERI_SKILL_COMMIT", "VERI_ISSUE", "VERI_STEP"):
        monkeypatch.delenv(key, raising=False)
    skill = SCRIPTS.parent
    home = tmp_path / "home"
    home.mkdir()
    (home / "skill").symlink_to(skill, target_is_directory=True)
    link = home / "skill" / "scripts" / "supervise.sh"
    caller = tmp_path / "caller"
    caller.mkdir()
    identity = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
                "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    git = ["git", "-C", str(caller)]
    subprocess.run([*git, "init", "-q", "-b", "main"], check=True, env={**os.environ, **identity})
    (caller / ".gitignore").write_text(".tdd/\n")
    subprocess.run([*git, "add", "-A"], check=True, env={**os.environ, **identity})
    subprocess.run([*git, "commit", "-q", "-m", "initial"], check=True, env={**os.environ, **identity})
    result = tmp_path / "leaf-result"
    result.write_text("#!/bin/sh\n" + "echo '" + json.dumps(
        {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 91234, "duration_api_ms": 40118,
         "num_turns": 7, "result": "done", "session_id": "4d1a", "total_cost_usd": 0.31,
         "usage": {"input_tokens": 37, "cache_creation_input_tokens": 41002, "cache_read_input_tokens": 903117,
                   "output_tokens": 5140}}) + "'\n")
    result.chmod(0o755)
    hang = tmp_path / "leaf-hang"
    hang.write_text("#!/bin/sh\necho started\nexec sleep 60\n")
    hang.chmod(0o755)
    head = skill_head()
    beside = [SCRIPTS / ".tdd", skill / ".tdd", home / ".tdd"]
    beside_before = [p for p in beside if p.exists()]
    env = {**os.environ, **identity, "VERI_STUCK_RETRIES": "0", "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}

    def supervise_run(name, leaf, extra):
        return subprocess.run([str(link), name, str(leaf)], cwd=caller, env={**env, **extra}, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True).returncode

    ok_code = supervise_run("develop-red", result, {"VERI_HEARTBEAT": "30", "VERI_TIMEOUT": "60"})
    kill_code = supervise_run("develop-green", hang, {"VERI_ISSUE": "1073", "VERI_STEP": "5", "VERI_HEARTBEAT": "1",
                                                      "VERI_TIMEOUT": "30"})

    events = [json.loads(line) for line in (caller / ".tdd" / "events.jsonl").read_text().splitlines()]
    refs = subprocess.run([*git, "for-each-ref", "--format=%(refname)", "refs/veri/attempts/1073/5/"],
                          capture_output=True, text=True, env={**os.environ, **identity}).stdout.split()
    assert len(head) == 40
    assert (ok_code, kill_code,
            [e["event"] for e in events if e["event"] in ("launch", "exit")].count("launch"),
            [e["event"] for e in events].count("exit"),
            [e.get("num_turns") for e in events if e["event"] == "usage"],
            {e.get("skill_commit") for e in events if e["event"] == "launch"},
            len(refs),
            sorted(p.name for p in (caller / ".tdd").iterdir() if p.suffix in (".log", ".exit", ".pid")),
            [p for p in beside if p.exists()] == beside_before) == (
        0, 2, 2, 2, ["7"], {head}, 1,
        ["develop-green.exit", "develop-green.log", "develop-green.pid",
         "develop-red.exit", "develop-red.log", "develop-red.pid"], True)


@pytest.mark.process("a real supervise.sh with a live leaf, refusing a second launch through run_cli while that leaf's process is alive")
def test_cli_refuses_a_launch_under_another_name_or_the_same_name_even_after_the_pre_launch_rm_of_exit_and_pid_exit_2_naming_the_live_leaf_and_its_supervisors_pid_running_nothing_while_a_leaf_is_alive_in_the_worktree_471(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    work = tmp_path / "live"
    work.mkdir()
    window = LIVE_LEAF_WINDOW
    sup = subprocess.Popen([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", "echo $$ > leaf-pid; exec sleep 60"],
                           cwd=work, env={**os.environ, **window}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    leaf = None
    try:
        for _ in range(500):
            if (work / "leaf-pid").is_file() and (work / ".tdd" / "leaf.owner").is_file() \
                    and (work / "leaf-pid").read_text().strip():
                break
            time.sleep(0.02)
        else:
            raise AssertionError("the first leaf never started")
        leaf = int((work / "leaf-pid").read_text())

        def second(name):
            (work / "ran").unlink(missing_ok=True)
            code, out, err = run_cli(supervise, [name, "sh", "-c", "echo ran > ran"], cwd=work, env=window)
            return code, out, err.strip().splitlines()[-1:], (work / "ran").exists()

        answers = [second("verify-red"), second("develop-red")]
        for suffix in ("exit", "pid"):
            (work / ".tdd" / f"develop-red.{suffix}").unlink(missing_ok=True)
        answers.append(second("develop-red"))
        assert answers == [
            (2, "", [REFUSAL.format("verify-red", "develop-red", sup.pid)], False),
            (2, "", [REFUSAL.format("develop-red", "develop-red", sup.pid)], False),
            (2, "", [REFUSAL.format("develop-red", "develop-red", sup.pid)], False),
        ]
    finally:
        sup.send_signal(signal.SIGTERM)
        sup.wait()
        if leaf and alive(leaf):
            os.kill(leaf, signal.SIGKILL)


@pytest.mark.process("a real supervise.sh run under run_cli, and a real leaf that launches a nested supervise.sh from inside its own live supervision")
def test_cli_launches_when_the_recorded_leaf_is_gone_or_finished_under_the_same_name_or_another_and_a_verify_green_from_inside_a_live_verdict_green_supervision_471(
        monkeypatch, tmp_path, supervise, run_cli):
    import shlex
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    clean_env(monkeypatch)
    window = LIVE_LEAF_WINDOW
    sup = str(SCRIPTS / "supervise.sh")

    def launch(work, name, *argv):
        code, _, err = run_cli(supervise, [name, *argv], cwd=work, env=window)
        return code, [line for line in err.splitlines() if "refusing" in line]

    gone = tmp_path / "gone"
    (gone / ".tdd").mkdir(parents=True)
    corpse = subprocess.Popen(["true"])
    corpse.wait()
    (gone / ".tdd" / "leaf.owner").write_text(f"{corpse.pid} revise-green-1\n")
    gone_answer = (launch(gone, "revise-green-1", "sh", "-c", "echo ran > ran"), (gone / "ran").exists(),
                   (gone / ".tdd" / "leaf.owner").read_text().endswith(" revise-green-1\n"))

    done = tmp_path / "done"
    done.mkdir()
    done_answers = []
    for name, word in (("revise-green-1", "first"), ("revise-green-1", "second"), ("verify-green", "third")):
        for suffix in ("exit", "pid"):
            (done / ".tdd" / f"{name}.{suffix}").unlink(missing_ok=True)
        with monkeypatch.context() as finished:
            finished.setattr(os, "getpid", lambda: corpse.pid)
            done_answers.append(launch(done, name, "sh", "-c", f"echo {word} >> ran"))

    nest = tmp_path / "nest"
    nest.mkdir()
    inner = f"{shlex.quote(sup)} verify-green sh -c 'echo inner >> ran' 2> inner-err; echo $? > inner-code"
    nest_answer = (launch(nest, "verdict-green", "sh", "-c", inner),
                   (nest / "inner-code").read_text().strip(), (nest / "ran").read_text(),
                   "refusing" in (nest / "inner-err").read_text())

    assert (gone_answer, done_answers, (done / "ran").read_text(), nest_answer) == (
        ((0, []), True, True),
        [(0, []), (0, []), (0, [])],
        "first\nsecond\nthird\n",
        ((0, []), "0", "inner\n", False),
    )


def test_cli_refuses_a_launch_while_a_recorded_leaf_is_alive_writing_2_for_another_name_and_none_for_the_same_one_running_nothing_leaving_leaf_owner_and_wait_leaf_answering_2_618(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    wait_leaf = importlib.import_module("veri.wait_leaf")
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(wait_leaf, "clock", lambda: 1000)
    clean_env(monkeypatch)
    live = f"{os.getpid()} develop-green\n"

    def refused(name):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        (work / ".tdd" / "leaf.owner").write_text(live)
        fake_git_only(monkeypatch, work)
        code, out, err = run_cli(supervise, [name, "sh", "-c", "echo ran > ran"], cwd=work)
        exit_file = work / ".tdd" / f"{name}.exit"
        return (code, out, err.splitlines()[-1:], exit_file.read_text() if exit_file.exists() else None,
                (work / ".tdd" / "leaf.owner").read_text(), (work / "ran").exists(),
                run_cli(wait_leaf, [name, "0"], cwd=work)[0])

    assert [refused("verdict-green"), refused("develop-green")] == [
        (2, "", [REFUSAL.format("verdict-green", "develop-green", os.getpid())], "2\n", live, False, 2),
        (2, "", [REFUSAL.format("develop-green", "develop-green", os.getpid())], None, live, False, 3),
    ]


def test_header_names_the_watchdogs_clock_source_and_why_it_pauses_while_the_machine_is_suspended_for_macos_and_linux_472():
    import re
    header = []
    for line in (SCRIPTS / "supervise.sh").read_text().splitlines()[1:]:
        if not line.startswith("#"):
            break
        header.append(re.sub(r"^# ?", "", line))
    text = " ".join(header)
    claims = {
        "clock-source": r"monotonic",
        "macos": r"macOS.{0,200}(suspend|sleep)|(suspend|sleep).{0,200}macOS",
        "linux": r"Linux.{0,200}(suspend|sleep)|(suspend|sleep).{0,200}Linux",
        "pauses-in-suspend": r"(not advance|stop[a-z]* advancing|pause[a-z]*|stand[a-z]* still|stop[a-z]*).{0,160}(suspend|asleep|sleep)",
    }
    assert [name for name, pattern in claims.items() if not re.search(pattern, text)] == []


def test_run_cli_reports_a_leaf_awake_2s_and_suspended_100s_as_exit_status_0_with_the_awake_seconds_as_secs_not_the_wall_seconds_neither_killed_nor_reported_early_across_the_suspended_polls(
        monkeypatch, tmp_path, supervise, run_cli, events):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    work = tmp_path / "slept"
    (work / ".tdd").mkdir(parents=True)
    clean_env(monkeypatch)
    events.refuse_event_sh()
    clock = {"wall": 1000, "awake": 5000, "sleeps": 0}
    suspended_polls, kills = [], []

    leaf = StubLeaf()

    def sleep(_):
        clock["sleeps"] += 1
        if clock["sleeps"] > 50:
            raise AssertionError("the supervisor never saw the leaf finish")
        if clock["sleeps"] == 1:
            clock["wall"] += 2
            clock["awake"] += 2
        elif clock["sleeps"] == 2:
            clock["wall"] += 100
        if clock["sleeps"] >= 2:
            suspended_polls.append(clock["sleeps"])
        if clock["sleeps"] == 4:
            (work / ".tdd" / "develop-red.rc").write_text("0\n")
            leaf.returncode = 0

    def answer(args):
        args = [str(a) for a in args]
        if "--show-toplevel" in args:
            return f"{work}\n"
        if args[:1] == ["git"]:
            return "0123456789abcdef0123456789abcdef01234567\n"
        if args[:1] == ["date"]:
            return f"{clock['wall']}\n"
        if args[:1] == ["stat"]:
            return "1000\n"
        return ""

    def run(args, *_, **kwargs):
        out = as_asked(answer(args), kwargs)
        return subprocess.CompletedProcess(args, 0, out, "" if isinstance(out, str) else b"")

    def popen(args, *_, **kwargs):
        if list(args[:2]) == ["/bin/sh", "-c"]:
            return leaf
        raise AssertionError(f"unexpected Popen: {args}")

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: clock["awake"] + 0.5)
    monkeypatch.setattr(os, "killpg", lambda pgid, sig: kills.append(sig))
    monkeypatch.setattr(os, "kill", lambda pid, sig: kills.append(sig))
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", lambda args, *a, **k: as_asked(answer(args), k))
    monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
    monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, **k).returncode)
    monkeypatch.setattr(subprocess, "Popen", popen)

    code, _, err = run_cli(supervise, ["develop-red", "leaf-slept-through"], cwd=work,
                           env={"VERI_ISSUE": "486", "VERI_STEP": "1", "VERI_HEARTBEAT": "30",
                                "VERI_TIMEOUT": "30", "VERI_STUCK_RETRIES": "0"})

    exits = [r for r in events.records(work) if r["event"] == "exit"]
    assert (code, kills, [r["status"] for r in exits], [r["secs"] for r in exits],
            len(suspended_polls) >= 2, "killed-stuck" in err) == (0, [], ["0"], ["2"], True, False)


def test_main_still_kills_a_4s_quiet_leaf_by_a_1s_hard_timeout_and_by_a_1s_heartbeat_when_time_monotonic_restarts_per_process(
        monkeypatch, tmp_path, run_cli, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(time, "monotonic", lambda: 0.0)

    def watch(window):
        clean_env(monkeypatch)
        clock = {"wall": 1000, "awake": 5000, "sleeps": 0}

        leaf = StubLeaf()

        def sleep(_):
            clock["sleeps"] += 1
            if clock["sleeps"] > 2000:
                raise Runaway()
            clock["wall"] += 1
            clock["awake"] += 1
            if clock["sleeps"] == 4:
                leaf.returncode = 0

        def killpg(pgid, sig):
            if pgid == leaf.pid and sig:
                leaf.returncode = -sig

        def kill(pid, sig):
            if pid < 0:
                return killpg(-pid, sig)
            if pid == leaf.pid and sig:
                leaf.returncode = -sig

        def answer(args):
            args = [str(a) for a in args]
            if args[:3] == ["git", "rev-parse", "--show-toplevel"]:
                return 0, f"{tmp_path}\n"
            if args[:1] == ["git"]:
                return 0, "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return 0, f"{clock['wall']}\n"
            if args[:3] == ["stat", "-c", "%Y"]:
                return 0, "1000\n"
            if args[:1] == ["stat"]:
                return 1, ""
            return 0, ""

        def run(args, *_, **kwargs):
            code, out = answer(args)
            out = as_asked(out, kwargs)
            if code and kwargs.get("check"):
                raise subprocess.CalledProcessError(code, args, out)
            return subprocess.CompletedProcess(args, code, out, "" if isinstance(out, str) else b"")

        def check_output(args, *_, **kwargs):
            code, out = answer(args)
            if code:
                raise subprocess.CalledProcessError(code, args)
            return as_asked(out, kwargs)

        def popen(args, *_, **kwargs):
            if list(args[:2]) == ["/bin/sh", "-c"]:
                return leaf
            raise AssertionError(f"unexpected Popen: {args}")

        monkeypatch.setattr(time, "sleep", sleep)
        monkeypatch.setattr(time, "clock_gettime", lambda *_: clock["awake"] + 0.5)
        monkeypatch.setattr(os, "killpg", killpg)
        monkeypatch.setattr(os, "kill", kill)
        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "check_output", check_output)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
        monkeypatch.setattr(subprocess, "Popen", popen)
        try:
            code, _, err = run_cli(supervise, ["develop-red", "leaf-quiet"], cwd=tmp_path,
                                   env={"VERI_STUCK_RETRIES": "0", "VERI_POLL": "0.02",
                                        "VERI_KILL_POLL": "0.01", **window})
        except Runaway:
            return "<never ended>", []
        return code, [line for line in err.splitlines() if line.startswith("supervise[")][-1:]

    timeout = watch({"VERI_HEARTBEAT": "999", "VERI_TIMEOUT": "1"})
    heartbeat = watch({"VERI_HEARTBEAT": "1", "VERI_TIMEOUT": "999"})

    assert (timeout[0], "hard timeout" in "".join(timeout[1]),
            heartbeat[0], "no heartbeat" in "".join(heartbeat[1])) == (2, True, 2, True), (timeout, heartbeat)


def test_main_launches_a_leaf_that_never_answers_the_same_number_of_times_with_veri_no_verdict_retries_above_or_below_veri_stuck_retries_as_without_it_1440(
        monkeypatch, tmp_path, supervise, run_cli):
    import signal
    monkeypatch.setattr(signal, "signal", lambda *_: None)

    def launches_of_a_silent_leaf(label, **env):
        work = tmp_path / label
        (work / ".tdd").mkdir(parents=True)
        clean_env(monkeypatch, VERI_STUCK_RETRIES="1", VERI_HEARTBEAT="3", VERI_TIMEOUT="5000", **env)
        clock = {"wall": 1000, "awake": 5000}
        launched = []

        def sleep(_):
            clock["wall"] += 1
            clock["awake"] += 1
            if clock["wall"] > 5000:
                raise AssertionError("never ended")

        def stop(_pid, sig):
            if sig:
                launched[-1].returncode = -sig

        def answer(args):
            args = [str(a) for a in args]
            if args[:1] == ["git"]:
                return "0123456789abcdef0123456789abcdef01234567\n"
            if args[:1] == ["date"]:
                return f"{clock['wall']}\n"
            if args[:1] == ["stat"]:
                return "1000\n"
            return ""

        install_awake_fakes(monkeypatch, clock, StubLeaf(), sleep, stop, answer)

        def popen(args, *_, **k):
            launched.append(StubLeaf())
            return launched[-1]

        monkeypatch.setattr(subprocess, "Popen", popen)
        code, _, _ = run_cli(supervise, ["hang", "leaf"], cwd=work)
        return code, len(launched)

    assert launches_of_a_silent_leaf("alone") == (2, 2)
    assert launches_of_a_silent_leaf("with-no-verdict", VERI_NO_VERDICT_RETRIES="5") == (2, 2)
    assert launches_of_a_silent_leaf("with-no-verdict-below", VERI_NO_VERDICT_RETRIES="0") == (2, 2)


def spy_leaf_start(monkeypatch, tmp_path, supervise):
    """git answers in-process; the leaf's start is a spy that records itself and reports a clean exit."""
    fake_git_only(monkeypatch, tmp_path)
    started = []

    def attempt_once(*_):
        started.append(True)
        return "success", "", "0", 0

    monkeypatch.setattr(supervise, "attempt_once", attempt_once)
    return started


def test_cli_refuses_a_develop_green_launch_whose_step_has_a_red_launch_followed_only_by_a_verify_red_reject_starting_no_leaf_and_naming_the_step_and_the_missing_pass_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
        {**base, "ts": 2, "event": "verdict", "actor": "verifier", "phase": "red", "step": "3", "attempt": "1",
         "verdict": "REJECT"},
        {**base, "ts": 3, "event": "verdict", "actor": "verifier", "phase": "red", "step": "4", "attempt": "1",
         "verdict": "PASS"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": "3"})

    assert (code, out, bool(started)) == (2, "", False)
    lines = err.splitlines()
    assert len(lines) == 1 and "step 3" in lines[0] and "verify-red" in lines[0] and "PASS" in lines[0], err


def test_cli_refuses_a_develop_green_launch_whose_step_has_a_red_launch_with_no_verdict_after_it_starting_no_leaf_and_naming_the_step_and_the_missing_pass_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
        {**base, "ts": 2, "event": "verdict", "actor": "verifier", "phase": "red", "step": "4", "attempt": "1",
         "verdict": "PASS"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": "3"})

    assert (code, out, bool(started)) == (2, "", False)
    lines = err.splitlines()
    assert len(lines) == 1 and "step 3" in lines[0] and "verify-red" in lines[0] and "PASS" in lines[0], err


def test_cli_refuses_a_develop_green_launch_whose_only_verify_red_pass_precedes_a_later_red_launch_of_the_step_starting_no_leaf_and_naming_the_step_and_the_missing_pass_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
        {**base, "ts": 2, "event": "verdict", "actor": "verifier", "phase": "red", "step": "3", "attempt": "1",
         "verdict": "PASS"},
        {**base, "ts": 3, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "2"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": "3"})

    assert (code, out, bool(started)) == (2, "", False)
    lines = err.splitlines()
    assert len(lines) == 1 and "step 3" in lines[0] and "verify-red" in lines[0] and "PASS" in lines[0], err


def test_cli_launches_a_develop_green_whose_step_has_a_verify_red_pass_after_its_latest_red_launch_and_records_the_stub_exit_status_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
        {**base, "ts": 2, "event": "verdict", "actor": "verifier", "phase": "red", "step": "3", "attempt": "1",
         "verdict": "REJECT"},
        {**base, "ts": 3, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "2"},
        {**base, "ts": 4, "event": "verdict", "actor": "verifier", "phase": "red", "step": "3", "attempt": "2",
         "verdict": "PASS"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": "3"})

    assert (code, bool(started), (tmp_path / ".tdd" / "develop-green.exit").read_text().strip()) == (0, True, "0"), err


def test_cli_launches_a_develop_green_whose_step_has_a_verify_pin_pass_after_its_latest_red_launch_and_records_the_stub_exit_status_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
        {**base, "ts": 2, "event": "verdict", "actor": "verifier", "phase": "pin", "step": "3", "attempt": "1",
         "verdict": "PASS"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": "3"})

    assert (code, bool(started), (tmp_path / ".tdd" / "develop-green.exit").read_text().strip()) == (0, True, "0"), err


def test_cli_launches_a_develop_green_whose_ci_repair_step_has_a_red_launch_and_no_verdict_and_records_the_stub_exit_status_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1741.md").write_text(
        "# Plan for #1741\n\n"
        "- [x] first step\n"
        "- [x] second step\n"
        "- [ ] fix the CI failure: suite — FAIL - case ⟦ci-repair⟧\n")
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": "3"})

    exitfile = tmp_path / ".tdd" / "develop-green.exit"
    assert (code, bool(started), exitfile.read_text().strip() if exitfile.exists() else None) == (0, True, "0"), err


def test_cli_launches_a_develop_green_whose_ci_repair_step_is_named_by_its_full_ledger_text_after_a_red_launch_with_no_verdict_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    text = "fix the CI failure: suite — FAIL - case ⟦ci-repair⟧"
    (tmp_path / ".tdd" / "issue-1741.md").write_text(
        "# Plan for #1741\n\n"
        "- [x] first step\n"
        "- [x] second step\n"
        f"- [ ] {text}\n")
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": text, "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": text})

    exitfile = tmp_path / ".tdd" / "develop-green.exit"
    assert (code, bool(started), exitfile.read_text().strip() if exitfile.exists() else None) == (0, True, "0"), err


def test_cli_refuses_a_develop_green_launch_whose_step_without_the_ci_repair_mark_is_named_by_its_full_ledger_text_after_a_red_launch_with_no_verdict_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    text = "add the retry knob to supervise"
    (tmp_path / ".tdd" / "issue-1741.md").write_text(
        "# Plan for #1741\n\n"
        "- [x] first step\n"
        "- [x] second step\n"
        f"- [ ] {text}\n")
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": text, "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": text})

    assert (code, out, bool(started)) == (2, "", False)
    lines = err.splitlines()
    assert len(lines) == 1 and text in lines[0] and "verify-red" in lines[0] and "PASS" in lines[0], err


def test_cli_refuses_a_develop_green_launch_whose_step_names_ci_repair_mid_sentence_after_a_red_launch_with_no_verdict_1989(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    text = "stop treating ⟦ci-repair⟧ as a mark anywhere in the text"
    (tmp_path / ".tdd" / "issue-1989.md").write_text(
        "# Plan for #1989\n\n"
        "- [x] first step\n"
        f"- [ ] {text}\n")
    base = {"issue": "1989", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "2", "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1989", "VERI_STEP": "2"})

    assert (code, out, bool(started)) == (2, "", False), err
    assert "has no verify-red PASS after its latest red leaf" in err


def test_cli_launches_a_develop_green_whose_ci_repair_mark_is_one_of_several_trailing_markers_after_a_red_launch_with_no_verdict_1989(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1989.md").write_text(
        "# Plan for #1989\n\n"
        "- [x] first step\n"
        "- [ ] fix the CI failure: suite — FAIL - case ⟦ci-repair⟧ ⟦phases: red, green⟧\n")
    base = {"issue": "1989", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "2", "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1989", "VERI_STEP": "2"})

    exitfile = tmp_path / ".tdd" / "develop-green.exit"
    assert (code, bool(started), exitfile.read_text().strip() if exitfile.exists() else None) == (0, True, "0"), err


def test_cli_refuses_a_develop_green_launch_whose_open_step_lacks_the_ci_repair_mark_though_an_earlier_done_step_carries_it_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    text = "split off the edge case ⟦added⟧"
    (tmp_path / ".tdd" / "issue-1741.md").write_text(
        "# Plan for #1741\n\n"
        "- [x] first step\n"
        "- [x] fix the CI failure: suite.test.sh — FAIL - case ⟦ci-repair⟧\n"
        f"- [ ] {text}\n")
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": text, "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": text})

    assert (code, out, bool(started)) == (2, "", False), err


def test_cli_refuses_a_develop_green_launch_when_a_red_launch_follows_a_non_json_line_that_follows_the_only_verify_red_pass_1977(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1977", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
        {**base, "ts": 2, "event": "verdict", "actor": "verifier", "phase": "red", "step": "3", "attempt": "1",
         "verdict": "PASS"},
    ]
    later = {**base, "ts": 3, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "2"}
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        "".join(json.dumps(line) + "\n" for line in log) + "this line is not json\n" + json.dumps(later) + "\n")
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1977", "VERI_STEP": "3"})

    assert (code, out, bool(started)) == (2, "", False), err
    assert "step 3" in err and "verify-red" in err, err


def test_cli_leaves_no_launch_event_and_no_owner_file_when_it_refuses_a_develop_green_launch_for_a_missing_verify_red_pass_1741(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1741", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
        {**base, "ts": 2, "event": "verdict", "actor": "verifier", "phase": "red", "step": "3", "attempt": "1",
         "verdict": "REJECT"},
    ]
    events = tmp_path / ".tdd" / "events.jsonl"
    events.write_text("".join(json.dumps(line) + "\n" for line in log))
    before = events.read_text()
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1741", "VERI_STEP": "3"})

    assert code == 2, err
    assert (events.read_text(), (tmp_path / ".tdd" / "leaf.owner").exists()) == (before, False), err


@pytest.mark.process("detach-leaf.sh, supervise.sh and wait-leaf.sh run for real over a refused develop-green launch (#1754)")
def test_cli_records_exit_2_for_a_refused_develop_green_launched_detached_so_wait_leaf_returns_2_not_3_and_no_leaf_starts_1754(
        monkeypatch, tmp_path):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    base = {"issue": "1754", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "3", "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    stub.write_text("#!/bin/sh\ntouch ran\n")
    stub.chmod(0o755)
    env = {**os.environ, "VERI_ISSUE": "1754", "VERI_STEP": "3", "VERI_POLL": "0.05"}

    detached = subprocess.run([str(SCRIPTS / "detach-leaf.sh"), str(SCRIPTS / "supervise.sh"), "develop-green",
                               str(stub)], cwd=tmp_path, env=env, capture_output=True, text=True)
    waited = subprocess.run([str(SCRIPTS / "wait-leaf.sh"), "develop-green", "3"], cwd=tmp_path, env=env,
                            capture_output=True, text=True)

    assert (detached.returncode, waited.returncode, (tmp_path / "ran").exists()) == (0, 2, False), waited.stderr


def test_cli_refuses_a_launch_whose_veri_step_is_set_but_empty_exiting_2_naming_veri_step_starting_no_leaf_and_appending_one_launch_refused_event_1760(
        monkeypatch, tmp_path, supervise, run_cli, events):
    clean_env(monkeypatch)
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["verify-red", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1760", "VERI_STEP": ""})

    lines = err.splitlines()
    assert (code, out, len(lines)) == (2, "", 1), err
    assert "VERI_STEP" in lines[0], err
    assert (bool(started), (tmp_path / ".tdd" / "leaf.owner").exists()) == (False, False), err
    records = events.records(tmp_path)
    assert [r["event"] for r in records] == ["launch-refused"], records
    assert (records[0]["name"], bool(records[0]["reason"])) == ("verify-red", True), records


def test_cli_refuses_a_verifier_launch_whose_step_argument_is_empty_exiting_2_naming_step_starting_no_leaf_and_appending_one_launch_refused_event_1760(
        monkeypatch, tmp_path, supervise, run_cli, events):
    clean_env(monkeypatch)
    stub = tmp_path / "run-verdict.sh"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["verdict-red", str(stub), "--step", "", "red", "spec.md", "t.sh", "case"],
                             cwd=tmp_path, env={"VERI_ISSUE": "1760"})

    lines = err.splitlines()
    assert (code, out, len(lines)) == (2, "", 1), err
    assert "--step" in lines[0], err
    assert bool(started) is False, err
    records = events.records(tmp_path)
    assert [r["event"] for r in records] == ["launch-refused"], records
    assert (records[0]["name"], bool(records[0]["reason"])) == ("verdict-red", True), records


def test_cli_records_2_in_the_exit_file_of_a_launch_refused_for_an_empty_veri_step_1760(
        monkeypatch, tmp_path, supervise, run_cli):
    clean_env(monkeypatch)
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, _, err = run_cli(supervise, ["verify-red", str(stub)], cwd=tmp_path,
                           env={"VERI_ISSUE": "1760", "VERI_STEP": ""})

    exit_file = tmp_path / ".tdd" / "verify-red.exit"
    assert (exit_file.read_text().strip() if exit_file.is_file() else None, code) == ("2", 2), err


def test_cli_launches_a_develop_green_whose_ci_repair_step_is_numbered_as_ledger_steps_numbers_it_past_a_non_step_box_line_1973(
        monkeypatch, tmp_path, supervise, run_cli):
    import json
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1973.md").write_text(
        "# Plan for #1973\n\n"
        "- [-] a note that is not a step\n"
        "- [x] first step\n"
        "- [ ] fix the CI failure: suite — FAIL - case ⟦ci-repair⟧\n")
    base = {"issue": "1973", "skill_commit": "unknown"}
    log = [
        {**base, "ts": 1, "event": "launch", "actor": "developer", "phase": "red", "step": "2", "attempt": "1"},
    ]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in log))
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    code, out, err = run_cli(supervise, ["develop-green", str(stub)], cwd=tmp_path,
                             env={"VERI_ISSUE": "1973", "VERI_STEP": "2"})

    assert (code, bool(started)) == (0, True), err


def test_red_awaits_pass_reads_an_events_log_holding_an_invalid_utf_8_byte_without_raising_and_still_reads_the_launch_and_verdict_lines_after_it(
        supervise, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    log = tmp_path / ".tdd" / "events.jsonl"
    launch = b'{"event": "launch", "phase": "red", "step": 1}\n'
    verdict = b'{"event": "verdict", "phase": "red", "step": 1, "verdict": "PASS"}\n'

    log.write_bytes(b'{"note": "bad \xff byte"}\n' + launch)
    assert supervise.red_awaits_pass("1") is True

    log.write_bytes(b'{"note": "bad \xff byte"}\n' + launch + verdict)
    assert supervise.red_awaits_pass("1") is False


def test_cli_refuses_a_verify_red_or_verify_green_launch_with_no_check_earlier_pass_marker_exit_2_naming_the_check_and_launching_nothing_2206(
        monkeypatch, tmp_path, supervise, run_cli):
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-2206.md").write_text("# Plan for #2206\n\n- [ ] first step\n")
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    answers = {}
    for name in ("verify-red", "verify-green"):
        code, out, err = run_cli(supervise, [name, str(stub)], cwd=tmp_path,
                                 env={"VERI_ISSUE": "2206", "VERI_STEP": "1"})
        answers[name] = (code, out, "check-earlier" in err, (tmp_path / ".tdd" / f"{name}.exit").read_text().strip())

    assert answers == {name: (2, "", True, "2") for name in ("verify-red", "verify-green")}
    assert not started


def test_cli_refuses_a_verify_red_or_verify_green_launch_whose_only_pass_markers_are_for_another_step_or_for_this_step_at_another_head_2206(
        monkeypatch, tmp_path, supervise, run_cli):
    clean_env(monkeypatch)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-2206.md").write_text("# Plan for #2206\n\n- [ ] first step\n")
    head = "0123456789abcdef0123456789abcdef01234567"
    marker_path = supervise.tests_frozen._pass_marker_path
    (tmp_path / marker_path("another step")).write_text(f"step: another step\nhead: {head}\n")
    (tmp_path / marker_path("first step")).write_text(f"step: first step\nhead: {'f' * 40}\n")
    stub = tmp_path / "claude"
    started = spy_leaf_start(monkeypatch, tmp_path, supervise)

    answers = {}
    for name in ("verify-red", "verify-green"):
        code, out, err = run_cli(supervise, [name, str(stub)], cwd=tmp_path,
                                 env={"VERI_ISSUE": "2206", "VERI_STEP": "1"})
        answers[name] = (code, out, "check-earlier" in err)

    assert answers == {name: (2, "", True) for name in ("verify-red", "verify-green")}
    assert not started
