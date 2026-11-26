"""take's wait loop in veri/merge_lock.py, with a release --force landing at each point of it."""
import os
import shutil
from types import SimpleNamespace

import pytest
from veri import merge_lock


def test_2361_take_waiting_on_a_held_lock_exits_0_holding_it_wherever_release_force_lands_in_its_wait_loop(
        tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setenv("VERI_MERGE_LOCK_POLL", "0")
    me = str(os.getpid())
    outcomes = {}
    for point in ("before the read", "holder removed, directory still there", "during the sleep"):
        lock = tmp_path / point.replace(", ", "-").replace(" ", "-") / "merge.lock"
        lock.mkdir(parents=True)
        (lock / "holder").write_text(f"{me} h t\n")
        record = str(lock / "holder")
        state = {"landed": False, "sleeps": 0}
        real_read = merge_lock._read_pid

        def read(path, point=point, lock=lock, state=state, real_read=real_read):
            if not state["landed"] and point == "before the read":
                state["landed"] = True
                shutil.rmtree(lock)
            elif not state["landed"] and point.startswith("holder removed"):
                state["landed"] = True
                os.unlink(path)
            return real_read(path)

        def sleep(_seconds, point=point, lock=lock, state=state):
            state["sleeps"] += 1
            assert state["sleeps"] < 5
            if point == "during the sleep" and not state["landed"]:
                state["landed"] = True
            if state["landed"] and lock.is_dir():
                shutil.rmtree(lock)

        monkeypatch.setattr(merge_lock, "_read_pid", read)
        monkeypatch.setattr(merge_lock, "time", SimpleNamespace(sleep=sleep))
        code = merge_lock._take(str(lock), record, ["--pid", me])
        outcomes[point] = (code, (lock / "holder").read_text().split()[0] if (lock / "holder").is_file() else None)
    assert outcomes == {point: (0, me) for point in outcomes}


def test_3027_take_with_no_lock_dir_and_a_failing_rename_polls_once_before_its_next_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    events = []

    def rename(src, dst):
        events.append("pass")
        if len(events) > 6:
            raise RuntimeError("spinning")
        raise OSError("staged dir gone")

    monkeypatch.setattr(merge_lock.os, "rename", rename)
    monkeypatch.setattr(merge_lock, "_poll_wait", lambda: events.append("poll"))
    lock = tmp_path / "tdd" / "merge.lock"
    try:
        merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(os.getpid())])
    except RuntimeError:
        pass
    assert events[:3] == ["pass", "poll", "pass"]


def test_3027_take_with_no_lock_dir_and_its_staged_dir_gone_exits_2_with_a_line_on_stderr(
        tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    polls = []

    def rename(src, dst):
        shutil.rmtree(src, ignore_errors=True)
        raise FileNotFoundError(src)

    def poll():
        polls.append(1)
        if len(polls) > 5:
            raise RuntimeError("still trying")

    monkeypatch.setattr(merge_lock.os, "rename", rename)
    monkeypatch.setattr(merge_lock, "_poll_wait", poll)
    lock = tmp_path / "tdd" / "merge.lock"
    try:
        code = merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(os.getpid())])
    except RuntimeError:
        code = "retried"
    assert (code, bool(capsys.readouterr().err.strip())) == (2, True)


def test_3027_take_waiting_on_a_live_holder_exits_2_naming_its_own_dead_pid_on_stderr(
        tmp_path, monkeypatch, capsys):
    me = os.getpid()
    dead = 4242424
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setattr(merge_lock, "_alive", lambda pid: pid == me)
    polls = []

    def poll():
        polls.append(1)
        if len(polls) > 5:
            raise RuntimeError("still waiting")

    monkeypatch.setattr(merge_lock, "_poll_wait", poll)
    lock = tmp_path / "tdd" / "merge.lock"
    lock.mkdir(parents=True)
    (lock / "holder").write_text(f"{me} h t\n")
    try:
        code = merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(dead)])
    except RuntimeError:
        code = "retried"
    assert (code, str(dead) in capsys.readouterr().err) == (2, True)


def test_3027_take_whose_own_pid_dies_after_three_polls_of_a_live_holder_exits_2_leaving_the_lock(
        tmp_path, monkeypatch, capsys):
    me = os.getpid()
    mine = 4242424
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    checks = []

    def alive(pid):
        if pid != mine:
            return True
        checks.append(1)
        return len(checks) <= 3

    polls = []

    def poll():
        polls.append(1)
        if len(polls) > 10:
            raise RuntimeError("still waiting")

    monkeypatch.setattr(merge_lock, "_alive", alive)
    monkeypatch.setattr(merge_lock, "_poll_wait", poll)
    lock = tmp_path / "tdd" / "merge.lock"
    lock.mkdir(parents=True)
    (lock / "holder").write_text(f"{me} h t\n")
    try:
        code = merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(mine)])
    except RuntimeError:
        code = "retried"
    assert (code, str(mine) in capsys.readouterr().err, (lock / "holder").read_text()) == (2, True, f"{me} h t\n")


def test_the_poll_wait_reads_an_empty_veri_merge_lock_poll_as_empty_and_fails_not_as_the_default_30(monkeypatch):
    monkeypatch.setattr(merge_lock.time, "sleep", lambda seconds: pytest.fail("slept %r" % seconds))
    monkeypatch.setenv("VERI_MERGE_LOCK_POLL", "")

    with pytest.raises(ValueError):
        merge_lock._poll_wait()


