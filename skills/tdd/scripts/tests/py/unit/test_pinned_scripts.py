"""Cases for veri/pinned_scripts.py, the module pinned-scripts.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def pinned_scripts(tmp_path, monkeypatch):
    module = importlib.import_module("veri.pinned_scripts")
    monkeypatch.setattr(module, "main_working_tree", lambda: str(tmp_path))
    return module


def test_2627_prints_the_directory_holding_the_runs_pinned_scripts(tmp_path, run_cli, pinned_scripts):
    kept = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "pinned-scripts"
    kept.mkdir(parents=True)

    assert run_cli(pinned_scripts, ["7"]) == (0, "%s\n" % kept, "")


def test_2627_a_missing_directory_exits_2_naming_the_pin_and_the_recovery_never_a_path(tmp_path, run_cli, pinned_scripts):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7-skill-commit").write_text("abc123\n")

    code, out, err = run_cli(pinned_scripts, ["7"])

    assert (code, out, "abc123" in err, "git archive abc123 skills/tdd/scripts" in err) == (2, "", True, True)


def test_2627_no_recorded_pin_exits_2_saying_so(tmp_path, run_cli, pinned_scripts):
    code, out, err = run_cli(pinned_scripts, ["7"])

    assert (code, out, "no pin is recorded" in err) == (2, "", True)


@pytest.mark.parametrize("argv", ([], ["seven"], ["7", "8"]))
def test_2627_bad_arguments_exit_2_with_the_usage(run_cli, pinned_scripts, argv):
    code, out, err = run_cli(pinned_scripts, argv)

    assert (code, out, err.startswith("usage: pinned-scripts.sh")) == (2, "", True)
