"""In-process cases for veri/tests_frozen.py, the module tests-frozen.sh is a shim over."""
import hashlib
import importlib
import types

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


def test_record_with_a_red_case_flag_and_no_value_is_exit_2_printing_the_usage_line_without_a_traceback_2269(
        tmp_path, run_cli, tests_frozen):
    code, out, err = run_cli(tests_frozen, ["record", "--step", "x", "--red-case"], cwd=tmp_path)

    assert (code, out, tests_frozen.USAGE in err, "Traceback" in err, sorted(p.name for p in tmp_path.rglob("*"))) == (
        2, "", True, False, [])


def test_record_resolves_a_red_case_naming_a_vitest_it_or_test_in_a_ts_file_and_still_exits_1_for_one_the_file_lacks_2426(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "a.test.ts").write_text(
        'import { it, test } from "vitest";\n'
        'it("adds two numbers", () => {\n  expect(1 + 1).toBe(2);\n});\n'
        'test("subtracts", () => {\n  expect(2 - 1).toBe(1);\n});\n')

    answers = [
        run_cli(tests_frozen, ["record", ".tdd/%s.record" % name, "--red-case", "a.test.ts::" + case, "a.test.ts"],
                cwd=tmp_path)
        for name, case in (("it", "adds two numbers"), ("test", "subtracts"), ("gone", "divides"))]

    assert [(code, out.strip()) for code, out, _ in answers] == [
        (0, ""), (0, ""), (1, "tests-frozen.sh: red case a.test.ts::divides no longer exists")]


def test_check_on_a_ts_file_flags_an_edit_inside_a_recorded_it_body_and_not_one_outside_every_case_2426(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "a.test.ts"
    original = (
        'import { it, test } from "vitest";\n'
        'it("adds two numbers", () => {\n  expect(1 + 1).toBe(2);\n});\n'
        'test("subtracts", () => {\n  expect(2 - 1).toBe(1);\n});\n')
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    step = "the case passes: repairs the fixture 'db' in a.test.ts, reproduced by a case in a.test.ts ⟦fixture-repair⟧"
    recorded = run_cli(tests_frozen, ["record", "--step", step, "a.test.ts"], cwd=tmp_path)[0]

    suite.write_text(original.replace('"vitest"', '"vitest/globals"'))
    outside = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]
    suite.write_text(original.replace("toBe(2)", "toBe(3)"))
    inside = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, outside, inside) == (0, (0, ""), (1, "a.test.ts\n"))


def test_check_earlier_except_a_vitest_case_by_title_leaves_it_unreported_while_an_unexcepted_one_still_is_2426(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "a.test.ts"
    original = (
        'import { it, test } from "vitest";\n'
        'it("adds two numbers", () => {\n  expect(1 + 1).toBe(2);\n});\n'
        'test("subtracts", () => {\n  expect(2 - 1).toBe(1);\n});\n')
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    earlier, later = "the earlier step", "the later step"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, later))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "a.test.ts"], cwd=tmp_path)[0]
    suite.write_text(original.replace("toBe(2)", "toBe(3)").replace("toBe(1)", "toBe(0)"))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later, "--except", "adds two numbers"],
                     cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "subtracts (%s)\n" % earlier))


def test_differing_tests_counts_a_spec_ts_and_a_ts_file_under_tests_dir_as_test_files_and_not_a_plain_ts_or_d_ts_2426(
        tmp_path, tests_frozen, monkeypatch):
    monkeypatch.chdir(tmp_path)
    listings = {"diff": b"src/app.spec.ts\0src/app.ts\0", "ls-files": b"src/__tests__/sum.ts\0src/types.d.ts\0"}

    class Done:
        returncode = 0

        def __init__(self, stdout):
            self.stdout = stdout

    monkeypatch.setattr(tests_frozen.subprocess, "run", lambda command, **_: Done(listings[command[1]]))

    assert tests_frozen._differing_tests() == ["src/app.spec.ts", "src/__tests__/sum.ts"]


