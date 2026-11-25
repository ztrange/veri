"""In-process cases for veri/stop_run.py, the module stop-run.sh is a shim over."""
import importlib
import os
from pathlib import Path
import pytest


USAGE = b"usage: stop-run.sh [--mode at-ledger|at-leaf|now] <issue> | --all\n"


@pytest.fixture
def stop_run():
    return importlib.import_module("veri.stop_run")


def answering(answers):
    """An answer for the shared fake: each argv tuple in <answers> answered with (exit code, stdout bytes)."""
    lines = {" ".join(argv): answer for argv, answer in answers.items()}

    def answer(line, **_):
        if line not in lines:
            raise AssertionError("unexpected command: %s" % line)
        code, stdout = lines[line]
        return code, stdout, b""
    return answer


def main_tree_at(main_tree):
    """The answers under which git worktree list --porcelain names <main_tree> first."""
    return {("git", "worktree", "list", "--porcelain"): (0, b"worktree %s\nHEAD abc\n" % os.fsencode(main_tree))}


def conductor_answers(*pids):
    """ps answers making each pid a claude whose parent is run_conductor.py."""
    answers = {}
    for pid in pids:
        parent = pid + 1000000
        answers[("ps", "-o", "command=", "-p", str(pid))] = (0, b"claude -p /tdd 5\n")
        answers[("ps", "-o", "ppid=", "-p", str(pid))] = (0, b"%d\n" % parent)
        answers[("ps", "-o", "command=", "-p", str(parent))] = (0, b"python3 run_conductor.py 5\n")
    return answers


def run_with_conductor(main_tree):
    """<main_tree>/.tdd/wt/5, its .tdd/conductor.pid holding 4242."""
    run = main_tree / ".tdd" / "wt" / "5"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
    return run


