"""The one-full-run lock of veri/full_run_lock.py, driven in-process on a lock file under the case's tmp_path."""
import fcntl
import importlib
import os
from builtins import open as builtins_open

import pytest


@pytest.fixture
def lock():
    return importlib.import_module("veri.full_run_lock")


@pytest.fixture(autouse=True)
def no_ambient_holder(monkeypatch):
    monkeypatch.delenv("PYTEST_LEG_FULL_LOCK_HOLDER", raising=False)
    monkeypatch.delenv("PYTEST_LEG_LOCK_WAIT_MARKER", raising=False)


@pytest.fixture(autouse=True)
def no_ps(monkeypatch):
    """A waiter records its start time through pid_file's ps reader; no case here starts ps."""
    monkeypatch.setattr(importlib.import_module("veri.pid_file"), "ps_field", lambda field, pid: None)


def test_the_lock_file_sits_beside_the_legs_registry_and_a_wait_marker_is_named_for_its_key(lock, monkeypatch):
    monkeypatch.setenv("VERI_PYTEST_LEGS", "/somewhere/legs/")

    assert (lock.legs_dir(), lock.path(), lock.wait_marker(77)) == (
        "/somewhere/legs/", "/somewhere/legs-full.lock", "/somewhere/legs-full.lock.wait-77")


def test_veri_test_lock_0_turns_the_lock_off_and_any_other_value_leaves_it_on(lock, monkeypatch):
    monkeypatch.setenv("VERI_TEST_LOCK", "0")
    off = lock.enabled()
    monkeypatch.setenv("VERI_TEST_LOCK", "1")
    on = lock.enabled()
    monkeypatch.delenv("VERI_TEST_LOCK")

    assert (off, on, lock.enabled()) == (False, True, True)


def planted_lock(lock, text):
    os.makedirs(os.path.dirname(lock.path()), exist_ok=True)
    with open(lock.path(), "w") as held:
        held.write(text)


@pytest.mark.parametrize("recorded, holder, expected", [
    ("pid {me}", "{me}", True),
    ("pid {me}", "", False),
    ("pid {me}", "not-a-pid", False),
    ("pid 1", "{me}", False),
    ("", "{me}", False),
], ids=["same-pid", "no-holder", "holder-not-a-number", "other-pid-recorded", "empty-file"])
def test_a_run_is_under_a_holder_only_when_its_environment_names_the_pid_the_lock_file_records(lock, monkeypatch, recorded, holder, expected):
    planted_lock(lock, recorded.format(me=os.getpid()) + "\ttree /x\n" if recorded else "")
    monkeypatch.setenv("PYTEST_LEG_FULL_LOCK_HOLDER", holder.format(me=os.getpid()))

    assert lock.held_by_ancestor() is expected


def test_a_run_is_not_under_a_holder_when_there_is_no_lock_file_or_the_recorded_holder_is_dead(lock, monkeypatch):
    monkeypatch.setenv("PYTEST_LEG_FULL_LOCK_HOLDER", "999999")
    missing = lock.held_by_ancestor()
    planted_lock(lock, "pid 999999\ttree /x\n")

    assert (missing, lock.held_by_ancestor()) == (False, False)


def test_acquiring_records_the_pid_and_tree_marks_this_process_the_holder_and_releasing_empties_the_file_and_restores_the_environment(lock, monkeypatch):
    monkeypatch.setenv("PYTEST_LEG_FULL_LOCK_HOLDER", "outer")

    held = lock.acquire()
    while_held = (open(lock.path()).read(), os.environ["PYTEST_LEG_FULL_LOCK_HOLDER"])
    held.release()

    assert while_held == ("pid %d\ttree %s\n" % (os.getpid(), os.path.realpath(os.getcwd())), str(os.getpid()))
    assert (open(lock.path()).read(), os.environ["PYTEST_LEG_FULL_LOCK_HOLDER"]) == ("", "outer")