def test_check_earlier_except_the_current_steps_own_case_still_exits_1_naming_an_earlier_steps_case_the_repair_changed_2596(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_suite.py"
    original = ("def test_earlier_case():\n    assert 1 + 1 == 2\n\n\n"
                "def test_current_case():\n    assert 2 - 1 == 1\n")
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    earlier, later = "the earlier step", "the current step"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, later))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "test_suite.py"], cwd=tmp_path)[0]
    suite.write_text(original.replace("1 + 1 == 2", "1 + 1 == 3").replace("2 - 1 == 1", "2 - 1 == 0"))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later, "--except", "test_current_case"],
                     cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "test_earlier_case (%s)\n" % earlier))


def test_check_earlier_ignores_the_record_of_an_unchecked_step_and_still_flags_the_same_record_once_ticked_2563(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_suite.py"
    original = "def test_bailed_case():\n    assert 1 + 1 == 2\n"
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    first, bailed, current = "step A", "step B", "step C"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (first, bailed, current))
    recorded = run_cli(tests_frozen, ["record", "--step", bailed, "test_suite.py"], cwd=tmp_path)[0]
    suite.write_text(original.replace("1 + 1 == 2", "1 + 1 == 3"))
    ticked = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (first, bailed, current))

    unchecked = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, ticked, unchecked) == (0, (1, "test_bailed_case (%s)\n" % bailed), (0, ""))


def test_check_earlier_still_flags_the_record_of_a_step_ticked_green_with_its_refactor_pending_2563(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_suite.py"
    original = "def test_pending_case():\n    assert 1 + 1 == 2\n"
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    first, pending, current = "step A", "step B", "step C"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s ⟂ refactor pending\n- [ ] %s\n" % (first, pending, current))
    recorded = run_cli(tests_frozen, ["record", "--step", pending + " ⟂ refactor pending", "test_suite.py"],
                       cwd=tmp_path)[0]
    suite.write_text(original.replace("1 + 1 == 2", "1 + 1 == 3"))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "test_pending_case (%s ⟂ refactor pending)\n" % pending))


def test_check_earlier_skips_a_recorded_case_in_no_revision_of_its_file_naming_it_with_its_step_and_record_2637(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_suite.py"
    suite.write_text("def test_ghost():\n    assert 1 + 1 == 2\n")
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_renamed_to", lambda name, case, digest, text, consumed: None)
    monkeypatch.setattr(tests_frozen, "_revisions", lambda name: ["0" * 40], raising=False)
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "1" * 40)
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, later = "the earlier step B", "the later step C"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, later))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "test_suite.py"], cwd=tmp_path)[0]
    suite.write_text("def test_other():\n    assert 2 - 1 == 1\n")
    record = ".tdd/tests-frozen-%s.record" % hashlib.sha256(earlier.encode()).hexdigest()[:16]

    code, out, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (recorded, code, out) == (0, 0, "")
    assert [phrase in err for phrase in ("test_ghost", earlier, record, "no revision of this branch", "skipped")] == [
        True] * 5


def test_check_earlier_still_flags_a_recorded_case_a_reachable_revision_held_and_the_tree_lost_2637(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_suite.py"
    suite.write_text("def test_real():\n    assert 1 + 1 == 2\n")
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {"test_real": "def test_real():\n    pass\n"})
    monkeypatch.setattr(tests_frozen, "_renamed_to", lambda name, case, digest, text, consumed: None)
    monkeypatch.setattr(tests_frozen, "_revisions", lambda name: ["0" * 40], raising=False)
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "1" * 40)
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, later = "the earlier step B", "the later step C"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, later))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "test_suite.py"], cwd=tmp_path)[0]
    suite.write_text("def test_other():\n    assert 2 - 1 == 1\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (recorded, code, out) == (0, 1, "test_real (%s)\n" % earlier)


def test_check_earlier_reports_the_changed_case_alone_on_stdout_and_names_the_ghost_beside_it_as_skipped_2637(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_suite.py"
    suite.write_text("def test_ghost():\n    assert 1 + 1 == 2\n\n\ndef test_changed():\n    assert 2 - 1 == 1\n")
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_renamed_to", lambda name, case, digest, text, consumed: None)
    monkeypatch.setattr(tests_frozen, "_revisions", lambda name: ["0" * 40], raising=False)
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "1" * 40)
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, later = "the earlier step B", "the later step C"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, later))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "test_suite.py"], cwd=tmp_path)[0]
    suite.write_text("def test_changed():\n    assert 2 - 1 == 0\n")

    code, out, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (recorded, code, out) == (0, 1, "test_changed (%s)\n" % earlier)
    assert "test_ghost" in err and "skipped" in err