def test_main_refuses_no_issue_and_a_non_integer_and_stops_a_live_run_or_answers_3_for_a_dead_one(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(answering({**main_tree_at(tmp_path), **conductor_answers(4242)}))
    live = {"4242": True}

    def fake_kill(pid, sig):
        if not live.get(str(pid)):
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    assert stop_run.main([]) == 2
    assert capsysbinary.readouterr() == (b"", b"stop-run: name an issue, or --all\n" + USAGE)
    assert calls == []

    assert stop_run.main(["ten"]) == 2
    assert capsysbinary.readouterr() == (b"", b"stop-run: <issue> must be a positive integer: 'ten'\n" + USAGE)
    assert calls == []

    run = run_with_conductor(tmp_path)
    assert stop_run.main(["5"]) == 0
    assert capsysbinary.readouterr() == (os.fsencode(run) + b"\n", b"")
    assert (run / ".tdd" / "stop").read_bytes() == b"at-ledger\n"

    (run / ".tdd" / "stop").unlink()
    live["4242"] = False
    assert stop_run.main(["5"]) == 3
    assert capsysbinary.readouterr()[0] == b""
    assert not (run / ".tdd" / "stop").exists()


def test_main_accepts_a_mode_stop_modes_lists_and_writes_it_to_the_runs_stop_file(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    import stop_modes
    monkeypatch.setattr(stop_modes, "STOP_MODES", ("at-ledger", "at-leaf", "now", "at-step"))
    monkeypatch.chdir(tmp_path)
    fake_processes(answering({**main_tree_at(tmp_path), **conductor_answers(4242)}))
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)
    run = run_with_conductor(tmp_path)

    assert stop_run.main(["--mode", "at-step", "5"]) == 0
    assert (run / ".tdd" / "stop").read_bytes() == b"at-step\n"


def test_main_refuses_a_mode_stop_modes_does_not_list_naming_every_mode_it_lists(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    import stop_modes
    monkeypatch.setattr(stop_modes, "STOP_MODES", ("at-ledger", "at-leaf", "now", "at-step"))
    monkeypatch.chdir(tmp_path)
    fake_processes(answering(main_tree_at(tmp_path)))
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)
    run = run_with_conductor(tmp_path)

    assert stop_run.main(["--mode", "bogus", "5"]) == 2
    out, err = capsysbinary.readouterr()
    assert out == b""
    assert err.split(b"\n")[0] == "stop-run: unknown mode — want at-ledger, at-leaf, now or at-step: 'bogus'".encode()
    assert not (run / ".tdd" / "stop").exists()


def test_main_builds_its_usage_line_from_the_modes_stop_modes_lists_when_it_runs(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    import stop_modes
    monkeypatch.setattr(stop_modes, "STOP_MODES", ("at-ledger", "at-leaf", "now", "at-step"))
    monkeypatch.chdir(tmp_path)
    fake_processes(answering(main_tree_at(tmp_path)))

    assert stop_run.main([]) == 2
    out, err = capsysbinary.readouterr()
    assert out == b""
    assert err.rstrip(b"\n").split(b"\n")[-1] == b"usage: stop-run.sh [--mode at-ledger|at-leaf|now|at-step] <issue> | --all"


REFUSALS = [
    (["--mode"], "--mode needs a value — at-ledger, at-leaf or now"),
    (["5", "--all", "--mode"], "--mode needs a value — at-ledger, at-leaf or now"),
    (["--mode", "bogus", "5", "--all"], "unknown mode — want at-ledger, at-leaf or now: 'bogus'"),
    (["--mode", "bogus"], "unknown mode — want at-ledger, at-leaf or now: 'bogus'"),
    (["--mode", "--all", "5"], "unknown mode — want at-ledger, at-leaf or now: '--all'"),
    (["5", "--all"], "name an issue or --all, not both"),
    (["5", "ten"], "<issue> must be a positive integer: 'ten'"),
    (["5", ""], "name an issue, or --all"),
    (["0"], "<issue> must be a positive integer: '0'"),
    (["05"], "<issue> must be a positive integer: '05'"),
    (["+5"], "<issue> must be a positive integer: '+5'"),
    (["5\n"], "<issue> must be a positive integer: '5\n'"),
    (["-x"], "<issue> must be a positive integer: '-x'"),
]


def test_main_refuses_each_bad_argument_list_in_stop_run_sh_order_with_its_message_and_the_usage_line_starting_nothing(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(answering(main_tree_at(tmp_path)))

    for argv, message in REFUSALS:
        assert (argv, stop_run.main(argv)) == (argv, 2)
        assert (argv, capsysbinary.readouterr()) == (argv, (b"", ("stop-run: " + message + "\n").encode() + USAGE))
        assert calls == []

    assert stop_run.main(["ten", "5"]) == 3
    assert capsysbinary.readouterr() == (b"", b"stop-run: no live run for issue 5\n")


def test_main_prints_each_stopped_run_exactly_answers_3_byte_for_byte_and_lists_all_runs_sorted_skipping_files_and_dot_names(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    main_tree = tmp_path / "m[a]i*n?"
    decoy = tmp_path / "maiXnY"
    elsewhere = tmp_path / "elsewhere"
    monkeypatch.chdir(tmp_path)
    fake_processes(answering({**main_tree_at(main_tree), **conductor_answers(8008, 6006, 1212, 7007, 2020)}))
    live = set()

    def fake_kill(pid, sig):
        if pid not in live:
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    def run_at(path, pid):
        (path / ".tdd").mkdir(parents=True)
        (path / ".tdd" / "conductor.pid").write_bytes(b"%d\n" % pid)
        return path

    wt = main_tree / ".tdd" / "wt"
    run_at(wt / "3", 3003)
    run_at(wt / ".8", 8008)
    (wt / "4").write_bytes(b"not a run\n")
    run_at(decoy / ".tdd" / "wt" / "6", 6006)
    live.update({8008, 6006})

    assert stop_run.main(["9"]) == 3
    assert capsysbinary.readouterr() == (b"", b"stop-run: no live run for issue 9\n")
    assert stop_run.main(["3"]) == 3
    assert capsysbinary.readouterr() == (b"", b"stop-run: no live run for issue 3\n")
    assert stop_run.main(["--all"]) == 3
    assert capsysbinary.readouterr() == (b"", b"stop-run: no live run to stop\n")
    assert not (wt / ".8" / ".tdd" / "stop").exists()

    run_at(wt / "12", 1212)
    run_at(wt / "7", 7007)
    run_at(elsewhere, 2020)
    (wt / "20").symlink_to(elsewhere)
    live.update({1212, 7007, 2020})

    assert stop_run.main(["12"]) == 0
    assert capsysbinary.readouterr() == (os.fsencode(wt / "12") + b"\n", b"")

    assert stop_run.main(["--all"]) == 0
    assert capsysbinary.readouterr() == (
        b"".join(os.fsencode(wt / name) + b"\n" for name in ("12", "20", "7")), b"")
    for name in ("12", "20", "7"):
        assert (wt / name / ".tdd" / "stop").read_bytes() == b"at-ledger\n"
    for path in (wt / "3", wt / ".8", decoy / ".tdd" / "wt" / "6"):
        assert not (path / ".tdd" / "stop").exists()


def test_main_all_with_no_tdd_wt_directory_answers_3_no_live_run_to_stop_as_the_unmatched_glob_does(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    monkeypatch.chdir(tmp_path)
    fake_processes(answering(main_tree_at(tmp_path)))

    assert stop_run.main(["--all"]) == 3
    assert capsysbinary.readouterr() == (b"", b"stop-run: no live run to stop\n")


def test_main_takes_a_git_that_cannot_start_exits_non_zero_or_prints_nothing_as_no_main_working_tree(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    caller = tmp_path / "caller"
    caller.mkdir()
    run_with_conductor(tmp_path)
    monkeypatch.chdir(caller)
    signalled = []
    monkeypatch.setattr(os, "kill", lambda pid, sig: signalled.append((pid, sig)))
    working_dirs = []

    def git_answering(answer):
        def respond(line, **kwargs):
            working_dirs.append(os.getcwd())
            if isinstance(answer, BaseException):
                raise answer
            return answer[0], answer[1], b""
        return respond

    for answer in ((0, b""), (128, b""), FileNotFoundError(2, "No such file or directory", "git")):
        working_dirs.clear()
        fake = fake_processes.answers({"git worktree list --porcelain": git_answering(answer)})

        assert (answer, stop_run.main(["5"])) == (answer, 2)
        assert capsysbinary.readouterr() == (
            b"", "stop-run: no main working tree here — type this inside the repository\n".encode() + USAGE)
        assert [(argv, kwargs.get("cwd"), kwargs.get("capture_output"), cwd)
                for (argv, kwargs), cwd in zip(fake.seen, working_dirs)] == [
            (["git", "worktree", "list", "--porcelain"], None, True, str(caller))]
        assert len(fake.seen) == 1
        assert list(tmp_path.rglob("stop")) == []
        assert signalled == []


def test_main_now_terms_only_pids_whose_ps_runs_supervise_sh_of_their_name_ignoring_kill_errors_and_other_modes_signal_nothing(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    import signal
    monkeypatch.chdir(tmp_path)
    run = run_with_conductor(tmp_path)
    tdd = run / ".tdd"
    huge = "99999999999999999999"
    files = {"a": "101", "b": "none", ".c": "103", "e": "105", "f": "106", "g": "107", "h": huge, "i": "108"}
    for name, content in files.items():
        (tdd / (name + ".pid")).write_bytes(content.encode() + b"\nT0\n")
    (tdd / "d.pid").mkdir()
    (tdd / "j").write_bytes(b"109\n")
    answers = {**main_tree_at(tmp_path), **conductor_answers(4242)}
    for pid, args in (("4242", b"bash supervise.sh conductor x\n"), ("101", b"bash supervise.sh a develop-red\n"),
                      ("103", b"bash supervise.sh .c x\n"), ("105", b"sleep 60\n"),
                      ("106", b"bash supervise.sh f x\n"), ("107", b"bash supervise.sh g x\n"),
                      (huge, b"bash supervise.sh h x\n"), ("108", b""),
                      ("109", b"bash supervise.sh j x\n")):
        answers[("ps", "-p", pid, "-o", "args=")] = (1 if pid == "108" else 0, args)
        answers[("ps", "-o", "lstart=", "-p", pid)] = (0, b"T0\n")
    calls = fake_processes(answering(answers))
    raises = {106: ProcessLookupError(3, "No such process"), 107: PermissionError(1, "Operation not permitted"),
              int(huge): OverflowError("signed integer is greater than maximum")}
    terms = []

    def fake_kill(pid, sig):
        if sig == signal.SIGTERM:
            terms.append(pid)
            if pid in raises:
                raise raises[pid]
        elif pid != 4242:
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    assert stop_run.main(["--mode", "now", "5"]) == 2
    assert terms == [101, 106, 107, int(huge)]
    out, err = capsysbinary.readouterr()
    assert out == os.fsencode(run) + b"\n"
    bare = err.replace(os.fsencode(run), b"")
    assert (b"107" in bare, os.fsencode(run) in err, b"101" in bare, b"106" in bare) == (True, True, False, False)
    assert (tdd / "stop").read_bytes() == b"now\n"

    for mode in ("at-ledger", "at-leaf"):
        terms.clear()
        calls.clear()
        assert (mode, stop_run.main(["--mode", mode, "5"])) == (mode, 0)
        assert (mode, terms, [c for c in calls if c.startswith("ps ")]) == (mode, [], [])
        assert (tdd / "stop").read_bytes() == mode.encode() + b"\n"
        capsysbinary.readouterr()


def test_2249_main_in_at_ledger_and_at_leaf_asks_pid_file_live_conductor_nothing_and_runs_no_ps_yet_answers_3_for_a_dead_pid(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    import pid_file
    monkeypatch.chdir(tmp_path)
    run = run_with_conductor(tmp_path)
    calls = fake_processes(answering(main_tree_at(tmp_path)))
    asked = []
    real = pid_file.live_conductor
    monkeypatch.setattr(pid_file, "live_conductor", lambda path: asked.append(path) or real(path))
    alive = {4242}

    def fake_kill(pid, sig):
        if pid not in alive:
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    for mode in ("at-ledger", "at-leaf"):
        for argv in (["5"], ["--all"]):
            asked.clear()
            calls.clear()
            (run / ".tdd" / "stop").unlink(missing_ok=True)
            assert (mode, argv, stop_run.main(["--mode", mode, *argv])) == (mode, argv, 0)
            assert (mode, argv, asked, [c for c in calls if c.startswith("ps ")]) == (mode, argv, [], [])
            assert (run / ".tdd" / "stop").read_bytes() == mode.encode() + b"\n"
            capsysbinary.readouterr()
        alive.clear()
        (run / ".tdd" / "stop").unlink()
        assert (mode, stop_run.main(["--mode", mode, "5"])) == (mode, 3)
        assert not (run / ".tdd" / "stop").exists()
        alive.add(4242)
        capsysbinary.readouterr()


def test_2249_main_in_now_asks_pid_file_live_conductor_for_the_run_in_one_issue_and_in_all_mode(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    import pid_file
    monkeypatch.chdir(tmp_path)
    run = run_with_conductor(tmp_path)
    fake_processes(answering({**main_tree_at(tmp_path), **conductor_answers(4242)}))
    asked = []
    real = pid_file.live_conductor
    monkeypatch.setattr(pid_file, "live_conductor", lambda path: asked.append(path) or real(path))
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)

    for argv in (["5"], ["--all"]):
        asked.clear()
        assert (argv, stop_run.main(["--mode", "now", *argv])) == (argv, 0)
        assert (argv, [os.fsencode(a) for a in asked]) == (argv, [os.fsencode(run)])
        capsysbinary.readouterr()


def test_main_passes_non_utf8_bytes_in_an_argument_through_to_the_refusal_unchanged(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(answering(main_tree_at(tmp_path)))
    raw = b"\xff\xfeb\xe9"
    arg = os.fsdecode(raw)

    assert stop_run.main(["--mode", arg, "5"]) == 2
    assert capsysbinary.readouterr() == (
        b"", "stop-run: unknown mode — want at-ledger, at-leaf or now: '".encode() + raw + b"'\n" + USAGE)

    assert stop_run.main([arg]) == 2
    assert capsysbinary.readouterr() == (
        b"", b"stop-run: <issue> must be a positive integer: '" + raw + b"'\n" + USAGE)
    assert calls == []


def test_main_answers_as_stop_run_test_sh_s_refusal_write_overwrite_all_no_main_tree_and_pid_0_cases_do(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    outside.mkdir()
    run = repo / ".tdd" / "wt" / "5"
    trees = {str(repo): b"worktree %s\nHEAD abc\n" % os.fsencode(repo), str(outside): b""}
    held = conductor_answers(4242, 7007)

    def worktrees(line, **_):
        return (0 if trees[os.getcwd()] else 128), trees[os.getcwd()], b""

    fake_processes.answers({
        **{" ".join(argv): (0, answer[1], b"") for argv, answer in held.items()},
        "ps -p": (1, b"", b""),
        "git worktree list --porcelain": worktrees,
    })
    live = {4242, 7007}
    signals = []

    def fake_kill(pid, sig):
        if sig != 0:
            signals.append((pid, sig))
        if pid not in live:
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    def conductor(path, content):
        (path / ".tdd").mkdir(parents=True, exist_ok=True)
        (path / ".tdd" / "conductor.pid").write_bytes(content + b"\n")

    conductor(run, b"4242")
    (run / ".tdd" / "develop-red.pid").write_bytes(b"4343\n")
    monkeypatch.chdir(repo)

    for argv in (["--mode", "bogus", "5"], ["--mode", "now", "5", "--all"], [], ["--mode", "now", "five"], ["--mode"]):
        assert (argv, stop_run.main(argv)) == (argv, 2)
        out, err = capsysbinary.readouterr()
        assert (argv, out, err.startswith(b"stop-run: ")) == (argv, b"", True)
        assert not (run / ".tdd" / "stop").exists()
        assert signals == []

    assert stop_run.main(["5"]) == 0
    assert (run / ".tdd" / "stop").read_bytes() == b"at-ledger\n"
    capsysbinary.readouterr()

    (run / ".tdd" / "stop").write_bytes(b"at-leaf\n")
    assert stop_run.main(["--mode", "now", "5"]) == 0
    assert (run / ".tdd" / "stop").read_bytes() == b"now\n"
    capsysbinary.readouterr()

    (run / ".tdd" / "stop").unlink()
    conductor(repo / ".tdd" / "wt" / "7", b"7007")
    conductor(repo / ".tdd" / "wt" / "9", b"9009")
    signals.clear()
    assert stop_run.main(["--mode", "at-leaf", "--all"]) == 0
    out, err = capsysbinary.readouterr()
    assert sorted(os.path.basename(line) for line in out.decode().splitlines()) == ["5", "7"]
    for name in ("5", "7"):
        assert (repo / ".tdd" / "wt" / name / ".tdd" / "stop").read_bytes() == b"at-leaf\n"
    assert not (repo / ".tdd" / "wt" / "9" / ".tdd" / "stop").exists()
    assert signals == []

    (run / ".tdd" / "stop").unlink()
    monkeypatch.chdir(outside)
    assert stop_run.main(["--mode", "now", "5"]) == 2
    out, err = capsysbinary.readouterr()
    assert (out, err.startswith(b"stop-run: ")) == (b"", True)
    assert not (run / ".tdd" / "stop").exists()
    assert signals == []

    monkeypatch.chdir(repo)
    live.add(0)
    for zero in ("0", "00"):
        zero_run = repo / ".tdd" / "wt" / ("1" + zero)
        conductor(zero_run, zero.encode())
        assert (zero, stop_run.main(["1" + zero])) == (zero, 3)
        assert not (zero_run / ".tdd" / "stop").exists()
        capsysbinary.readouterr()
    assert signals == []


def test_main_that_resolves_a_main_working_tree_outside_the_fixture_tree_fails_writing_no_stop_and_signalling_nothing_1158(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    import signal
    fixture = tmp_path / "fixture"
    repo = fixture / "repo"
    run_with_conductor(repo)
    decoy = tmp_path / "decoy"
    decoy_run = run_with_conductor(decoy)
    (decoy_run / ".tdd" / "develop-red.pid").write_bytes(b"4343\n")
    monkeypatch.chdir(repo)
    answers = {("ps", "-p", "4343", "-o", "args="): (0, b"bash supervise.sh develop-red 5\n")}
    fake_processes(answering(answers))
    monkeypatch.setattr(stop_run.run_dir, "main_tree", lambda **_: str(decoy))
    terms = []

    def fake_kill(pid, sig):
        if sig == signal.SIGTERM:
            terms.append(pid)
        elif pid not in (4242, 4343):
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    for argv in (["--mode", "now", "5"], ["--mode", "now", "--all"]):
        code = stop_run.main(argv)
        out, err = capsysbinary.readouterr()
        assert (argv, code != 0, os.fsencode(decoy) in out) == (argv, True, False)
        assert (argv, list(decoy.rglob("stop"))) == (argv, [])
        assert (argv, terms) == (argv, [])


@pytest.fixture
def started(request):
    """Processes the case starts, each killed and reaped by the pid recorded at its start."""
    procs = []
    yield procs
    for proc in procs:
        proc.kill()
    for proc in procs:
        proc.wait()


def fake_lstart(monkeypatch, stop_run, started="T0"):
    """pid_file's ps lstart read answers <started> for any pid; its other ps reads stay as they are."""
    real = stop_run.pid_file.ps_field
    monkeypatch.setattr(stop_run.pid_file, "ps_field", lambda field, pid: started if field == "lstart" else real(field, pid))


def test_a_symlink_beside_no_scripts_still_finds_the_real_scripts_directory(tmp_path, monkeypatch, stop_run):
    import importlib.util
    real = Path(stop_run.__file__).resolve()
    farm = tmp_path.resolve() / "farm" / "veri"
    farm.mkdir(parents=True)
    os.symlink(real, farm / "stop_run.py")
    spec = importlib.util.spec_from_file_location("symlinked_stop_run", farm / "stop_run.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    monkeypatch.chdir(real.parent.parent)

    assert loaded.inside_own_scripts() is True


def test_3375_stop_leaves_waits_the_kill_grace_the_env_names_between_the_term_and_the_kill_of_a_detached_group_and_by_default_waits_a_positive_time(
        monkeypatch, tmp_path, stop_run):
    import signal
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "fulltier.pid").write_text("777\nT0\n")
    events = []
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: False)
    monkeypatch.setattr(stop_run.pid_file, "detached", lambda pid: True)
    fake_lstart(monkeypatch, stop_run)
    monkeypatch.setattr(os, "killpg", lambda group, sig: events.append(("killpg", group, sig)))
    monkeypatch.setattr(stop_run.time, "sleep", lambda seconds: events.append(("sleep", seconds)))

    monkeypatch.setenv("VERI_STOP_KILL_GRACE", "7")
    stop_run.stop_leaves(str(tmp_path))

    assert events == [("killpg", 777, signal.SIGTERM), ("sleep", 7.0), ("killpg", 777, signal.SIGKILL)]

    events.clear()
    monkeypatch.delenv("VERI_STOP_KILL_GRACE")
    stop_run.stop_leaves(str(tmp_path))

    assert [e[0] for e in events] == ["killpg", "sleep", "killpg"]
    assert events[1][1] > 0


def test_3375_stop_run_mode_now_exits_2_naming_the_pid_and_the_run_when_a_detached_group_sent_kill_is_still_alive_and_0_when_the_group_dies_on_kill(
        monkeypatch, tmp_path, capsys, stop_run):
    import signal
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "fulltier.pid").write_text("777\nT0\n")
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: False)
    monkeypatch.setattr(stop_run.pid_file, "detached", lambda pid: True)
    fake_lstart(monkeypatch, stop_run)
    monkeypatch.setattr(stop_run.time, "sleep", lambda seconds: None)

    def group_that(dies_on_kill):
        alive = [True]

        def killpg(group, sig):
            if sig == signal.SIGKILL and dies_on_kill:
                alive[0] = False
            elif sig == 0 and not alive[0]:
                raise ProcessLookupError
        return killpg

    monkeypatch.setattr(os, "killpg", group_that(dies_on_kill=True))
    assert stop_run.stop_run(str(run), "now") == 0
    capsys.readouterr()

    monkeypatch.setattr(os, "killpg", group_that(dies_on_kill=False))
    code = stop_run.stop_run(str(run), "now")
    err = capsys.readouterr().err

    assert code == 2
    assert "777" in err and str(run) in err


def test_3375_stop_run_mode_now_exits_0_when_a_member_of_the_detached_group_is_alive_at_the_first_probes_after_kill_and_gone_at_a_later_probe(
        monkeypatch, tmp_path, capsys, stop_run):
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "fulltier.pid").write_text("777\nT0\n")
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: False)
    monkeypatch.setattr(stop_run.pid_file, "detached", lambda pid: True)
    fake_lstart(monkeypatch, stop_run)
    monkeypatch.setattr(stop_run.time, "sleep", lambda seconds: None)
    probes = []

    def killpg(group, sig):
        if sig == 0:
            probes.append(group)
            if len(probes) > 3:
                raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "killpg", killpg)

    code = stop_run.stop_run(str(run), "now")
    err = capsys.readouterr().err

    assert code == 0, err


def test_3375_stop_run_mode_now_exits_2_naming_the_pid_and_the_run_when_the_survivor_probe_of_a_detached_group_is_refused(
        monkeypatch, tmp_path, capsys, stop_run):
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "fulltier.pid").write_text("777\nT0\n")
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: False)
    monkeypatch.setattr(stop_run.pid_file, "detached", lambda pid: True)
    fake_lstart(monkeypatch, stop_run)
    monkeypatch.setattr(stop_run.time, "sleep", lambda seconds: None)

    def killpg(group, sig):
        if sig == 0:
            raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(os, "killpg", killpg)

    code = stop_run.stop_run(str(run), "now")
    err = capsys.readouterr().err

    assert (run / ".tdd" / "stop").read_text() == "now\n"
    assert code == 2
    assert "777" in err and str(run) in err


def test_3375_stop_run_mode_now_exits_2_naming_the_pid_and_the_run_when_the_kill_sent_a_detached_group_is_refused(
        monkeypatch, tmp_path, capsys, stop_run):
    import signal
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "fulltier.pid").write_text("777\nT0\n")
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: False)
    monkeypatch.setattr(stop_run.pid_file, "detached", lambda pid: True)
    fake_lstart(monkeypatch, stop_run)
    monkeypatch.setattr(stop_run.time, "sleep", lambda seconds: None)

    def killpg(group, sig):
        if sig == signal.SIGKILL:
            raise PermissionError(1, "Operation not permitted")
        if sig == 0:
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "killpg", killpg)

    code = stop_run.stop_run(str(run), "now")
    err = capsys.readouterr().err

    assert (run / ".tdd" / "stop").read_text() == "now\n"
    assert code == 2
    assert "777" in err and str(run) in err


