"""In-process cases for veri/tests_frozen.py, the module tests-frozen.sh is a shim over."""
import hashlib
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


def test_path_names_a_steps_record_by_the_first_16_hex_digits_of_its_texts_sha256_whatever_its_length_or_slashes_1586(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "a.test.sh").write_text("assert one\n")
    long_step = "port the case / its pair " * 20
    short_step = "port the other case"

    answers = []
    for step in (long_step, short_step):
        code, out, err = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
        recorded = run_cli(tests_frozen, ["record", out.rstrip("\n"), "a.test.sh"], cwd=tmp_path)[0]
        answers.append((code, out, err, recorded))

    assert answers == [(0, ".tdd/tests-frozen-%s.record\n" % hashlib.sha256(step.encode()).hexdigest()[:16], "", 0)
                       for step in (long_step, short_step)]


def test_path_without_a_step_text_or_with_an_empty_one_is_exit_2_naming_the_usage_1586(tmp_path, run_cli, tests_frozen):
    answers = [run_cli(tests_frozen, argv, cwd=tmp_path) for argv in (["path"], ["path", ""])]

    assert [(code, out, "path <step-text>" in err) for code, out, err in answers] == [(2, "", True), (2, "", True)]


def test_two_consecutive_steps_on_one_suite_file_each_check_against_their_own_record_and_a_step_with_none_is_exit_2_1586(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "a.test.sh"
    suite.write_text("case one\n")
    first, second, third = "step one adds case one", "step two adds case two", "step three never recorded"
    paths = {step: run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].rstrip("\n") for step in (first, second, third)}

    recorded_first = run_cli(tests_frozen, ["record", paths[first], "a.test.sh"], cwd=tmp_path)[0]
    suite.write_text("case one\ncase two\n")
    recorded_second = run_cli(tests_frozen, ["record", paths[second], "a.test.sh"], cwd=tmp_path)[0]
    checks = {step: run_cli(tests_frozen, ["check", paths[step]], cwd=tmp_path)[:2] for step in (first, second, third)}

    assert (recorded_first, recorded_second, checks) == (
        0, 0, {first: (1, "a.test.sh\n"), second: (0, ""), third: (2, "")})


@pytest.mark.parametrize("mark", ["⟦suite-repair⟧", "⟦ci-repair⟧"])
def test_a_repair_marked_step_is_never_frozen_so_an_edit_to_its_test_file_is_not_rejected_and_no_record_is_written_1586(
        tmp_path, run_cli, tests_frozen, mark):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "a.test.sh"
    suite.write_text("case one, stale\n")
    step = "fix the full-suite failure: a.test.sh — FAIL - case one " + mark

    recorded = run_cli(tests_frozen, ["record", "--step", step, "a.test.sh"], cwd=tmp_path)
    suite.write_text("case one, repaired\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (recorded, checked, sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == ((0, "", ""), (0, "", ""), [])



@pytest.mark.parametrize("value", ["::name", "path::"])
def test_record_refuses_a_red_case_value_with_an_empty_half_around_the_double_colon_and_writes_no_record_2269(
        tmp_path, run_cli, tests_frozen, value):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "a.test.sh").write_text("case one\n")

    code, out, err = run_cli(tests_frozen, ["record", ".tdd/x.record", "--red-case", value, "a.test.sh"], cwd=tmp_path)

    assert (code, out, "--red-case" in err and value in err, sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == (
        2, "", True, [])


def test_record_refuses_a_red_case_that_no_longer_exists_in_its_test_file_naming_it_and_keeps_the_old_record_2269(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_a.py"
    suite.write_text("def test_kept():\n    assert 1\n")
    record = tmp_path / ".tdd" / "x.record"
    record.write_text("old record\n")

    code, out, err = run_cli(
        tests_frozen, ["record", ".tdd/x.record", "--red-case", "test_a.py::test_gone", "test_a.py"], cwd=tmp_path)

    assert (code, "test_a.py::test_gone" in out, record.read_text()) == (1, True, "old record\n")


def test_record_with_a_red_case_still_present_records_exactly_as_without_it_2269(tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "test_a.py").write_text("def test_kept():\n    assert 1\n")

    plain = run_cli(tests_frozen, ["record", ".tdd/plain.record", "test_a.py"], cwd=tmp_path)
    withcase = run_cli(
        tests_frozen, ["record", ".tdd/case.record", "--red-case", "test_a.py::test_kept", "test_a.py"], cwd=tmp_path)

    recorded = {p.name: p.read_text() for p in (tmp_path / ".tdd").iterdir()}
    assert (plain[0], withcase, recorded.get("case.record")) == (0, (0, "", ""), recorded["plain.record"])


def test_record_step_with_a_red_case_whose_test_file_is_gone_exits_1_naming_it_and_writes_no_record_2269(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "test_b.py").write_text("def test_b():\n    assert 1\n")

    code, out, err = run_cli(
        tests_frozen,
        ["record", "--step", "step one", "--red-case", "gone/test_a.py::test_gone", "test_b.py"],
        cwd=tmp_path)

    assert (code, "gone/test_a.py::test_gone" in out, "Traceback" in err, sorted(p.name for p in tmp_path.rglob("*"))) == (
        1, True, False, ["test_b.py"])
