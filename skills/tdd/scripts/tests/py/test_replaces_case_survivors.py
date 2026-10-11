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
