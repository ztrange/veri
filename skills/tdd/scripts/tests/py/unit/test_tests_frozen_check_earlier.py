"""In-process `check-earlier` cases for veri/tests_frozen.py, on a history committed through fed_commits (PRD 017.6)."""
import hashlib
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


BASH_SUITE = "tests/suite.test.sh"


def _test_a_based(root, fed_commits):
    """root holding tests/ and .tdd/, the suite holding test_a committed as "base"; returns the suite's path."""
    (root / "tests").mkdir(parents=True)
    (root / ".tdd").mkdir()
    (root / SUITE).write_text("def test_a():\n    assert 0\n")
    repo = fed_commits(root=root)
    repo.add("tests")
    repo.commit("base")
    return root / SUITE


def test_check_earlier_exits_0_printing_nothing_when_a_later_step_re_recorded_a_case_and_a_still_later_step_left_it_alone_2125(
        tmp_path, run_cli, tests_frozen, fed_commits):
    suite = _test_a_based(tmp_path, fed_commits)
    one, two, three = "step one", "step two", "step three"
    suite.write_text("def test_a():\n    assert 1\n")
    run_cli(tests_frozen, ["record", "--step", one, SUITE], cwd=tmp_path)
    suite.write_text("def test_a():\n    assert 2\n")
    run_cli(tests_frozen, ["record", "--step", two, SUITE], cwd=tmp_path)
    suite.write_text("def test_a():\n    assert 2\n\n\ndef test_c():\n    assert 3\n")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (one, two, three))

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", three], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_earlier_exits_0_printing_nothing_for_a_later_step_that_leaves_alone_a_case_each_re_recording_route_edited_2125(
        tmp_path, run_cli, tests_frozen, fed_commits):
    routes = {
        "red-contradicted": "step two red-contradicted re-edits test_a",
        "red-supersede": "step two red-supersede re-edits test_a",
        "repair": "step two red-repair re-edits test_a, a case its green report superseded",
        "replaces-case": "⟦replaces-case⟧ replaces 'test_a' in %s.test.sh" % SUITE,
        "fixture-repair": "repairs the fixture 'f' in %s, reproduced by a case ⟦fixture-repair⟧" % SUITE}
    results = {}
    for route, two in routes.items():
        repo = tmp_path / route
        suite = _test_a_based(repo, fed_commits)
        one, three = "step one", "step three adds test_c"
        suite.write_text("def test_a():\n    assert 1\n")
        run_cli(tests_frozen, ["record", "--step", one, SUITE], cwd=repo)
        suite.write_text("def test_a():\n    assert 2\n")
        run_cli(tests_frozen, ["record", "--step", two, SUITE], cwd=repo)
        suite.write_text("def test_a():\n    assert 2\n\n\ndef test_c():\n    assert 3\n")
        ledger = repo / ".tdd/ledger.md"
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (one, two, three))
        results[route] = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", three], cwd=repo)[:2]

    assert results == {route: (0, "") for route in routes}


def test_check_earlier_exits_2_never_1_printing_usage_on_stderr_for_an_empty_step_an_empty_except_an_odd_except_count_and_outside_a_repository_2125(
        tmp_path, run_cli, tests_frozen, fed_commits, monkeypatch):
    fed_commits()
    # Outside a repository `git rev-parse --show-toplevel` fails, and case_history.toplevel answers None.
    monkeypatch.setattr(importlib.import_module("case_history"), "toplevel", lambda: None)
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] step one\n")
    base = ["check-earlier", str(ledger)]
    runs = [run_cli(tests_frozen, base + argv, cwd=tmp_path) for argv in (
        ["--step", ""],
        ["--step", "step one", "--except", ""],
        ["--step", "step one", "--except"],
        ["--step", "step one"])]

    assert [(code, out, "usage" in err) for code, out, err in runs] == [(2, "", True)] * 4


