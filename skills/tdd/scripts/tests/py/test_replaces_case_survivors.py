"""In-process cases for veri/replaces_case_survivors.py, the module replaces-case-survivors.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def survivors():
    return importlib.import_module("veri.replaces_case_survivors")


def test_main_exits_0_when_every_named_case_is_gone_and_1_naming_each_one_still_present_1406(tmp_path, run_cli, survivors):
    suite = tmp_path / "tests" / "demo.test.sh"
    suite.parent.mkdir()
    suite.write_text('verdict "kept case" 0\nverdict "stale first" 0\nverdict "stale second" 0\n')
    step = "the replacement takes over: replaces 'stale first', 'stale second', 'long gone' in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"

    still_owed = run_cli(survivors, [step], cwd=tmp_path)
    suite.write_text('verdict "kept case" 0\n')
    done = run_cli(survivors, [step], cwd=tmp_path)

    assert done == (0, "", "")
    code, out, _ = still_owed
    assert code == 1
    assert [line for line in out.splitlines() if "stale first" in line or "stale second" in line] != []
    assert "stale first" in out and "stale second" in out
    assert "long gone" not in out and "kept case" not in out


def test_main_exits_0_when_a_named_case_appears_only_inside_a_longer_case_name_or_a_comment_1406(tmp_path, run_cli, survivors):
    suite = tmp_path / "tests" / "demo.test.sh"
    suite.parent.mkdir()
    suite.write_text('# stale first was deleted\nverdict "kept case" 0\nverdict "stale first, extended" 0\n')
    step = "the replacement takes over: replaces 'stale first' in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"

    assert run_cli(survivors, [step], cwd=tmp_path) == (0, "", "")


def test_main_reports_a_still_present_case_whose_name_holds_an_apostrophe_1406(tmp_path, run_cli, survivors):
    name = "a variable added to the shared session list reaches neither the leaf's nor the conductor's claude (#621)"
    suite = tmp_path / "tests" / "run-leaf.test.sh"
    suite.parent.mkdir()
    suite.write_text(f'verdict "kept case" 0\nverdict "{name}" 0\n')
    step = (
        "veri.run_leaf.main strips the launched environment only through veri.session_env, so a name added "
        f"to veri.session_env.SESSION_VARS is absent from the faked launch's environment: replaces '{name}' "
        "in tests/run-leaf.test.sh ⟦replaces-case⟧ ⟦criterion 4⟧"
    )

    code, out, _ = run_cli(survivors, [step], cwd=tmp_path)

    assert code == 1
    assert name in out


def test_main_exits_0_naming_nothing_when_the_green_deleted_the_whole_suite_file_1406(tmp_path, run_cli, survivors):
    step = "the replacement takes over: replaces 'stale first', 'stale second' in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"

    assert run_cli(survivors, [step], cwd=tmp_path) == (0, "", "")
