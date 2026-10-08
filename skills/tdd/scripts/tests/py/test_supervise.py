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


def test_main_marks_a_watched_names_launch_and_exit_through_event_sh_under_its_role_and_none_for_a_verdict_or_refused_name_whose_failure_changes_nothing(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: 5000.0)
    event_sh = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(supervise.__file__))), "event.sh")

    def run_one(label, name, event_rc, script, **env):
        work = tmp_path / label
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, **env)
        fake_leaf_launch(monkeypatch)
        launching, running = subprocess.Popen, subprocess.run
        events = []

        def is_event(args):
            return event_sh in [str(a) for a in args]

        def record(args, kwargs):
            seen = kwargs.get("env")
            seen = dict(os.environ if seen is None else seen)
            events.append(([str(a) for a in args], seen.get("VERI_ISSUE"), seen.get("VERI_STEP")))

        def popen(args, *a, **kwargs):
            if is_event(args):
                record(args, kwargs)
                return launching(["sh", "-c", f"exit {event_rc}"])
            return launching(args, *a, **kwargs)

        def run(args, *a, **kwargs):
            if is_event(args):
                record(args, kwargs)
                if kwargs.get("check") and event_rc:
                    raise subprocess.CalledProcessError(event_rc, args)
                return subprocess.CompletedProcess(args, event_rc, "", "")
            return running(args, *a, **kwargs)

        monkeypatch.setattr(subprocess, "Popen", popen)
        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        code = supervise.main([name, "sh", "-c", script])
        out, err = capsysbinary.readouterr()
        exit_record = (work / ".tdd" / f"{name}.exit").read_bytes()
        role_lines = [line for line in err.splitlines() if line.startswith(b"leaf-role:")]
        return code, out, exit_record, events, role_lines

    role = ["env", "VERI_ACTOR=developer", "VERI_PHASE=red", "VERI_ATTEMPT=1", event_sh]
    marked = [
        (role + ["launch", "name=develop-red", "cmd=sh -c printf 'leaf out\\n'; exit 1", "model=opus-x"],
         "1073", "4"),
        (role + ["exit", "status=1", "secs=0"], "1073", "4"),
    ]
    leaf = "printf 'leaf out\\n'; exit 1"
    env = {"VERI_ISSUE": "1073", "VERI_STEP": "4", "VERI_MODEL": "opus-x", "VERI_TIMEOUT": "900"}
    assert run_one("ok", "develop-red", 0, leaf, **env) == (1, b"leaf out\n", b"1\n", marked, [])
    assert run_one("failing", "develop-red", 1, leaf, **env) == (1, b"leaf out\n", b"1\n", marked, [])

    assert run_one("verdict", "verdict-plan", 0, leaf, **env) == (1, b"leaf out\n", b"1\n", [], [])

    code, out, exit_record, events, role_lines = run_one("bogus", "bogus-x", 0, "printf 'leaf out\\n'", **env)
    diagnostic = b"leaf-role: leaf name 'bogus-x' has an unknown leading word (want develop-*|revise-*|verify-*|conductor-*)"
    assert (code, out, exit_record, events, role_lines) == (0, b"leaf out\n", b"0\n", [], [diagnostic, diagnostic])


