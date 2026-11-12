"""run_case finds detect-test-command.sh in the scripts directory, the parent of veri/."""
import importlib
import os
import subprocess


def test_run_case_looks_up_detect_test_command_in_the_scripts_directory_not_under_veri(monkeypatch):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(tick_ledger.subprocess, "run", fake_run)
    tick_ledger.run_case("tests/py/unit/test_x.py::test_y")

    scripts = os.path.dirname(os.path.dirname(os.path.realpath(tick_ledger.__file__)))
    assert os.path.isfile(os.path.join(scripts, "detect-test-command.sh"))
    assert calls[0][0] == os.path.join(scripts, "detect-test-command.sh")
