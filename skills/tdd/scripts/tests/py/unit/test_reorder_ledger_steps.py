"""In-process cases for veri/reorder_ledger_steps.py, the module reorder-ledger-steps.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def reorder():
    return importlib.import_module("veri.reorder_ledger_steps")


def test_reorder_ledger_steps_the_even_when_left_in_localStorage_step_placed_first_ends_second_after_the_remembered_choice_step(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #125\n\n- [ ] Without dev tools compiled in, payment succeeds even when a failure choice is left in localStorage\n- [ ] The failure choice is remembered in localStorage like the other dev menus\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['even when a failure choice is left in localStorage', 'after', 'remembered in localStorage']])

    assert code == 0
    assert ledger.read_bytes() == '# Plan for #125\n\n- [ ] The failure choice is remembered in localStorage like the other dev menus\n- [ ] Without dev tools compiled in, payment succeeds even when a failure choice is left in localStorage\n'.encode()


def test_reorder_ledger_steps_the_last_step_moved_before_the_middle_step_lands_just_ahead_of_it(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #126\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['charlie', 'before', 'bravo']])

    assert code == 0
    assert ledger.read_bytes() == '# Plan for #126\n\n- [ ] alpha step\n- [ ] charlie step\n- [ ] bravo step\n'.encode()


def test_reorder_ledger_steps_a_ticked_step_to_move_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #127\n\n- [x] alpha step\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['alpha', 'after', 'charlie']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'alpha' in err


def test_reorder_ledger_steps_a_ticked_anchor_carrying_the_refactor_pending_mark_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #128\n\n- [x] alpha step ⟂ refactor pending\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['charlie', 'after', 'alpha']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'alpha' in err


def test_reorder_ledger_steps_an_unchecked_step_to_move_carrying_the_refactor_pending_mark_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #129\n\n- [ ] alpha step ⟂ refactor pending\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['alpha', 'after', 'charlie']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'alpha' in err


def test_reorder_ledger_steps_an_unchecked_anchor_carrying_the_refactor_pending_mark_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #130\n\n- [ ] alpha step\n- [ ] bravo step ⟂ refactor pending\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['alpha', 'after', 'bravo']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'bravo' in err


def test_reorder_ledger_steps_a_step_substring_matching_no_step_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #131\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['zulu', 'after', 'charlie']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'zulu' in err


def test_reorder_ledger_steps_an_anchor_substring_matching_no_step_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #132\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['alpha', 'after', 'zulu']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'zulu' in err


def test_reorder_ledger_steps_a_step_substring_matching_more_than_one_step_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #133\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['step', 'after', 'charlie']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'step' in err


def test_reorder_ledger_steps_an_anchor_substring_matching_more_than_one_step_exits_1(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #134\n\n- [ ] alpha step\n- [ ] bravo shared\n- [ ] charlie shared\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['alpha', 'after', 'shared']])

    assert code == 1
    assert ledger.read_bytes() == original
    assert 'shared' in err


def test_reorder_ledger_steps_a_position_other_than_before_or_after_exits_2(tmp_path, run_cli, reorder):
    ledger = tmp_path / "ledger.md"
    original = '# Plan for #135\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n'.encode()
    ledger.write_bytes(original)

    code, out, err = run_cli(reorder, [str(ledger), *['alpha', 'sideways', 'charlie']])

    assert code == 2
    assert ledger.read_bytes() == original


def test_the_four_ledger_entry_points_exit_2_naming_the_path_and_the_os_reason_for_a_ledger_path_that_is_a_directory(tmp_path, run_cli):
    ledger = tmp_path / "ledger.md"
    ledger.mkdir()
    calls = [
        ("veri.tick_ledger", [str(ledger), "alpha"]),
        ("veri.add_ledger_step", [str(ledger), "after", "alpha", "new step"]),
        ("veri.reorder_ledger_steps", [str(ledger), "alpha", "after", "bravo"]),
        ("veri.clear_refactor_pending", [str(ledger), "alpha"]),
    ]

    for name, argv in calls:
        code, out, err = run_cli(importlib.import_module(name), argv)

        assert (name, code) == (name, 2)
        assert (name, str(ledger) in err, "Is a directory" in err) == (name, True, True)
