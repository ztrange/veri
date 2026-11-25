"""In-process `diff --step` cases for veri/tests_frozen.py."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


NEW = "tests/test_new.py"
STEP = "step one adds a case"


def test_diff_step_prints_the_unified_diff_from_the_recorded_content_to_the_current_content_of_an_edited_recorded_file(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / NEW).write_text("one\ntwo, changed\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "-two" in lines and "+two, changed" in lines
    assert " one" in lines