class _StillPolling(Exception):
    pass


def test_3995_take_on_a_lock_held_past_veri_merge_lock_wait_exits_2_naming_the_holder_and_the_limit_with_the_lock_in_place(
        tmp_path, monkeypatch, capsys):
    me = os.getpid()
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setenv("VERI_MERGE_LOCK_WAIT", "100")
    now = [1000.0]
    polls = []

    def sleep(_seconds):
        polls.append(1)
        if len(polls) > 20:
            raise _StillPolling
        now[0] += 30

    monkeypatch.setattr(merge_lock, "time", SimpleNamespace(sleep=sleep))
    monkeypatch.setattr(merge_lock, "_clock", lambda: now[0])
    lock = tmp_path / "tdd" / "merge.lock"
    lock.mkdir(parents=True)
    (lock / "holder").write_text(f"{me} h t\n")
    try:
        code = merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(me)])
    except _StillPolling:
        code = "still polling"
    err = capsys.readouterr().err
    assert (code, len(err.splitlines()), f"{me} h t" in err, "100" in err, (lock / "holder").read_text(),
            sorted(p.name for p in lock.parent.glob(".merge.lock.*"))) == (2, 1, True, True, f"{me} h t\n", [])


def test_3995_take_with_veri_merge_lock_wait_0_gives_up_at_the_first_poll_that_finds_the_lock_held(
        tmp_path, monkeypatch, capsys):
    me = os.getpid()
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setenv("VERI_MERGE_LOCK_WAIT", "0")
    monkeypatch.setattr(merge_lock, "_clock", lambda: 1000.0)
    polls = []

    def sleep(_seconds):
        polls.append(1)
        if len(polls) > 3:
            raise _StillPolling

    monkeypatch.setattr(merge_lock, "time", SimpleNamespace(sleep=sleep))
    lock = tmp_path / "tdd" / "merge.lock"
    lock.mkdir(parents=True)
    (lock / "holder").write_text(f"{me} h t\n")
    try:
        code = merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(me)])
    except _StillPolling:
        code = "still polling"
    assert (code, polls, (lock / "holder").read_text()) == (2, [], f"{me} h t\n")


PINNED_START = "Mon_Nov_16_10:00:00_2026"
LOCAL_START = "lun._16_nov._19:00:00_2026"


def _ps_by_environment(line, env=None, **_):
    """ps -o lstart= as it prints under LC_ALL=C TZ=UTC (pinned) and under the caller's fr_FR, Asia/Tokyo one."""
    seen = os.environ if env is None else env
    pinned = (seen.get("LC_ALL"), seen.get("TZ")) == ("C", "UTC")
    return 0, (PINNED_START if pinned else LOCAL_START).replace("_", " ") + "\n", ""


@pytest.mark.parametrize("recorded, expected", [
    (PINNED_START, (0, 1)),
    (LOCAL_START, (0, 1)),
    ("Thu_Jan__1_00:00:00_1970", (2, 0)),
], ids=["pinned-form-record", "old-local-form-record", "neither"])
def test_review_take_reads_a_live_holder_recorded_in_the_pinned_or_the_callers_local_form_as_live_and_any_other_as_stale(
        tmp_path, monkeypatch, fake_processes, recorded, expected):
    monkeypatch.setenv("TZ", "Asia/Tokyo")
    monkeypatch.setenv("LC_ALL", "fr_FR.UTF-8")
    fake_processes.answers({"ps -o lstart= -p": _ps_by_environment})
    me = os.getpid()
    lock = tmp_path / "tdd" / "merge.lock"
    lock.mkdir(parents=True)
    (lock / "holder").write_text(f"{me} h {recorded}\n")
    waits = []

    def release_on_wait(_seconds):
        waits.append(1)
        shutil.rmtree(lock)

    monkeypatch.setattr(merge_lock, "time", SimpleNamespace(sleep=release_on_wait))

    code = merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(me)])

    assert (code, len(waits)) == expected


def test_review_take_on_a_merge_lock_that_is_a_regular_file_exits_2_at_veri_merge_lock_wait_naming_what_it_found(
        tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setenv("VERI_MERGE_LOCK_WAIT", "100")
    now = [1000.0]
    polls = []

    def sleep(_seconds):
        polls.append(1)
        if len(polls) > 20:
            raise _StillPolling
        now[0] += 30

    monkeypatch.setattr(merge_lock, "time", SimpleNamespace(sleep=sleep))
    monkeypatch.setattr(merge_lock, "_clock", lambda: now[0])
    lock = tmp_path / "tdd" / "merge.lock"
    lock.parent.mkdir(parents=True)
    lock.write_text("not a directory\n")
    try:
        code = merge_lock._take(str(lock), str(lock / "holder"), ["--pid", str(os.getpid())])
    except _StillPolling:
        code = "still polling"
    err = capsys.readouterr().err
    assert (code, len(err.splitlines()), str(lock) in err, "regular file" in err, lock.read_text(),
            sorted(p.name for p in lock.parent.glob(".merge.lock.*"))) == (2, 1, True, True, "not a directory\n", [])