def test_check_earlier_leaves_a_vitest_it_case_unchanged_when_a_second_case_is_appended_after_it_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    original = 'describe("sum", () => {\n  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\n'
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "sum.test.ts"], cwd=tmp_path)[0]
    suite.write_text(original.replace(
        "  });\n});\n", '  });\n\n  it("subtracts", () => {\n    expect(3 - 1).toBe(2);\n  });\n});\n'))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_earlier_leaves_a_vitest_it_case_last_in_its_describe_unchanged_when_a_case_is_inserted_into_either_describe_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    original = (
        'describe("sum", () => {\n  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\n\n'
        'describe("diff", () => {\n  it("subtracts", () => {\n    expect(3 - 1).toBe(2);\n  });\n});\n')
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "sum.test.ts"], cwd=tmp_path)[0]
    new_case = '  it("multiplies", () => {\n    expect(2 * 2).toBe(4);\n  });\n'

    suite.write_text(original.replace("  });\n});\n\ndescribe", "  });\n\n" + new_case + "});\n\ndescribe"))
    into_first = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]
    suite.write_text(original[:-len("});\n")] + "\n" + new_case + "});\n")
    into_second = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, into_first, into_second) == (0, (0, ""), (0, ""))


def test_check_earlier_leaves_a_vitest_it_case_last_before_a_finish_trailer_unchanged_when_a_case_is_appended_after_it_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    original = 'describe("sum", () => {\n  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\nfinish\n'
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "sum.test.ts"], cwd=tmp_path)[0]
    suite.write_text(original.replace(
        "  });\n});\n", '  });\n\n  it("subtracts", () => {\n    expect(3 - 1).toBe(2);\n  });\n});\n'))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_step_exits_0_for_a_vitest_it_case_after_a_case_is_appended_to_the_file_that_recorded_it_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    original = 'describe("sum", () => {\n  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\n'
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    step = "the case passes: repairs the fixture 'db' in sum.test.ts, reproduced by a case in sum.test.ts ⟦fixture-repair⟧"
    recorded = run_cli(tests_frozen, ["record", "--step", step, "sum.test.ts"], cwd=tmp_path)[0]
    suite.write_text(original.replace(
        "  });\n});\n", '  });\n\n  it("subtracts", () => {\n    expect(3 - 1).toBe(2);\n  });\n});\n'))

    answer = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_earlier_flags_an_edit_inside_a_recorded_vitest_it_case_naming_it_with_cases_appended_around_it_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    original = 'describe("sum", () => {\n  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\n'
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "sum.test.ts"], cwd=tmp_path)[0]
    edited = original.replace("toBe(2)", "toBe(3)")
    suite.write_text(edited.replace(
        "  });\n});\n", '  });\n\n  it("subtracts", () => {\n    expect(3 - 1).toBe(2);\n  });\n});\n'))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "adds (%s)\n" % earlier))


def test_record_digests_a_python_def_case_over_its_ast_span_decorators_included_whatever_follows_it_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_sum.py"
    adds = '@pytest.mark.slow\ndef test_adds():\n    assert 1 + 1 == 2\n'
    suite.write_text('import pytest\n\n\n%s\n\ndef test_subtracts():\n    assert 3 - 1 == 2\n' % adds)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    step = "step A"

    recorded = run_cli(tests_frozen, ["record", "--step", step, "test_sum.py"], cwd=tmp_path)[0]

    record = (tmp_path / tests_frozen._record_path(step)).read_text()
    digest = hashlib.sha256(adds.rstrip().encode()).hexdigest()
    assert (recorded, "body: test_sum.py\ttest_adds\t%s\n" % digest in record) == (0, True)


def test_check_earlier_exits_0_for_a_format_2_record_of_a_vitest_it_case_digested_over_the_old_extent_against_the_unchanged_file_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    adds = '  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n'
    suite.write_text('describe("sum", () => {\n%s});\n' % adds)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    old_extent = (adds + "});\n").strip().rstrip()
    record = tmp_path / tests_frozen._record_path(earlier)
    record.write_text("deadbeef  sum.test.ts\nformat: 2\ncase: adds\nbody: sum.test.ts\tadds\t%s\n"
                      % hashlib.sha256(old_extent.encode()).hexdigest())

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert answer == (0, "")


