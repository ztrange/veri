"""take, release and holder of veri/merge_lock.py under an --owner token."""
import os

from veri import merge_lock


def test_3134_release_by_the_owner_token_that_took_the_lock_frees_it(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    taken = merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    released = merge_lock._release(lock, record, ["--pid", me, "--owner", "token-a"])
    assert (taken, released, merge_lock._holder(lock, record, [])) == (0, 0, 3)
