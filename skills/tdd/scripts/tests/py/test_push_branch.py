"""In-process cases for veri/push_branch.py, the module push-branch.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def push_branch():
    return importlib.import_module("veri.push_branch")


def merged(answer):
    """<answer>(line) -> (exit code, merged output), as the shared fake's answer."""
    return lambda line, **_: (*answer(line), "")


def test_main_with_one_retry_runs_a_failed_push_to_its_push_failed_event(monkeypatch, capsys, push_branch, fake_processes):
    def answer(line):
        if line == "git push --set-upstream origin HEAD":
            return 128, "fatal: unable to access origin\n"
        return 0, ""

    calls = fake_processes(merged(answer))
    monkeypatch.setenv("VERI_PUSH_RETRIES", "1")
    monkeypatch.delenv("VERI_PUSH_BACKOFF", raising=False)

    code = push_branch.main([])

    captured = capsys.readouterr()
    assert calls == [
        "git push --set-upstream origin HEAD",
        "sleep 2",
        "git push --set-upstream origin HEAD",
        "event.sh push-failed error=fatal: unable to access origin attempts=2",
    ]
    assert (code, captured.out, captured.err) == (
        0, "", "push-branch.sh: push failed after 2 attempts; the branch is not on the remote\n")


def test_main_refuses_a_bogus_argument_with_its_usage_and_no_process(monkeypatch, capsys, push_branch, fake_processes):
    calls = fake_processes(lambda line, **_: (0, "", ""))
    monkeypatch.delenv("VERI_PUSH_RETRIES", raising=False)
    monkeypatch.delenv("VERI_PUSH_BACKOFF", raising=False)

    code = push_branch.main(["--bogus"])

    captured = capsys.readouterr()
    assert calls == []
    assert (code, captured.out, captured.err) == (
        2, "",
        "push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, got '--bogus'\n"
        "usage: push-branch.sh [--force-with-lease=<branch>:<sha>]\n")


def test_main_pushes_a_valid_lease_ahead_of_set_upstream(monkeypatch, capsys, push_branch, fake_processes):
    calls = fake_processes(lambda line, **_: (0, "", ""))
    monkeypatch.setenv("VERI_PUSH_RETRIES", "0")
    monkeypatch.delenv("VERI_PUSH_BACKOFF", raising=False)

    push_branch.main(["--force-with-lease=b:abc1234"])

    assert calls[:1] == ["git push --force-with-lease=b:abc1234 --set-upstream origin HEAD"]


def test_main_reports_a_non_fast_forward_rejection_once_and_records_push_rejected(monkeypatch, capsys, push_branch, fake_processes):
    rejected = " ! [rejected]        HEAD -> feature (non-fast-forward)"
    stderr_at_event = []

    def answer(line):
        if line == "git push --set-upstream origin HEAD":
            return 1, rejected + "\n"
        if line == "git rev-parse --abbrev-ref HEAD":
            return 0, "feature\n"
        if line == "git ls-remote origin refs/heads/feature":
            return 0, "abc1234def\trefs/heads/feature\n"
        if line.startswith("event.sh "):
            stderr_at_event.append(capsys.readouterr().err)
        return 0, ""

    calls = fake_processes(merged(answer))
    monkeypatch.delenv("VERI_PUSH_RETRIES", raising=False)
    monkeypatch.delenv("VERI_PUSH_BACKOFF", raising=False)

    code = push_branch.main([])

    captured = capsys.readouterr()
    assert calls == [
        "git push --set-upstream origin HEAD",
        "git rev-parse --abbrev-ref HEAD",
        "git ls-remote origin refs/heads/feature",
        f"event.sh push-rejected remote_sha=abc1234def error={rejected}",
    ]
    assert (code, captured.out, stderr_at_event, captured.err) == (
        1, "", ["push rejected (non-fast-forward): origin/feature is at abc1234def\n"], "")


def test_main_reads_retries_and_backoff_with_leading_zeros_as_decimal_and_records_push_failed_issue_776(monkeypatch, capsys, push_branch, fake_processes):
    push = "git push --set-upstream origin HEAD"
    event = "event.sh push-failed error=fatal: unable to access origin attempts="

    def failing(line):
        return (128, "fatal: unable to access origin\n") if line == push else (0, "")

    def run_with(retries, backoff):
        calls = fake_processes(merged(failing))
        monkeypatch.setenv("VERI_PUSH_RETRIES", retries)
        monkeypatch.setenv("VERI_PUSH_BACKOFF", backoff)
        code = push_branch.main([])
        sleeps = [line for line in calls if line.startswith("sleep ")]
        return code, calls.count(push), sleeps[1:], calls[-1:], capsys.readouterr().err

    failed = "push-branch.sh: push failed after {} attempts; the branch is not on the remote\n"
    observed = (run_with("007", "0"), run_with("08", "0"), run_with("2", "09"))

    assert observed == (
        (0, 8, ["sleep 0"] * 6, [event + "8"], failed.format(8)),
        (0, 9, ["sleep 0"] * 7, [event + "9"], failed.format(9)),
        (0, 3, ["sleep 18"], [event + "3"], failed.format(3)),
    )


