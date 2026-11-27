"""Small cases for veri/leg_registry.py: the legs registry's entries and what a reader counts of them."""
import importlib

import pytest

STARTED = "Wed Nov 18 08:00:00 2026"


@pytest.fixture
def leg_registry(monkeypatch):
    """leg_registry with ps answering STARTED for pids 101-104 and this process, and every other pid gone."""
    import os
    module = importlib.import_module("leg_registry")
    alive = {101, 102, 103, 104, os.getpid()}
    monkeypatch.setattr(module.pid_file, "ps_field", lambda field, pid: STARTED if int(pid) in alive else None)

    def kill(pid, signal):
        if pid not in alive:
            raise ProcessLookupError(pid)

    monkeypatch.setattr(module.os, "kill", kill)
    return module


def test_4805_a_leg_claimed_with_the_lock_wait_marker_set_registers_a_third_line_leaf_and_without_it_two_lines(leg_registry, monkeypatch):
    monkeypatch.setenv("PYTEST_LEG_LOCK_WAIT_MARKER", "/tmp/marker")
    leaf = leg_registry.registration(4)
    monkeypatch.setenv("PYTEST_LEG_LOCK_WAIT_MARKER", "")
    empty = leg_registry.registration(4)
    monkeypatch.delenv("PYTEST_LEG_LOCK_WAIT_MARKER")
    unset = leg_registry.registration(4)

    assert (leaf, empty, unset) == ("4\n%s\nleaf\n" % STARTED, "4\n%s\n" % STARTED, "4\n%s\n" % STARTED)


def test_4805_w_other_counts_live_entries_without_line_3_leaf_a_two_line_entry_included_and_a_dead_pids_entry_nowhere(leg_registry, tmp_path):
    (tmp_path / "101").write_text("4\n%s\nleaf\n" % STARTED)
    (tmp_path / "102").write_text("3\n%s\n" % STARTED)
    (tmp_path / "103").write_text("2\n%s\nother\n" % STARTED)
    (tmp_path / "999999").write_text("8\n%s\n" % STARTED)
    (tmp_path / "999998").write_text("8\n%s\nleaf\n" % STARTED)

    assert (leg_registry.other_workers(str(tmp_path)), leg_registry.registered_workers(str(tmp_path))) == (5, 9)
