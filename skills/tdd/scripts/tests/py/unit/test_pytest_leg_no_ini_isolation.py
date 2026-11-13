"""The no-ini serial subset case of test_pytest_leg_passes.py, under shared state poisoned on purpose."""
import importlib
import sys
import types

import pytest


def test_a_no_ini_subset_leg_started_beside_its_serial_case_is_unmoved_by_state_a_sibling_left_behind_3697(run_cli, tmp_path, monkeypatch):
    planted = tmp_path / "planted"
    (planted / "second").mkdir(parents=True)
    (planted / "second" / "test_planted_serial_in_second.py").write_text("import pytest\n@pytest.mark.serial\ndef test_serial():\n    pass\n")
    stale_record = tmp_path / "stale-serial-seen"
    stale_record.write_text("none\nnamed 7\nargs {\"targets\": [\"elsewhere\"], \"root\": \"/elsewhere\", \"ini\": null}\n")
    monkeypatch.setenv("PYTEST_LEG_SERIAL_SEEN", str(stale_record))
    stale_module = types.ModuleType("test_planted_serial_in_second")
    stale_module.__file__ = str(tmp_path / "elsewhere" / "test_planted_serial_in_second.py")
    monkeypatch.setitem(sys.modules, "test_planted_serial_in_second", stale_module)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}

    code, out, err = run_cli(importlib.import_module("veri.pytest_leg"),
                             ["--subset", "-m", "not slow", "-q", "-p", "no:cacheprovider", str(planted)], env=env,
                             cwd=planted / "second")

    assert (code, "unselected" in out + err, out.splitlines()[-1]) == (0, False, "1 named, 1 run, 1 passed, 0 failed across both passes")