def test_check_earlier_exits_0_for_a_format_2_record_of_a_vitest_it_case_followed_by_a_second_case_digested_over_the_old_extent_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    adds = '  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n\n'
    subtracts = '  it("subtracts", () => {\n    expect(3 - 1).toBe(2);\n  });\n});\n'
    suite.write_text('describe("sum", () => {\n%s%s' % (adds, subtracts))
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    record = tmp_path / tests_frozen._record_path(earlier)
    record.write_text("deadbeef  sum.test.ts\nformat: 2\ncase: adds\nbody: sum.test.ts\tadds\t%s\n"
                      % hashlib.sha256(adds.strip().encode()).hexdigest())

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert answer == (0, "")


def test_check_earlier_flags_an_edit_inside_a_vitest_it_case_of_a_format_2_record_digested_over_the_old_extent_naming_it_2591(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "sum.test.ts"
    adds = '  it("adds", () => {\n    expect(1 + 1).toBe(2);\n  });\n'
    suite.write_text('describe("sum", () => {\n%s});\n' % adds.replace("toBe(2)", "toBe(3)"))
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    old_extent = (adds + "});\n").strip()
    record = tmp_path / tests_frozen._record_path(earlier)
    record.write_text("deadbeef  sum.test.ts\nformat: 2\ncase: adds\nbody: sum.test.ts\tadds\t%s\n"
                      % hashlib.sha256(old_extent.encode()).hexdigest())

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert answer == (1, "adds (%s)\n" % earlier)


def test_rerecord_rebased_with_no_pre_rebase_sha_or_an_extra_argument_is_exit_2_with_the_usage_and_no_record_2552(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd" / "issue-1.md"
    ledger.write_text("- [x] step\n")

    answers = [run_cli(tests_frozen, argv, cwd=tmp_path)
               for argv in (["rerecord-rebased", str(ledger)], ["rerecord-rebased", str(ledger), "abc1234", "extra"])]

    assert ([(code, out, "rerecord-rebased <ledger> <pre-rebase-sha>" in err) for code, out, err in answers],
            sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == (
        [(2, "", True), (2, "", True)], ["issue-1.md"])


def test_check_earlier_exits_0_for_a_python_def_case_sharing_its_name_with_another_unchanged_since_head_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_dup.py"
    suite.write_text("def test_dup():\n    assert 1 + 1 == 2\n\n\ndef test_dup():\n    assert 2 + 2 == 4\n")
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)

    def git_show(command, **kwargs):
        assert command[:2] == ["git", "show"]
        return types.SimpleNamespace(returncode=0, stdout=suite.read_bytes(), stderr=b"")

    monkeypatch.setattr(tests_frozen.subprocess, "run", git_show)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "test_dup.py"], cwd=tmp_path)[0]

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_earlier_exits_0_for_a_js_call_form_case_sharing_its_name_under_two_describes_unchanged_since_head_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "dup.test.ts"
    suite.write_text(
        'describe("a", () => {\n  it("dup", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\n\n'
        'describe("b", () => {\n  it("dup", () => {\n    expect(2 + 2).toBe(4);\n  });\n});\n')
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)

    def git_show(command, **kwargs):
        assert command[:2] == ["git", "show"]
        return types.SimpleNamespace(returncode=0, stdout=suite.read_bytes(), stderr=b"")

    monkeypatch.setattr(tests_frozen.subprocess, "run", git_show)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "dup.test.ts"], cwd=tmp_path)[0]

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_step_exits_0_for_a_fixture_repair_step_of_a_file_with_two_python_def_cases_sharing_a_name_after_an_edit_outside_both_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_dup.py"
    original = "def test_dup():\n    assert 1 + 1 == 2\n\n\ndef test_dup():\n    assert 2 + 2 == 4\n"
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_head_cases_all", lambda name: [])
    step = "the case passes: repairs the fixture 'db' in test_dup.py, reproduced by a case in test_dup.py ⟦fixture-repair⟧"
    recorded = run_cli(tests_frozen, ["record", "--step", step, "test_dup.py"], cwd=tmp_path)[0]
    suite.write_text("import os\n\n\n" + original)

    answer = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_step_exits_0_for_a_fixture_repair_step_of_a_file_with_two_js_call_form_cases_sharing_a_name_after_an_edit_outside_both_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "dup.test.ts"
    original = (
        'describe("a", () => {\n  it("dup", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\n\n'
        'describe("b", () => {\n  it("dup", () => {\n    expect(2 + 2).toBe(4);\n  });\n});\n')
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_head_cases_all", lambda name: [])
    step = "the case passes: repairs the fixture 'db' in dup.test.ts, reproduced by a case in dup.test.ts ⟦fixture-repair⟧"
    recorded = run_cli(tests_frozen, ["record", "--step", step, "dup.test.ts"], cwd=tmp_path)[0]
    suite.write_text("import { expect } from 'vitest';\n\n" + original)

    answer = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_record_step_writes_only_the_edited_twin_of_two_python_def_cases_sharing_a_name_and_leaves_the_untouched_one_out_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_dup.py"
    at_head = "def test_dup():\n    assert 1 + 1 == 2\n\n\ndef test_dup():\n    assert 2 + 2 == 4\n"
    suite.write_text(at_head.replace("2 + 2 == 4", "3 + 3 == 6"))
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])

    def git_show(command, **kwargs):
        assert command[:2] == ["git", "show"]
        return types.SimpleNamespace(returncode=0, stdout=at_head.encode(), stderr=b"")

    monkeypatch.setattr(tests_frozen.subprocess, "run", git_show)
    step = "step A"
    recorded = run_cli(tests_frozen, ["record", "--step", step, "test_dup.py"], cwd=tmp_path)
    record = run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()

    assert recorded[:2] == (0, "")
    written = (tmp_path / record).read_text().splitlines()
    digests = [line.split("\t")[2] for line in written if line.startswith("body: ")]

    assert digests == [tests_frozen._body_digest("def test_dup():\n    assert 3 + 3 == 6")]


