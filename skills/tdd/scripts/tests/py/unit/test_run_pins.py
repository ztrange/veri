"""In-process cases for veri/run_pins.py, the owner of a run's per-issue pin files."""
import importlib

import pytest


@pytest.fixture
def run_pins():
    return importlib.import_module("veri.run_pins")


def _tdd(root):
    (root / ".tdd").mkdir(parents=True, exist_ok=True)
    return root / ".tdd"


def test_write_skip_verify_writes_the_listed_phases_and_a_newline_or_nothing_when_none_are_listed(tmp_path, run_pins):
    seen = []
    for listed in ("refactor,green", ""):
        _tdd(tmp_path)
        run_pins.write_skip_verify(str(tmp_path), 7, listed)
        seen.append((tmp_path / ".tdd" / "issue-7-skip-verify").read_bytes())

    assert seen == [b"refactor,green\n", b""]


def test_skip_verify_answers_the_stripped_list_of_the_first_root_that_holds_the_pin_and_none_when_no_root_does(tmp_path, run_pins):
    first, second = tmp_path / "a", tmp_path / "b"
    assert run_pins.skip_verify(7, str(first), str(second)) is None
    (_tdd(second) / "issue-7-skip-verify").write_text("  refactor \n")
    assert run_pins.skip_verify(7, str(first), str(second)) == "refactor"
    (_tdd(first) / "issue-7-skip-verify").write_text(" \n")
    assert run_pins.skip_verify(7, str(first), str(second)) == ""


def test_write_conductor_model_then_conductor_model_round_trips_the_model_with_one_newline_on_disk(tmp_path, run_pins):
    _tdd(tmp_path)
    run_pins.write_conductor_model(str(tmp_path), 7, "sonnet")

    assert ((tmp_path / ".tdd" / "issue-7-conductor-model").read_bytes(),
            run_pins.conductor_model(7, str(tmp_path))) == (b"sonnet\n", "sonnet")


def test_conductor_model_answers_none_when_the_run_recorded_none(tmp_path, run_pins):
    assert run_pins.conductor_model(7, str(tmp_path)) is None
