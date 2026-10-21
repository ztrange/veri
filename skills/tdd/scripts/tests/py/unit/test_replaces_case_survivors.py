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


def test_main_exits_0_when_a_deleted_named_case_is_quoted_only_in_a_comment_line_of_the_suite_1406(tmp_path, run_cli, survivors):
    suite = tmp_path / "tests" / "demo.test.sh"
    suite.parent.mkdir()
    suite.write_text('# removed "stale first" and \'stale second\' (see #12)\nverdict "kept case" 0\n')
    step = "the replacement takes over: replaces 'stale first', 'stale second' in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 4⟧"

    assert run_cli(survivors, [step], cwd=tmp_path) == (0, "", "")


def test_main_reports_the_last_of_several_named_cases_when_only_it_is_still_present_1406(tmp_path, run_cli, survivors):
    suite = tmp_path / "tests" / "demo.test.sh"
    suite.parent.mkdir()
    suite.write_text('verdict "kept case" 0\nverdict "stale third" 0\n')
    step = "the replacement takes over: replaces 'stale first', 'stale second', 'stale third' in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"

    code, out, _ = run_cli(survivors, [step], cwd=tmp_path)

    assert code == 1
    assert "stale third" in out


def test_main_exits_3_with_no_output_and_no_traceback_on_a_step_carrying_no_replaces_case_mark_1558(tmp_path, run_cli, survivors):
    step = "the launcher prints its usage line when called with no argument ⟦criterion 2⟧"

    code, out, err = run_cli(survivors, [step], cwd=tmp_path)

    assert (code, out) == (3, "")
    assert "Traceback" not in err and "AttributeError" not in err


def test_main_reports_a_still_present_case_named_with_backslash_escapes_spelled_the_same_in_the_suite_1617(tmp_path, run_cli, survivors):
    suite = tmp_path / "tests" / "demo.test.sh"
    suite.parent.mkdir()
    suite.write_text('verdict "kept case" 0\nverdict "\\`### 🔴 Red\\` heading and \\"<STEP>\\" and \\$S" 0\n')
    step = (
        "the replacement takes over: replaces '\\`### 🔴 Red\\` heading and \\\"<STEP>\\\" and \\$S' "
        "in tests/demo.test.sh ⟦replaces-case⟧ ⟦criterion 4⟧"
    )

    code, out, _ = run_cli(survivors, [step], cwd=tmp_path)

    assert code == 1
    assert "\\`### 🔴 Red\\` heading and \\\"<STEP>\\\" and \\$S" in out


def test_main_exits_3_with_no_output_on_a_step_mentioning_the_replaces_case_mark_only_in_its_prose_or_backticks_1538(tmp_path, run_cli, survivors):
    suite = tmp_path / "tests" / "demo.test.sh"
    suite.parent.mkdir()
    suite.write_text('verdict "stale first" 0\n')
    prose = "the guard reads the ⟦replaces-case⟧ mark only among trailing marks: replaces 'stale first' in tests/demo.test.sh ⟦criterion 2⟧"
    ticks = "a step that only quotes `⟦replaces-case⟧`: replaces 'stale first' in tests/demo.test.sh ⟦criterion 2⟧"

    assert [run_cli(survivors, [step], cwd=tmp_path) for step in (prose, ticks)] == [(3, "", "")] * 2


def test_main_reports_both_cases_of_a_step_joining_two_quoted_names_with_and_1538(tmp_path, run_cli, survivors):
    first = "a variable added to lib/session-env.sh's session list does not reach the conductor's claude (#621)"
    second = "a name planted in lib/session-env.sh's SESSION_VARS stays out of run-conductor.sh's claude's environment"
    suite = tmp_path / "skills" / "tdd" / "scripts" / "tests" / "run-leaf.test.sh"
    suite.parent.mkdir(parents=True)
    suite.write_text(f'verdict "kept case" 0\nverdict "{first}" 0\nverdict "{second}" 0\n')
    step = (
        "veri.run_conductor.main strips claude's environment only through veri.session_env, so a name added "
        "to veri.session_env.SESSION_VARS is absent from the faked launch's environment: "
        f"replaces '{first}' and '{second}' in skills/tdd/scripts/tests/run-leaf.test.sh "
        "⟦replaces-case⟧ ⟦criterion 1⟧"
    )

    code, out, _ = run_cli(survivors, [step], cwd=tmp_path)

    assert code == 1
    assert first in out and second in out
    assert "kept case" not in out


def test_main_prints_nothing_and_exits_0_once_one_deletion_removed_all_eight_named_cases_1781(tmp_path, run_cli, survivors):
    names = [f"push case {i}" for i in range(1, 9)]
    suite = tmp_path / "tests" / "push-branch.test.sh"
    suite.parent.mkdir()
    suite.write_text("".join(f'verdict "{n}" 0\n' for n in names) + 'verdict "kept case" 0\n')
    listed = ", ".join(f"'{n}'" for n in names)
    step = f"the port takes over: replaces {listed} in tests/push-branch.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧"
    suite.write_text('verdict "kept case" 0\n')

    assert run_cli(survivors, [step], cwd=tmp_path) == (0, "", "")


def test_main_exits_2_with_one_stderr_line_naming_the_step_when_the_clause_mixes_quoted_and_unquoted_names_1882(run_cli, survivors):
    step = "the replacement takes over: replaces 'a', b, 'c' in t/x.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧"

    code, out, err = run_cli(survivors, [step])

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert step in err


def test_main_exits_2_with_one_stderr_line_naming_the_step_when_the_clause_is_fully_unquoted_1882(run_cli, survivors):
    step = "the replacement takes over: replaces a, b in t/x.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧"

    code, out, err = run_cli(survivors, [step])

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert step in err


def test_main_exits_2_with_one_stderr_line_naming_the_step_when_the_suite_is_not_a_test_sh_file_1882(run_cli, survivors):
    step = "the replacement takes over: replaces 'a' in t/x.py ⟦replaces-case⟧ ⟦criterion 2⟧"

    code, out, err = run_cli(survivors, [step])

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert step in err


def test_main_exits_3_with_nothing_printed_when_the_quoted_clause_has_no_suite_after_it_1954(run_cli, survivors):
    step = "the replacement takes over: replaces 'a', 'b' ⟦replaces-case⟧ ⟦criterion 2⟧"

    assert run_cli(survivors, [step]) == (3, "", "")