def test_check_earlier_flags_an_edit_inside_the_first_of_two_python_def_cases_sharing_a_name_both_added_since_head_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_dup.py"
    original = "def test_dup():\n    assert 1 + 1 == 2\n\n\ndef test_dup():\n    assert 2 + 2 == 4\n"
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_head_cases_all", lambda name: [])
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "test_dup.py"], cwd=tmp_path)[0]
    suite.write_text(original.replace("1 + 1 == 2", "1 + 2 == 3"))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "test_dup (%s)\n" % earlier))


def test_check_earlier_flags_an_edit_inside_the_second_of_two_python_def_cases_sharing_a_name_both_added_since_head_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_dup.py"
    original = "def test_dup():\n    assert 1 + 1 == 2\n\n\ndef test_dup():\n    assert 2 + 2 == 4\n"
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_head_cases_all", lambda name: [])
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    earlier, current = "step A", "step B"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    recorded = run_cli(tests_frozen, ["record", "--step", earlier, "test_dup.py"], cwd=tmp_path)[0]
    suite.write_text(original.replace("2 + 2 == 4", "2 + 3 == 5"))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "test_dup (%s)\n" % earlier))


def _twins_added_since_head(tmp_path, tests_frozen, monkeypatch, name, original):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / name
    suite.write_text(original)
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_head_cases_all", lambda name: [])
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] step A\n- [ ] step B\n")
    return suite, ledger


_PY_TWINS = "def test_dup():\n    assert 1 + 1 == 2\n\n\ndef test_dup():\n    assert 2 + 2 == 4\n"
_JS_TWINS = ('describe("a", () => {\n  it("dup", () => {\n    expect(1 + 1).toBe(2);\n  });\n});\n\n'
             'describe("b", () => {\n  it("dup", () => {\n    expect(2 + 2).toBe(4);\n  });\n});\n')


