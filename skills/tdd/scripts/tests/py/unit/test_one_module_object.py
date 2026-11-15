"""conftest makes `veri.<name>` and flat `<name>` one module object, so a patch through either name is seen by both."""
import importlib

import pytest


@pytest.mark.parametrize("name", ["git", "status", "event_log", "run_dir", "pid_file", "push_branch"])
def test_both_names_are_one_module_object(name):
    assert importlib.import_module("veri." + name) is importlib.import_module(name)


def test_a_module_imported_by_another_is_the_same_object_under_both_names():
    event_log = importlib.import_module("veri.event_log")
    run_dir = importlib.import_module("run_dir")
    assert event_log.run_file is run_dir.run_file
    assert importlib.import_module("veri.run_dir") is run_dir


def test_a_patch_through_one_name_is_seen_through_the_other(monkeypatch):
    monkeypatch.setattr(importlib.import_module("veri.git"), "default_branch", lambda *a, **k: "patched")
    assert importlib.import_module("git").default_branch() == "patched"


def test_the_shared_object_keeps_its_flat_name_and_spec_so_a_reload_re_executes_it():
    module = importlib.import_module("veri.status")
    assert (module.__name__, module.__spec__.name) == ("status", "status")
    assert importlib.reload(module) is importlib.import_module("status")