def test_releasing_a_lock_taken_with_no_outer_holder_removes_the_holder_variable(lock):
    held = lock.acquire()
    held.release()

    assert "PYTEST_LEG_FULL_LOCK_HOLDER" not in os.environ


def contended(lock, monkeypatch, marker):
    """Take the lock with the first, non-blocking flock refused (a holder, who recorded itself in the file) and the second granted."""
    monkeypatch.setenv("PYTEST_LEG_LOCK_WAIT_MARKER", marker)
    os.makedirs(os.path.dirname(lock.path()), exist_ok=True)
    with open(lock.path(), "w") as held:
        held.write("pid 4242\ttree /other/tree\n")
    flags, marked = [], []

    def flock(handle, how):
        flags.append(how)
        if how & fcntl.LOCK_NB:
            raise BlockingIOError()
        marked.append(os.path.exists(marker))

    monkeypatch.setattr(fcntl, "flock", flock)
    lock.acquire().release()
    return flags, marked


def test_a_waiter_says_once_who_holds_the_lock_marks_its_wait_while_it_lasts_and_removes_the_mark_on_taking_the_lock(lock, monkeypatch, tmp_path, capfd):
    marker = str(tmp_path / "marker")

    flags, marked = contended(lock, monkeypatch, marker)

    assert (flags, marked, os.path.exists(marker)) == ([fcntl.LOCK_EX | fcntl.LOCK_NB, fcntl.LOCK_EX], [True], False)
    assert capfd.readouterr().err == "waiting for the full run holding the lock: pid 4242 tree /other/tree\n"


def test_3989_a_waiter_marks_its_wait_with_its_pid_on_line_1_and_its_start_time_on_line_2_in_pid_file_records_form(lock, monkeypatch, tmp_path):
    pid_file = importlib.import_module("veri.pid_file")
    started = "Mon Nov 16 10:00:00 2026"
    monkeypatch.setattr(pid_file, "ps_field", lambda field, pid: started if (field, int(pid)) == ("lstart", os.getpid()) else None)
    marker = tmp_path / "marker"
    monkeypatch.setenv("PYTEST_LEG_LOCK_WAIT_MARKER", str(marker))
    os.makedirs(os.path.dirname(lock.path()), exist_ok=True)
    texts = []

    def flock(handle, how):
        if how & fcntl.LOCK_NB:
            raise BlockingIOError()
        texts.append(marker.read_text())

    monkeypatch.setattr(fcntl, "flock", flock)
    lock.acquire().release()
    assert texts == ["%d\n%s\n" % (os.getpid(), started)]


def test_3989_a_wait_mark_whose_write_is_cut_short_leaves_no_empty_marker_behind(lock, monkeypatch, tmp_path):
    pid_file = importlib.import_module("veri.pid_file")

    class CutShort:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.handle.close()

        def write(self, text):
            raise OSError(28, "No space left on device")

    monkeypatch.setattr(pid_file, "open", lambda path, mode="r", *a, **k: CutShort(builtins_open(path, mode, *a, **k)), raising=False)
    marker = tmp_path / "marker"
    flags, marked = contended(lock, monkeypatch, str(marker))
    assert (marked, sorted(p.name for p in tmp_path.iterdir() if p.name.startswith("marker"))) == ([False], [])


def test_a_waiter_that_cannot_write_its_wait_mark_says_so_and_still_waits_for_the_lock(lock, monkeypatch, tmp_path, capfd):
    flags, marked = contended(lock, monkeypatch, str(tmp_path / "no-such-dir" / "marker"))

    err = capfd.readouterr().err
    assert (flags, marked) == ([fcntl.LOCK_EX | fcntl.LOCK_NB, fcntl.LOCK_EX], [False])
    assert err.startswith("waiting for the full run holding the lock: pid 4242 tree /other/tree\n")
    assert "cannot mark the lock wait, so it counts toward the leaf's timeout: " in err