def test_stop_run_mode_now_signals_no_leaf_whose_pid_file_records_no_start_time_naming_each_such_file_on_stderr_and_still_exits_0(
        monkeypatch, tmp_path, capsys, stop_run):
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    supervisor_file, detached_file = run / ".tdd" / "develop-red.pid", run / ".tdd" / "fulltier.pid"
    supervisor_file.write_text("101\n")
    detached_file.write_text("777\n")
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: pid == "101")
    monkeypatch.setattr(stop_run.pid_file, "detached", lambda pid: pid == "777")
    fake_lstart(monkeypatch, stop_run)
    monkeypatch.setattr(stop_run.time, "sleep", lambda seconds: None)
    signalled = []
    monkeypatch.setattr(os, "kill", lambda pid, sig: signalled.append(("kill", pid, sig)))
    monkeypatch.setattr(os, "killpg", lambda group, sig: signalled.append(("killpg", group, sig)))

    code = stop_run.stop_run(str(run), "now")
    lines = capsys.readouterr().err.splitlines()

    assert signalled == []
    assert code == 0
    assert [str(supervisor_file) in lines[0], str(detached_file) in lines[1], len(lines)] == [True, True, 2]


def test_stop_run_mode_now_does_not_term_a_supervisor_whose_pid_file_start_time_differs_from_the_live_process_s_and_exits_0_silently(
        monkeypatch, tmp_path, capsys, stop_run):
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "develop-red.pid").write_text("101\nT0\n")
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: True)
    fake_lstart(monkeypatch, stop_run, started="T1")
    signalled = []
    monkeypatch.setattr(os, "kill", lambda pid, sig: signalled.append((pid, sig)))

    code = stop_run.stop_run(str(run), "now")

    assert signalled == []
    assert (code, capsys.readouterr().err) == (0, "")


def test_stop_leaves_waits_the_default_kill_grace_when_veri_stop_kill_grace_is_set_but_empty(monkeypatch, tmp_path, stop_run):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "fulltier.pid").write_text("777\nT0\n")
    events = []
    monkeypatch.setattr(stop_run.pid_file, "supervising", lambda pid, name: False)
    monkeypatch.setattr(stop_run.pid_file, "detached", lambda pid: True)
    fake_lstart(monkeypatch, stop_run)
    monkeypatch.setattr(os, "killpg", lambda group, sig: events.append(("killpg", group)))
    monkeypatch.setattr(stop_run.time, "sleep", lambda seconds: events.append(("sleep", seconds)))
    monkeypatch.setenv("VERI_STOP_KILL_GRACE", "")

    stop_run.stop_leaves(str(tmp_path))

    assert events == [("killpg", 777), ("sleep", 5.0), ("killpg", 777)]
