"""In-process check-earlier cases on a python case whose recorded helpers: digest is the legacy stop-at-func value
(#3164): check-earlier accepts it and re-records it from the current formula, on a history committed through
fed_commits (PRD 017.8)."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
SUITE = "tests/test_suite.py"
OLDER = "def test_older_case():\n    assert True\n"
EARLIER, CURRENT = "step one adds a case", "step two adds nothing"
WITH_OTHER = ("def helper():\n    assert 1 == 1\n\n\ndef test_a():\n    helper()\n\n\n"
              "def other():\n    assert 2 == 2\n")
WITH_TEST_B = ("def helper():\n    assert 1 == 1\n\n\ndef test_a():\n    helper()\n\n\n"
               "def test_b():\n    assert 3 == 3\n")


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


def _legacy_recorded(root, run_cli, tests_frozen, text, edited=None):
    """Step EARLIER records OLDER + text; the suite then holds OLDER + edited (default text), and the record's helpers:
    lines are replaced by one for test_a holding the legacy digest of the suite's text. Returns (record, ledger)."""
    suite = root / SUITE
    suite.write_text(OLDER + "\n\n" + text)
    run_cli(tests_frozen, ["record", "--step", EARLIER, SUITE], cwd=root)
    now = text if edited is None else edited
    suite.write_text(OLDER + "\n\n" + now)
    (record,) = (root / ".tdd").glob("tests-frozen-*.record")
    legacy = tests_frozen.body_digest("\n".join(sorted(tests_frozen._assertion_lines(now))))
    kept = [line for line in record.read_text().splitlines(keepends=True) if not line.startswith("helpers:")]
    record.write_text("".join(kept) + "helpers: %s\ttest_a\t%s\n" % (SUITE, legacy))
    ledger = root / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (EARLIER, CURRENT))
    return record, ledger


def test_check_earlier_exits_0_for_a_python_case_whose_recorded_helpers_digest_is_the_legacy_stop_at_func_value_3164(
        tmp_path, run_cli, tests_frozen, based):
    _, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, WITH_OTHER)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_earlier_leaves_one_helpers_line_equal_to_the_current_digest_after_accepting_a_legacy_one_3164(
        tmp_path, run_cli, tests_frozen, based):
    record, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, WITH_OTHER)
    suite = tmp_path / SUITE
    now = tests_frozen._helper_digest(suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "test_a")[0])

    code = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=tmp_path)[0]
    held = [line.split("\t")[-1] for line in record.read_text().splitlines() if line.startswith("helpers: ")]

    assert (code, held) == (0, [now])


def test_check_earlier_exits_1_and_leaves_a_legacy_helpers_line_as_recorded_when_its_own_case_was_edited_3164(
        tmp_path, run_cli, tests_frozen, based):
    record, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, WITH_TEST_B)
    before = record.read_text()
    edited = WITH_TEST_B.replace("    helper()\n", "    helper()\n    assert 9 == 9\n")
    (tmp_path / SUITE).write_text(OLDER + "\n\n" + edited)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=tmp_path)

    assert (code, "test_a" in out, record.read_text()) == (1, True, before)


def test_check_earlier_exits_1_and_leaves_a_legacy_helpers_line_as_recorded_when_another_case_was_edited_3164(
        tmp_path, run_cli, tests_frozen, based):
    edited = WITH_TEST_B.replace("3 == 3", "3 == 4")
    record, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, WITH_TEST_B, edited=edited)
    before = record.read_text()

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=tmp_path)

    assert (code, "test_b" in out, "test_a" in out, record.read_text()) == (1, True, False, before)


def test_check_earlier_names_the_case_on_stderr_saying_its_helpers_digest_was_re_recorded_from_the_legacy_formula_3164(
        tmp_path, run_cli, tests_frozen, based):
    _, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, WITH_OTHER)

    code, _, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=tmp_path)

    assert (code, "test_a" in err, "re-recorded" in err, "legacy" in err) == (0, True, True, True)


def test_a_second_check_earlier_after_the_legacy_re_record_exits_0_and_prints_no_legacy_line_again_3164(
        tmp_path, run_cli, tests_frozen, based):
    _, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, WITH_OTHER)
    argv = ["check-earlier", str(ledger), "--step", CURRENT]
    run_cli(tests_frozen, argv, cwd=tmp_path)

    code, out, err = run_cli(tests_frozen, argv, cwd=tmp_path)

    assert (code, out, err) == (0, "", "")


def test_check_earlier_exits_1_naming_the_case_when_an_assertion_is_deleted_from_the_helper_after_the_legacy_re_record_3164(
        tmp_path, run_cli, tests_frozen, based):
    _, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, WITH_OTHER)
    argv = ["check-earlier", str(ledger), "--step", CURRENT]
    first = run_cli(tests_frozen, argv, cwd=tmp_path)[0]
    (tmp_path / SUITE).write_text(OLDER + "\n\n" + WITH_OTHER.replace("    assert 1 == 1\n", "    pass\n"))

    code, out, _ = run_cli(tests_frozen, argv, cwd=tmp_path)

    assert (first, code, "test_a" in out) == (0, 1, True)


ABOVE_CLASS = ("def helper():\n    assert 1 == 1\n\n\nclass TestA:\n    def test_a(self):\n        helper()\n"
               "        assert 2 == 2\n\n\ndef other():\n    assert 3 == 3\n")


def test_check_earlier_accepts_an_unscoped_helpers_digest_and_re_records_it_to_the_scoped_one_4868(
        tmp_path, run_cli, tests_frozen, based):
    """The helper above TestA once ran on to `def other`, through test_a's own assertion: that digest is accepted over
    the unchanged file and re-recorded to the scoped one, which ends the helper at test_a's head."""
    record, ledger = _legacy_recorded(tmp_path, run_cli, tests_frozen, ABOVE_CLASS)
    unscoped = tests_frozen.body_digest("assert1==1\nassert2==2")
    kept = [line for line in record.read_text().splitlines(keepends=True) if not line.startswith("helpers:")]
    record.write_text("".join(kept) + "helpers: %s\ttest_a\t%s\n" % (SUITE, unscoped))

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=tmp_path)
    held = [line.split("\t")[-1] for line in record.read_text().splitlines() if line.startswith("helpers: ")]

    assert (code, out, held) == (0, "", [tests_frozen.body_digest("assert1==1")])