def test_main_resolves_the_model_in_process_marks_it_on_the_launch_and_hands_the_leaf_its_own_environment_plus_veri_leaf_model_and_veri_skill_commit(
        monkeypatch, tmp_path, capsysbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: 5000.0)
    monkeypatch.setenv("VERI_LEAF_MODEL", "ambient")
    monkeypatch.setenv("VERI_SKILL_COMMIT", "ambient")
    here = os.path.dirname(os.path.dirname(os.path.abspath(supervise.__file__)))
    event_sh = os.path.join(here, "event.sh")
    sha = "0123456789abcdef0123456789abcdef01234567"
    whitespace = b"leaf-model: model 'opus x' contains whitespace (a model id or alias is one word)"

    def run_one(label, git_ok, **env):
        work = tmp_path / label
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="900", **env)
        fake_leaf_launch(monkeypatch)
        launching = subprocess.Popen
        launch_models, leaf_envs = [], []

        def git(args, kwargs):
            if list(args) == ["git", "-C", here, "rev-parse", "HEAD"] and git_ok:
                return 0, as_asked(f"{sha}\n", kwargs)
            return 128, as_asked("", kwargs)

        def run(args, *a, **kwargs):
            args = [str(x) for x in args]
            if event_sh in args:
                if "launch" in args:
                    launch_models.append([f for f in args if f.startswith("model=")])
                return subprocess.CompletedProcess(args, 0, "", "")
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
        before = dict(os.environ)
        code = supervise.main(["develop-red", "sh", "-c", "exit 0"])
        _, err = capsysbinary.readouterr()
        handed = ("VERI_LEAF_MODEL", "VERI_SKILL_COMMIT")
        added = [{**{k: v for k, v in e.items() if k not in before or before[k] != v},
                  **{k: e.get(k) for k in handed}} for e in leaf_envs]
        dropped = [sorted(k for k in before if k not in e) for e in leaf_envs]
        return code, launch_models, added, dropped, err.splitlines().count(whitespace)

    def leaf(model, commit):
        return [{"VERI_LEAF_MODEL": model, "VERI_SKILL_COMMIT": commit}]

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
        "chosen": (0, [["model=opus-x"]], leaf("opus-x", sha), [[]], 0),
        "none": (0, [["model="]], leaf("", sha), [[]], 0),
        "whitespace": (0, [["model="]], leaf("", sha), [[]], 1),
        "dash-n": (0, [["model="]], leaf("", sha), [[]], 0),
        "dash-e": (0, [["model="]], leaf("", sha), [[]], 0),
        "dash-E": (0, [["model="]], leaf("", sha), [[]], 0),
        "git-beats-inherited": (0, [["model="]], leaf("", sha), [[]], 0),
        "inherited": (0, [["model="]], leaf("", "inherited"), [[]], 0),
        "inherited-empty": (0, [["model="]], leaf("", "unknown"), [[]], 0),
        "unknown": (0, [["model="]], leaf("", "unknown"), [[]], 0),
    }