def test_check_earlier_exits_0_for_two_python_def_cases_sharing_a_name_both_added_since_head_and_left_unchanged_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, ledger = _twins_added_since_head(tmp_path, tests_frozen, monkeypatch, "test_dup.py", _PY_TWINS)
    recorded = run_cli(tests_frozen, ["record", "--step", "step A", "test_dup.py"], cwd=tmp_path)[0]

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", "step B"], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_earlier_exits_0_for_two_js_call_form_cases_sharing_a_name_under_two_describes_both_added_since_head_and_left_unchanged_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, ledger = _twins_added_since_head(tmp_path, tests_frozen, monkeypatch, "dup.test.ts", _JS_TWINS)
    recorded = run_cli(tests_frozen, ["record", "--step", "step A", "dup.test.ts"], cwd=tmp_path)[0]

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", "step B"], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (0, ""))


def test_check_earlier_flags_an_edit_inside_the_first_of_two_js_call_form_cases_sharing_a_name_both_added_since_head_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, ledger = _twins_added_since_head(tmp_path, tests_frozen, monkeypatch, "dup.test.ts", _JS_TWINS)
    recorded = run_cli(tests_frozen, ["record", "--step", "step A", "dup.test.ts"], cwd=tmp_path)[0]
    suite.write_text(_JS_TWINS.replace("expect(1 + 1).toBe(2)", "expect(1 + 2).toBe(3)"))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", "step B"], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "dup (step A)\n"))


def test_check_earlier_flags_an_edit_inside_the_second_of_two_js_call_form_cases_sharing_a_name_both_added_since_head_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, ledger = _twins_added_since_head(tmp_path, tests_frozen, monkeypatch, "dup.test.ts", _JS_TWINS)
    recorded = run_cli(tests_frozen, ["record", "--step", "step A", "dup.test.ts"], cwd=tmp_path)[0]
    suite.write_text(_JS_TWINS.replace("expect(2 + 2).toBe(4)", "expect(2 + 3).toBe(5)"))

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", "step B"], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "dup (step A)\n"))


def _twins_one_edited_since_head(tmp_path, tests_frozen, monkeypatch, edited_first):
    """A step records only the twin it edited (one digest) out of two same-named twins that head holds."""
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_dup.py"
    at_head = _PY_TWINS
    suite.write_text(at_head.replace("1 + 1 == 2", "1 + 2 == 3") if edited_first
                     else at_head.replace("2 + 2 == 4", "3 + 3 == 6"))
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_has_head", lambda: True)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_work_tree_hash", lambda: "tree")
    monkeypatch.setattr(tests_frozen, "_write_pass_marker", lambda step, tree: None)
    monkeypatch.setattr(tests_frozen.subprocess, "run", lambda command, **kwargs: types.SimpleNamespace(
        returncode=0, stdout=at_head.encode(), stderr=b""))
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] step A\n- [ ] step B\n")
    return suite, ledger


def test_check_earlier_exits_0_when_a_step_recorded_only_the_first_of_two_same_named_twins_and_both_are_unchanged_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, ledger = _twins_one_edited_since_head(tmp_path, tests_frozen, monkeypatch, edited_first=True)
    recorded = run_cli(tests_frozen, ["record", "--step", "step A", "test_dup.py"], cwd=tmp_path)[0]
    path = run_cli(tests_frozen, ["path", "step A"], cwd=tmp_path)[1].strip()
    digests = [l for l in (tmp_path / path).read_text().splitlines() if l.startswith("body: ")]

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", "step B"], cwd=tmp_path)[:2]

    assert (recorded, len(digests), answer) == (0, 1, (0, ""))


def test_check_earlier_exits_0_when_a_step_recorded_only_the_second_of_two_same_named_twins_and_both_are_unchanged_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, ledger = _twins_one_edited_since_head(tmp_path, tests_frozen, monkeypatch, edited_first=False)
    recorded = run_cli(tests_frozen, ["record", "--step", "step A", "test_dup.py"], cwd=tmp_path)[0]
    path = run_cli(tests_frozen, ["path", "step A"], cwd=tmp_path)[1].strip()
    digests = [l for l in (tmp_path / path).read_text().splitlines() if l.startswith("body: ")]

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", "step B"], cwd=tmp_path)[:2]

    assert (recorded, len(digests), answer) == (0, 1, (0, ""))