def test_main_lands_a_lease_push_silently_and_records_the_last_attempts_merged_output(monkeypatch, capsys, push_branch, fake_processes):
    def run_with(argv, answers, retries="0"):
        calls = fake_processes(lambda line, **_: answers[line].pop(0) if line in answers else (0, "", ""))
        monkeypatch.setenv("VERI_PUSH_RETRIES", retries)
        monkeypatch.setenv("VERI_PUSH_BACKOFF", "0")
        code = push_branch.main(argv)
        captured = capsys.readouterr()
        return code, calls, captured.out, captured.err

    lease = "--force-with-lease=feature:abc1234"
    leased_push = f"git push {lease} --set-upstream origin HEAD"
    push = "git push --set-upstream origin HEAD"
    remote = {
        "git rev-parse --abbrev-ref HEAD": [(0, "feature\n", "")],
        "git ls-remote origin refs/heads/feature": [(0, "def5678\trefs/heads/feature\n", "")],
    }
    fetch_first = " ! [rejected]  HEAD -> feature (fetch first)"
    stale_info = " ! [rejected]  HEAD -> feature (stale info)"

    observed = (
        run_with([lease], {leased_push: [(0, "To origin\n", "  new branch \n")]}),
        run_with([], {push: [(1, "", "  To origin\n" + fetch_first + "  \n\n")], **remote})[1][-1],
        run_with([lease], {leased_push: [(1, "", stale_info + "\n")],
                           "git rev-parse --abbrev-ref HEAD": [(0, "feature\n", "")],
                           "git ls-remote origin refs/heads/feature": [(0, "def5678\trefs/heads/feature\n", "")]})[::3],
        run_with([], {push: [(128, "first out\n", "first err\n"),
                             (128, "  last out \n", "  last err \n\n")]}, retries="1")[1][-1],
    )

    assert observed == (
        (0, [leased_push], "", ""),
        f"event.sh push-rejected remote_sha=def5678 error=  To origin\n{fetch_first}  ",
        (1, "push rejected (non-fast-forward): origin/feature is at def5678\n"),
        "event.sh push-failed error=  last out \n  last err  attempts=2",
    )


def test_main_returns_2_on_a_failed_event_write_bad_tunable_or_bad_argument_and_1_with_an_empty_remote_sha(monkeypatch, capsys, push_branch, fake_processes):
    push = "git push --set-upstream origin HEAD"
    rejected = " ! [rejected]        HEAD -> feature (non-fast-forward)"
    bad_argument = "push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, got '{}'\n" \
                   "usage: push-branch.sh [--force-with-lease=<branch>:<sha>]\n"

    def run_with(argv, push_answer, event_code=0, ls_remote_code=0, retries="0", backoff="0"):
        stderr_at_event = []

        def answer(line):
            if line.startswith("git push "):
                return push_answer
            if line == "git rev-parse --abbrev-ref HEAD":
                return 0, "feature\n"
            if line == "git ls-remote origin refs/heads/feature":
                return (0, "abc1234def\trefs/heads/feature\n") if ls_remote_code == 0 else (128, "")
            if line.startswith("event.sh "):
                stderr_at_event.append(capsys.readouterr().err)
                return event_code, ""
            return 0, ""

        calls = fake_processes(merged(answer))
        monkeypatch.setenv("VERI_PUSH_RETRIES", retries)
        monkeypatch.setenv("VERI_PUSH_BACKOFF", backoff)
        code = push_branch.main(argv)
        return code, calls, stderr_at_event, capsys.readouterr().err

    unreachable = (128, "fatal: unable to access origin\n")
    observed = (
        run_with([], unreachable, event_code=1)[::2],
        run_with([], (1, rejected + "\n"), event_code=1)[::2],
        run_with([], (1, rejected + "\n"), ls_remote_code=128),
        run_with([], unreachable, retries="x"),
        run_with([], unreachable, backoff="-1"),
        run_with(["--force-with-lease=b:abc1234", "extra"], unreachable),
        run_with(["--force-with-lease=b:HEAD"], unreachable),
    )

    assert observed == (
        (2, ["push-branch.sh: push failed after 1 attempts; the branch is not on the remote\n"]),
        (2, ["push rejected (non-fast-forward): origin/feature is at abc1234def\n"]),
        (1, [push, "git rev-parse --abbrev-ref HEAD", "git ls-remote origin refs/heads/feature",
             f"event.sh push-rejected remote_sha= error={rejected}"],
         ["push rejected (non-fast-forward): origin/feature is at \n"], ""),
        (2, [], [], "push-branch.sh: VERI_PUSH_RETRIES must be a non-negative integer, got 'x'\n"),
        (2, [], [], "push-branch.sh: VERI_PUSH_BACKOFF must be a non-negative integer, got '-1'\n"),
        (2, [], [], bad_argument.format("--force-with-lease=b:abc1234 extra")),
        (2, [], [], bad_argument.format("--force-with-lease=b:HEAD")),
    )


