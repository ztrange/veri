"""In-process cases for veri/stop_run.py, the module stop-run.sh is a shim over."""
import importlib
import os
import subprocess

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


def run_with_conductor(main_tree):
    """<main_tree>/.tdd/wt/5, its .tdd/conductor.pid holding 4242."""
    run = main_tree / ".tdd" / "wt" / "5"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "conductor.pid").write_bytes(b"4242\n")
    return run


def test_main_refuses_no_issue_and_a_non_integer_and_stops_a_live_run_or_answers_3_for_a_dead_one(
        monkeypatch, tmp_path, capsysbinary, stop_run, fake_processes):
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(answering(main_tree_at(tmp_path)))
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
    fake_processes(answering(main_tree_at(tmp_path)))
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
    fake_processes(answering(main_tree_at(main_tree)))
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
        monkeypatch, tmp_path, capsysbinary, stop_run):
    caller = tmp_path / "caller"
    caller.mkdir()
    run_with_conductor(tmp_path)
    monkeypatch.chdir(caller)
    signalled = []
    monkeypatch.setattr(os, "kill", lambda pid, sig: signalled.append((pid, sig)))
    calls = []

    def git_answering(answer):
        def fake_run(args, **kwargs):
            calls.append((list(args), kwargs.get("cwd"), kwargs.get("stderr"), os.getcwd()))
            if isinstance(answer, BaseException):
                raise answer
            return subprocess.CompletedProcess(args, answer[0], answer[1], None)
        return fake_run

    for answer in ((0, b""), (128, b""), FileNotFoundError(2, "No such file or directory", "git")):
        monkeypatch.setattr(subprocess, "run", git_answering(answer))
        calls.clear()

        assert (answer, stop_run.main(["5"])) == (answer, 2)
        assert capsysbinary.readouterr() == (
            b"", "stop-run: no main working tree here — type this inside the repository\n".encode() + USAGE)
        assert calls == [(["git", "worktree", "list", "--porcelain"], None, subprocess.DEVNULL, str(caller))]
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
        (tdd / (name + ".pid")).write_bytes(content.encode() + b"\n")
    (tdd / "d.pid").mkdir()
    (tdd / "j").write_bytes(b"109\n")
    answers = main_tree_at(tmp_path)
    for pid, args in (("4242", b"bash supervise.sh conductor x\n"), ("101", b"bash supervise.sh a develop-red\n"),
                      ("103", b"bash supervise.sh .c x\n"), ("105", b"sleep 60\n"),
                      ("106", b"bash supervise.sh f x\n"), ("107", b"bash supervise.sh g x\n"),
                      (huge, b"bash supervise.sh h x\n"), ("108", b""),
                      ("109", b"bash supervise.sh j x\n")):
        answers[("ps", "-p", pid, "-o", "args=")] = (1 if pid == "108" else 0, args)
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

    assert stop_run.main(["--mode", "now", "5"]) == 0
    assert terms == [101, 106, 107, int(huge)]
    assert capsysbinary.readouterr() == (os.fsencode(run) + b"\n", b"")
    assert (tdd / "stop").read_bytes() == b"now\n"

    for mode in ("at-ledger", "at-leaf"):
        terms.clear()
        calls.clear()
        assert (mode, stop_run.main(["--mode", mode, "5"])) == (mode, 0)
        assert (mode, terms, [c for c in calls if c.startswith("ps ")]) == (mode, [], [])
        assert (tdd / "stop").read_bytes() == mode.encode() + b"\n"
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
        monkeypatch, tmp_path, capsysbinary, stop_run):
    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    outside.mkdir()
    run = repo / ".tdd" / "wt" / "5"
    trees = {str(repo): b"worktree %s\nHEAD abc\n" % os.fsencode(repo), str(outside): b""}

    def fake_run(args, **kwargs):
        if list(args[:2]) == ["ps", "-p"]:
            return subprocess.CompletedProcess(args, 1, "", None)
        if list(args) != ["git", "worktree", "list", "--porcelain"]:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0 if trees[os.getcwd()] else 128, trees[os.getcwd()], None)

    monkeypatch.setattr(subprocess, "run", fake_run)
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
    monkeypatch.setattr(stop_run, "main_working_tree", lambda: os.fsencode(decoy))
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
