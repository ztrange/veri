"""Importing run_conductor must leave the importing process's bytecode writing as it was."""
import importlib.util
import sys

from conftest import SCRIPTS


def test_importing_run_conductor_leaves_the_importing_process_bytecode_writing_as_it_was(monkeypatch):
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    spec = importlib.util.spec_from_file_location("run_conductor_import_probe", str(SCRIPTS / "veri" / "run_conductor.py"))

    spec.loader.exec_module(importlib.util.module_from_spec(spec))

    assert sys.dont_write_bytecode is False
