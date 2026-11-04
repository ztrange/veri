"""take's wait loop in veri/merge_lock.py, with a release --force landing at each point of it."""
import os
import shutil
from types import SimpleNamespace

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