def test_main_runs_harvest_usage_sh_once_for_a_watched_name_onto_its_stderr_before_the_status_line_a_failing_one_changing_nothing_and_none_for_a_verdict_name(
        monkeypatch, tmp_path, capfdbinary, supervise):
    import signal
    import time
    monkeypatch.setattr(signal, "signal", lambda *_: None)
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(time, "clock_gettime", lambda *_: 5000.0)
    here = os.path.dirname(os.path.dirname(os.path.abspath(supervise.__file__)))
    harvest_sh = os.path.join(here, "harvest-usage.sh")
    harvester = "printf 'harvest out\\n'; printf 'harvest err\\n' >&2; exit 1"
    real_popen = subprocess.Popen

    def run_one(name):
        work = tmp_path / name
        work.mkdir()
        monkeypatch.chdir(work)
        clean_env(monkeypatch, VERI_TIMEOUT="900")
        fake_leaf_launch(monkeypatch)
        launching, running = subprocess.Popen, subprocess.run
        harvests = []

        def as_harvester(args, kwargs):
            harvests.append([str(a) for a in args])
            passed = {k: kwargs[k] for k in ("stdout", "stderr") if k in kwargs}
            return ["sh", "-c", harvester], passed

        def popen(args, *a, **kwargs):
            if harvest_sh in [str(x) for x in args]:
                cmd, passed = as_harvester(args, kwargs)
                return real_popen(cmd, **passed)
            if os.path.join(here, "event.sh") in [str(x) for x in args]:
                return launching(["true"])
            return launching(args, *a, **kwargs)

        def run(args, *a, **kwargs):
            if harvest_sh in [str(x) for x in args]:
                cmd, passed = as_harvester(args, kwargs)
                code = real_popen(cmd, **passed).wait()
                if kwargs.get("check") and code:
                    raise subprocess.CalledProcessError(code, args)
                return subprocess.CompletedProcess(args, code, None, None)
            if os.path.join(here, "event.sh") in [str(x) for x in args]:
                return subprocess.CompletedProcess(args, 0, "", "")
            return running(args, *a, **kwargs)

        monkeypatch.setattr(subprocess, "Popen", popen)
        monkeypatch.setattr(subprocess, "run", run)
        monkeypatch.setattr(subprocess, "call", lambda args, *a, **k: run(args, *a, **k).returncode)
        monkeypatch.setattr(subprocess, "check_call", lambda args, *a, **k: run(args, *a, check=True, **k).returncode)
        code = supervise.main([name, "sh", "-c", "printf 'leaf out\\n'"])
        out, err = capfdbinary.readouterr()
        lines = [line for line in err.splitlines()
                 if line.startswith((b"harvest ", b"harvest-usage.sh:", b"supervise["))]
        return code, out, (work / ".tdd" / f"{name}.exit").read_bytes(), harvests, lines

    assert run_one("develop-red") == (
        0, b"leaf out\n", b"0\n", [[harvest_sh, "develop-red"]],
        [b"harvest out", b"harvest err", b"supervise[develop-red]: success"])
    assert run_one("verdict-red") == (
        0, b"leaf out\n", b"0\n", [], [b"supervise[verdict-red]: success"])


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
    skill = (here.parents[0] / "SKILL.md").read_text()
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

    class Leaf:
        pid = 4242
        returncode = None
        args = []

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            return self.returncode

    leaf = Leaf()
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

        class Leaf:
            pid = 4242
            returncode = None
            args = []

            def poll(self):
                return self.returncode

            def wait(self, timeout=None):
                return self.returncode

        leaf = Leaf()

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
        (2, [(1009, "group", 4242, term)], ["supervise[develop-red]: killed-stuck — no heartbeat for 9s (window 010s)"]),
        []]

    broken = {value: watch("develop-red", value, lambda s, w: (0, "1000\n") if s == "-c" else fails, 100, rc_after=3)
              for value in ("08", "1.5")}
    assert {value: (r["code"], r["kills"], r["status"], len([l for l in r["err"] if value.encode() in l]))
            for value, r in broken.items()} == {
        "08": (0, [], ["supervise[develop-red]: success"], 3),
        "1.5": (0, [], ["supervise[develop-red]: success"], 3)}

    word = watch("develop-red", "abc", lambda s, w: (0, "1000\n") if s == "-c" else fails, 100)
    assert (word["code"], word["sleeps"], word["kills"], word["exit"]) == (1, 0, [], None)


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

        class Leaf:
            pid = 4242
            returncode = None
            args = []

            def poll(self):
                return self.returncode

            def wait(self, timeout=None):
                return self.returncode

        leaf = Leaf()

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
        (2, [(8, 8, term)], ["supervise[develop-red]: killed-stuck — hard timeout 010s exceeded"], b"2\n"),
        (2, [(8, 8, term)], ["supervise[develop-red]: killed-stuck — hard timeout 010s exceeded"], b"2\n"),
        (2, [(900, 900, term)], ["supervise[develop-red]: killed-stuck — hard timeout 900s exceeded"], b"2\n"),
        (2, [(11, 11, term)], ["supervise[develop-red]: killed-stuck — hard timeout 11s exceeded"], b"2\n")]
    assert [(r["clocks"], r["awake_runs"] > 0) for r in fired[:3]] == [
        ({uptime_raw}, False), ({time.CLOCK_MONOTONIC}, False), (set(), True)]

    suspended = watch({"VERI_HEARTBEAT": "5", "VERI_TIMEOUT": "100000"}, 1, jump=100)
    assert (suspended["code"], suspended["kills"], suspended["status"]) == (
        2, [(106, 6, term)], ["supervise[develop-red]: killed-stuck — no heartbeat for 6s (window 5s)"])

    broken = {value: watch({**quiet, "VERI_TIMEOUT": value}, 100, rc_after=3) for value in ("08", "1.5")}
    assert {value: (r["code"], r["kills"], r["status"], len([l for l in r["err"] if value.encode() in l]))
            for value, r in broken.items()} == {
        "08": (0, [], ["supervise[develop-red]: success"], 3),
        "1.5": (0, [], ["supervise[develop-red]: success"], 3)}

    word = watch({**quiet, "VERI_TIMEOUT": "abc"}, 100)
    assert (word["code"], word["sleeps"], word["kills"], word["exit"]) == (1, 0, [], None)


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

        class Leaf:
            pid = 4242
            returncode = None
            args = []

            def poll(self):
                events.append(("poll",))
                return self.returncode

            def wait(self, timeout=None):
                return self.returncode

        leaf = Leaf()

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