def test_check_earlier_flags_a_recorded_twin_removed_while_the_other_same_named_twin_is_unchanged_2543(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, ledger = _twins_added_since_head(tmp_path, tests_frozen, monkeypatch, "test_dup.py", _PY_TWINS)
    recorded = run_cli(tests_frozen, ["record", "--step", "step A", "test_dup.py"], cwd=tmp_path)[0]
    suite.write_text("def test_dup():\n    assert 2 + 2 == 4\n")

    answer = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", "step B"], cwd=tmp_path)[:2]

    assert (recorded, answer) == (0, (1, "test_dup (step A)\n"))


def _rerecord_fixture(tmp_path, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(tests_frozen, "_refused_outside_repository", lambda: False)
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(tests_frozen, "_differing_tests", lambda: [])
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: {})
    monkeypatch.setattr(tests_frozen, "_revisions", lambda name: [])
    return tmp_path / "test_suite.py"


def _recorded_names(tmp_path, tests_frozen, step):
    record = (tmp_path / tests_frozen._record_path(step)).read_text()
    return sorted(l[6:] for l in record.splitlines() if l.startswith("case: "))


def test_rerecord_on_head_keeps_every_recorded_case_still_there_and_never_one_a_later_step_added_to_the_file_2673(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = _rerecord_fixture(tmp_path, tests_frozen, monkeypatch)
    step = "the step that owns the cases"
    suite.write_text("def test_one():\n    assert 1\n\n\ndef test_two():\n    assert 2\n")
    recorded = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)[0]
    suite.write_text("def test_one():\n    assert 1\n\n\ndef test_later_step():\n    assert 9\n\n\n"
                     "def test_two():\n    assert 2\n\n\ndef test_last_step():\n    assert 8\n")
    head = dict(tests_frozen._cases(suite.read_text()))
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: head)
    monkeypatch.setattr(tests_frozen, "_step_commits", lambda s: {"mine"})
    monkeypatch.setattr(tests_frozen, "_introduced_by", lambda name, own: set())

    rerecorded = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)[0]

    assert (recorded, rerecorded, _recorded_names(tmp_path, tests_frozen, step)) == (0, 0, ["test_one", "test_two"])


def test_rerecord_on_head_exits_2_naming_the_step_and_file_and_keeps_the_record_when_every_recorded_case_is_gone_2673(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = _rerecord_fixture(tmp_path, tests_frozen, monkeypatch)
    step = "the step that owns the cases"
    suite.write_text("def test_one():\n    assert 1\n")
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    kept = (tmp_path / tests_frozen._record_path(step)).read_text()
    suite.write_text("def test_other_step():\n    assert 9\n")
    head = dict(tests_frozen._cases(suite.read_text()))
    monkeypatch.setattr(tests_frozen, "_cases_at", lambda rev, name: head)
    monkeypatch.setattr(tests_frozen, "_step_commits", lambda s: {"mine"})
    monkeypatch.setattr(tests_frozen, "_introduced_by", lambda name, own: set())

    code, _, err = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)

    assert (code, step in err and "test_suite.py" in err, (tmp_path / tests_frozen._record_path(step)).read_text()) == (
        2, True, kept)


@pytest.mark.parametrize("quote", ['"', "'"])
def test_cases_records_a_js_title_holding_an_escaped_quote_of_its_own_kind_whole_and_unescaped_2765(
        tests_frozen, quote):
    title = "a \\%sb\\%s c" % (quote, quote)
    text = "it(%s%s%s, () => {\n  expect(1).toBe(1);\n});\n" % (quote, title, quote)

    assert [name for name, _ in tests_frozen._cases(text)] == ["a %sb%s c" % (quote, quote)]


def test_cases_records_two_js_titles_differing_only_after_an_escaped_quote_as_two_cases_2765(tests_frozen):
    text = ('it("shows \\"¿Ya contrataste?", () => {\n  expect(1).toBe(1);\n});\n\n'
            'it("shows \\"Validando", () => {\n  expect(2).toBe(2);\n});\n')

    assert [name for name, _ in tests_frozen._cases(text)] == ['shows "¿Ya contrataste?', 'shows "Validando']


def test_cases_records_a_js_backtick_title_without_interpolation_2765(tests_frozen):
    text = "it(`shows the login page`, () => {\n  expect(1).toBe(1);\n});\n"

    assert [name for name, _ in tests_frozen._cases(text)] == ["shows the login page"]
