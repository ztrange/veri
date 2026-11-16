"""In-process `check-earlier` cases for veri/tests_frozen.py, on a history committed through fed_commits (PRD 017.6)."""
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
SUITE = "tests/test_suite.py"
FIXTURE = "tests/test_fixture.py"
GUARD = "tests/test_guard.py"
GUARD_ELSEWHERE = "projects/x/tests/test_guard.py"
OLDER = "def test_older_case():\n    assert True\n"


@pytest.fixture
def based(tmp_path, fed_commits):
    """tmp_path holding tests/ and .tdd/, the suite holding OLDER committed as "base"; returns the fed_commits log."""
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / SUITE).write_text(OLDER)
    repo = fed_commits()
    repo.add("tests")
    repo.commit("base")
    return repo


def test_check_earlier_exits_1_naming_the_case_an_earlier_step_recorded_and_the_step_when_a_later_leaf_weakened_it_2125(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a case", "step two adds another"
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_pinned_2125():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_pinned_2125():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert code == 1
    assert "test_pinned_2125" in out and earlier in out


def test_check_earlier_exits_0_printing_nothing_for_an_earlier_steps_case_renamed_with_its_text_otherwise_unchanged_2329(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a case", "step two renames it"
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_pinned_2329():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    based.add("tests")
    based.commit("step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_pinned_and_renamed_2329():\n    assert 1 == 2\n")
    based.add("tests")
    based.commit("step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_earlier_exits_1_naming_the_old_case_and_its_step_when_an_earlier_steps_case_is_renamed_and_its_body_changed_2329(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a case", "step two renames and weakens it"
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_pinned_2329():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    based.add("tests")
    based.commit("step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_pinned_and_renamed_2329():\n    assert True\n")
    based.add("tests")
    based.commit("step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert code == 1
    assert "test_pinned_2329" in out and earlier in out


def test_check_earlier_exits_1_naming_a_changed_case_in_a_file_whose_path_only_ends_with_a_guard_subject_3443(
        tmp_path, run_cli, tests_frozen, fed_commits):
    (tmp_path / "tests").mkdir()
    (tmp_path / "projects/x/tests").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    for name in (GUARD, GUARD_ELSEWHERE):
        (tmp_path / name).write_text("def test_existing_3443():\n    assert 1 == 1\n")
    repo = fed_commits()
    repo.add("tests", "projects")
    repo.commit("base")
    earlier = "step one ⟦guard-subject: %s⟧" % GUARD
    current = "step two edits the case again"
    for name in (GUARD, GUARD_ELSEWHERE):
        (tmp_path / name).write_text("def test_existing_3443():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, GUARD, GUARD_ELSEWHERE], cwd=tmp_path)
    repo.add("tests", "projects")
    repo.commit("step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    for name in (GUARD, GUARD_ELSEWHERE):
        (tmp_path / name).write_text("def test_existing_3443():\n    assert 1 == 3\n")
    repo.add("tests", "projects")
    repo.commit("step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert code == 1
    assert "test_existing_3443" in out and earlier in out


def test_check_earlier_exits_1_naming_exactly_one_case_when_two_identical_earlier_cases_are_removed_for_one_added_case_2419(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds two cases", "step two folds them into one"
    (tmp_path / SUITE).write_text(
        OLDER + "\n\ndef test_alpha_2419():\n    assert 1 == 1\n"
        "\n\ndef test_beta_2419():\n    assert 1 == 1\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    based.add("tests")
    based.commit("step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_gamma_2419():\n    assert 1 == 1\n")
    based.add("tests")
    based.commit("step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert code == 1
    assert len(out.splitlines()) == 1


def test_check_earlier_exits_1_naming_exactly_the_third_of_three_identical_earlier_cases_removed_for_two_added_cases_2419(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds three cases", "step two folds them into two"
    (tmp_path / SUITE).write_text(
        OLDER + "\n\ndef test_alpha_2419():\n    assert 1 == 1\n"
        "\n\ndef test_beta_2419():\n    assert 1 == 1\n"
        "\n\ndef test_delta_2419():\n    assert 1 == 1\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    based.add("tests")
    based.commit("step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(
        OLDER + "\n\ndef test_gamma_2419():\n    assert 1 == 1\n"
        "\n\ndef test_epsilon_2419():\n    assert 1 == 1\n")
    based.add("tests")
    based.commit("step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_delta_2419 (%s)\n" % earlier)


def test_check_earlier_exits_1_naming_the_case_and_its_step_when_the_case_or_its_whole_file_was_deleted_2125(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a case", "step two adds another"
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_pinned_2125():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    based.commit("step one", all=True)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    argv = ["check-earlier", str(ledger), "--step", current]

    (tmp_path / SUITE).write_text(OLDER)
    case_removed = run_cli(tests_frozen, argv, cwd=tmp_path)
    (tmp_path / SUITE).unlink()
    file_deleted = run_cli(tests_frozen, argv, cwd=tmp_path)

    expected = "test_pinned_2125 (%s)\n" % earlier
    assert [case_removed[:2], file_deleted[:2]] == [(1, expected), (1, expected)]


def test_check_earlier_exits_0_printing_nothing_when_the_current_step_only_adds_cases_and_skips_a_step_with_no_record_2125(
        tmp_path, run_cli, tests_frozen, based):
    earlier, unrecorded, current = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    recorded = OLDER + "\n\ndef test_pinned_2125():\n    assert 1 == 2\n"
    (tmp_path / SUITE).write_text(recorded)
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, unrecorded, current))
    (tmp_path / SUITE).write_text(recorded + "\n\ndef test_added_now():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_earlier_except_exempts_each_case_named_and_still_exits_1_for_a_changed_case_not_named_2125(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds cases", "step two adds another"
    (tmp_path / SUITE).write_text(
        OLDER + "\n\n"
        "def test_named_a_2125():\n    assert 1 == 2\n\n\n"
        "def test_named_b_2125():\n    assert 1 == 3\n\n\n"
        "def test_unnamed_2125():\n    assert 1 == 4\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(
        OLDER + "\n\n"
        "def test_named_a_2125():\n    assert True\n\n\n"
        "def test_named_b_2125():\n    assert True\n\n\n"
        "def test_unnamed_2125():\n    assert 1 == 4\n")
    argv = ["check-earlier", str(ledger), "--step", current,
            "--except", "test_named_a_2125", "--except", "test_named_b_2125"]

    named_only = run_cli(tests_frozen, argv, cwd=tmp_path)
    (tmp_path / SUITE).write_text(
        OLDER + "\n\n"
        "def test_named_a_2125():\n    assert True\n\n\n"
        "def test_named_b_2125():\n    assert True\n\n\n"
        "def test_unnamed_2125():\n    assert True\n")
    unnamed_too = run_cli(tests_frozen, argv, cwd=tmp_path)

    assert [named_only[:2], unnamed_too[:2]] == [
        (0, ""), (1, "test_unnamed_2125 (%s)\n" % earlier)]


def test_check_earlier_without_except_exempts_the_cases_a_replaces_case_step_names_and_the_fixture_file_a_fixture_repair_step_names_2125(
        tmp_path, run_cli, tests_frozen, based):
    earlier = "step one adds cases"
    (tmp_path / SUITE).write_text(
        OLDER + "\n\n"
        "def test_named_2125():\n    assert 1 == 2\n\n\n"
        "def test_unnamed_2125():\n    assert 1 == 3\n")
    (tmp_path / FIXTURE).write_text("def test_in_fixture_file_2125():\n    assert 1 == 4\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE, FIXTURE], cwd=tmp_path)
    (tmp_path / SUITE).write_text(
        OLDER + "\n\n"
        "def test_named_2125():\n    assert True\n\n\n"
        "def test_unnamed_2125():\n    assert True\n")
    (tmp_path / FIXTURE).write_text("def test_in_fixture_file_2125():\n    assert True\n")
    replaces = "⟦replaces-case⟧ replaces 'test_named_2125' in %s.test.sh" % SUITE
    repair = "repairs the fixture 'f' in %s, reproduced by a case ⟦fixture-repair⟧" % FIXTURE
    results = []
    for current in (replaces, repair):
        ledger = tmp_path / ".tdd/ledger.md"
        ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
        results.append(run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2])

    assert results == [
        (1, "test_unnamed_2125 (%s)\ntest_in_fixture_file_2125 (%s)\n" % (earlier, earlier)),
        (1, "test_named_2125 (%s)\ntest_unnamed_2125 (%s)\n" % (earlier, earlier))]


def test_check_earlier_prints_usage_naming_check_earlier_and_exits_2_without_a_ledger_or_step_or_with_an_unreadable_ledger_2125(
        tmp_path, run_cli, tests_frozen, fed_commits):
    fed_commits()
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] step\n")

    results = [run_cli(tests_frozen, argv, cwd=tmp_path)[::2] for argv in (
        ["check-earlier"],
        ["check-earlier", str(ledger)],
        ["check-earlier", str(tmp_path / "missing.md"), "--step", "step"])]

    assert [code for code, _ in results] == [2, 2, 2]
    assert all("usage:" in err and "check-earlier" in err for _, err in results)
    scripts = Path(__file__).resolve().parents[3]
    header = (scripts / "tests-frozen.sh").read_text().split("\nexec ")[0]
    assert "tests-frozen.sh check-earlier" in header
    assert "check-earlier" in (scripts.parent / "SCRIPTS.md").read_text()