def test_check_earlier_exits_1_naming_the_case_and_its_step_when_a_decorator_is_added_above_a_recorded_case_followed_by_an_undecorated_case_2177(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a first case", "step two adds a second case"
    first = "def test_first_2177():\n    assert 1 == 2\n"
    second = "def test_second_2177():\n    assert True\n"
    (tmp_path / SUITE).write_text(OLDER + "\n\n" + first + "\n\n" + second)
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\n@pytest.mark.skip\n" + first + "\n\n" + second)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_first_2177 (%s)\n" % earlier)


def test_check_earlier_exits_1_naming_the_case_and_its_step_when_a_decorator_is_added_above_a_recorded_case_last_in_its_file_2177(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a last case", "step two adds another"
    body = "def test_last_2177():\n    assert 1 == 2\n"
    (tmp_path / SUITE).write_text(OLDER + "\n\n" + body)
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\n@pytest.mark.skip\n" + body)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_last_2177 (%s)\n" % earlier)


def test_check_earlier_exits_1_naming_a_python_def_case_whose_format_2_record_differs_from_its_current_digest_though_the_old_cut_matches_2591(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a def case", "step two adds a sibling"
    first = "def test_def_2591():\n    assert 1 == 2\n"
    second = "def test_sibling_2591():\n    assert True\n"
    (tmp_path / SUITE).write_text(OLDER + "\n\n" + first + "\n\n" + second)
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\n@pytest.mark.skip\n" + first + "\n\n" + second)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_def_2591 (%s)\n" % earlier)


def test_check_earlier_exits_0_printing_nothing_for_a_case_the_current_step_recorded_and_has_since_changed_2125(
        tmp_path, run_cli, tests_frozen, based):
    current = "step one adds a case"
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_own_2125():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", current, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % current)
    (tmp_path / SUITE).write_text(OLDER + "\n\ndef test_own_2125():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


# test_first_2177's body as the old cut took it: up to the next case's start, its decorator included.
OLD_CUT_BODY = "def test_first_2177():\n    assert 1 == 2\n\n\n@pytest.mark.timeout(60)"


def _old_cut_record(tmp_path, run_cli, tests_frozen, step):
    """Writes `step`'s record as the old cut did: test_first_2177 against OLD_CUT_BODY's digest, no format line."""
    _, record, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record.strip()).write_text("case: test_first_2177\nbody: %s\ttest_first_2177\t%s\n"
                                           % (SUITE, hashlib.sha256(OLD_CUT_BODY.encode()).hexdigest()))


def test_check_earlier_exits_0_printing_nothing_for_a_record_written_with_the_old_cut_against_an_unchanged_file_2177(
        tmp_path, run_cli, tests_frozen, fed_commits):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    fed_commits()
    earlier, current = "step one adds a case", "step two adds a decorated case"
    (tmp_path / SUITE).write_text(
        "def test_first_2177():\n    assert 1 == 2\n\n\n@pytest.mark.timeout(60)\n"
        "def test_second_2177():\n    assert True\n")
    _old_cut_record(tmp_path, run_cli, tests_frozen, earlier)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_earlier_exits_1_naming_a_case_changed_since_a_record_written_with_the_old_cut_2177(
        tmp_path, run_cli, tests_frozen, fed_commits):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    fed_commits()
    earlier, current = "step one adds a case", "step two adds a decorated case"
    _old_cut_record(tmp_path, run_cli, tests_frozen, earlier)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(
        "def test_first_2177():\n    assert 1 == 3\n\n\n@pytest.mark.timeout(60)\n"
        "def test_second_2177():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_first_2177 (%s)\n" % earlier)


def test_check_earlier_exits_1_naming_the_case_and_its_step_when_only_the_recorded_cases_own_decorator_is_edited_2177(
        tmp_path, run_cli, tests_frozen, based):
    earlier, current = "step one adds a decorated case", "step two adds another"
    body = "def test_decorated_2177():\n    assert 1 == 2\n"
    (tmp_path / SUITE).write_text(OLDER + "\n\n@pytest.mark.timeout(5)\n" + body)
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / SUITE).write_text(OLDER + "\n\n@pytest.mark.timeout(60)\n" + body)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_decorated_2177 (%s)\n" % earlier)
