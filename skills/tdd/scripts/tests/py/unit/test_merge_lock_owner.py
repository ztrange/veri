"""take, release and holder of veri/merge_lock.py under an --owner token."""
import os
import types

from veri import merge_lock


def test_3134_release_by_the_owner_token_that_took_the_lock_frees_it(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    taken = merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    released = merge_lock._release(lock, record, ["--pid", me, "--owner", "token-a"])
    assert (taken, released, merge_lock._holder(lock, record, [])) == (0, 0, 3)


def test_3134_release_by_another_owner_token_on_the_same_pid_is_refused(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    refused = merge_lock._release(lock, record, ["--pid", me, "--owner", "token-b"])
    held = merge_lock._holder(lock, record, [])
    named = capsys.readouterr().out.split()[:1]
    assert (refused, os.path.isdir(lock), held, named) == (1, True, 0, [me])


def test_3134_release_without_an_owner_of_a_lock_taken_under_one_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    refused = merge_lock._release(lock, record, ["--pid", me])
    assert (refused, os.path.isdir(lock)) == (1, True)


def test_3134_failed_gate_under_another_owner_token_of_the_same_pid_leaves_the_lock_held(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setattr(merge_lock.subprocess, "run", lambda cmd, **kw: types.SimpleNamespace(returncode=1))
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    code = merge_lock._gate(lock, record, ["--pid", me, "--owner", "token-b", "--", "false"])
    assert (code, os.path.isdir(lock), merge_lock._holder(lock, record, [])) == (1, True, 0)


def test_3134_take_under_another_owner_token_of_the_same_pid_keeps_waiting_with_the_lock_held(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    polls = []

    def poll():
        polls.append(1)
        if len(polls) > 3:
            raise RuntimeError("still waiting")

    monkeypatch.setattr(merge_lock, "_poll_wait", poll)
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    try:
        code = merge_lock._take(lock, record, ["--pid", me, "--owner", "token-b"])
    except RuntimeError:
        code = "waiting"
    held = merge_lock._holder(lock, record, [])
    assert (code, held, open(record).read().split()[3:]) == ("waiting", 0, ["token-a"])