def test_main_retries_an_unreachable_origin_doubling_its_backoff_and_returns_2_on_a_bad_tunable_or_failed_event_write(monkeypatch, capsys, push_branch, fake_processes):
    push = "git push --set-upstream origin HEAD"
    rejected = " ! [rejected]        HEAD -> feature (non-fast-forward)"
    unreachable = (128, "fatal: unable to access origin\n")

    def run_with(env, push_answers, event_code=0):
        answers = list(push_answers)

        def answer(line):
            if line == push:
                return answers.pop(0) if len(answers) > 1 else answers[0]
            if line == "git rev-parse --abbrev-ref HEAD":
                return 0, "feature\n"
            if line == "git ls-remote origin refs/heads/feature":
                return 0, "abc1234def\trefs/heads/feature\n"
            if line.startswith("event.sh "):
                return event_code, ""
            return 0, ""

        calls = fake_processes(merged(answer))
        for name in ("VERI_PUSH_RETRIES", "VERI_PUSH_BACKOFF"):
            if name in env:
                monkeypatch.setenv(name, env[name])
            else:
                monkeypatch.delenv(name, raising=False)
        code = push_branch.main([])
        return code, calls, capsys.readouterr().err

    def kinds(calls):
        return [line if not line.startswith("event.sh ") else line.split(" ")[1] for line in calls]

    two_retries = run_with({"VERI_PUSH_RETRIES": "2", "VERI_PUSH_BACKOFF": "0"}, [unreachable])
    default_retries = run_with({"VERI_PUSH_BACKOFF": "0"}, [unreachable])
    second_lands = run_with({"VERI_PUSH_BACKOFF": "0"}, [unreachable, (0, "")])
    backoff = run_with({"VERI_PUSH_RETRIES": "3", "VERI_PUSH_BACKOFF": "1"}, [unreachable])

    observed = (
        (two_retries[0], two_retries[1].count(push), kinds(two_retries[1]).count("push-failed"), two_retries[2]),
        default_retries[1].count(push),
        (second_lands[0], kinds(second_lands[1]), second_lands[2]),
        [line for line in backoff[1] if line.startswith("sleep ")],
        run_with({"VERI_PUSH_RETRIES": "abc", "VERI_PUSH_BACKOFF": "0"}, [unreachable])[:2],
        run_with({"VERI_PUSH_RETRIES": "0", "VERI_PUSH_BACKOFF": "1.5"}, [unreachable])[:2],
        run_with({"VERI_PUSH_RETRIES": "0", "VERI_PUSH_BACKOFF": "0"}, [unreachable], event_code=1)[0],
        run_with({"VERI_PUSH_RETRIES": "0", "VERI_PUSH_BACKOFF": "0"}, [(1, rejected + "\n")], event_code=1)[0],
    )

    assert observed == (
        (0, 3, 1, "push-branch.sh: push failed after 3 attempts; the branch is not on the remote\n"),
        4,
        (0, [push, "sleep 0", push], ""),
        ["sleep 1", "sleep 2", "sleep 4"],
        (2, []),
        (2, []),
        2,
        2,
    )


def test_main_refuses_a_retries_or_backoff_that_is_not_a_non_negative_whole_number_naming_it_issue_776(monkeypatch, capsys, push_branch, fake_processes):
    def run_with(name, value):
        calls = fake_processes(lambda line, **_: (128, "fatal: unable to access origin\n", ""))
        monkeypatch.setenv("VERI_PUSH_RETRIES", "0")
        monkeypatch.setenv("VERI_PUSH_BACKOFF", "0")
        monkeypatch.setenv(name, value)
        code = push_branch.main([])
        return code, calls, capsys.readouterr().err

    bad = ("+3", " 3", "3 ", "1_0", "1e3", "0x10", "٣")
    names = ("VERI_PUSH_RETRIES", "VERI_PUSH_BACKOFF")
    observed = [run_with(name, value) for name in names for value in bad]

    assert observed == [
        (2, [], f"push-branch.sh: {name} must be a non-negative integer, got '{value}'\n")
        for name in names for value in bad
    ]
