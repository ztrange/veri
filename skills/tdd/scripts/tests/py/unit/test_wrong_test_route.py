"""In-process cases for veri/wrong_test_route.py, the module wrong-test-route.sh is a shim over."""
import hashlib
import importlib
import os

import pytest

from conftest import ROOT


def test_main_1621_routes_a_green_whose_wrong_test_names_a_contradicted_case_to_a_red_over_that_case(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    contradicted = "test_main_counts_a_repair_text_as_a_repair"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n" % contradicted)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % contradicted)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % contradicted)


def test_main_1621_prints_revise_and_exits_3_when_the_green_report_has_no_wrong_test_line(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def test_main_returns_zero():\n    pass\n")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nVERDICT: REJECT\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1621_exits_2_with_nothing_on_stdout_when_the_green_report_is_a_directory(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    report = tmp_path / "green-report.txt"
    report.mkdir()

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (2, "")


@pytest.mark.tree_audit("the repository's own tests directories, searched for the case a WRONG_TEST names")
def test_main_1621_finds_a_real_pytest_function_and_a_real_bash_suite_case_from_the_repository_root(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    pytest_case = "test_a_planted_develop_prompt_that_makes_no_commit_and_the_real_prompts_directory_are_clean"
    bash_case = "harvest-usage.sh run through a symlink to the skill directory and from another working directory appends the same usage event and exits as when run in place"
    results = []
    for line in ("WRONG_TEST: %s asserts the opposite of the criterion" % pytest_case,
                 "WRONG_TEST: the case `%s` asserts the opposite of the criterion" % bash_case):
        report = tmp_path / ("report-%d.txt" % len(results))
        report.write_text("SUITE: make test\n" + line + "\n")
        code, stdout, stderr = run_cli(
            wrong_test_route, [str(report), "test_main_returns_zero"], cwd=ROOT)
        results.append((code, stdout))

    assert results == [(0, "red %s\n" % pytest_case), (0, "red %s\n" % bash_case)]


@pytest.mark.tree_audit("the repository's own tests directories, searched for the case a WRONG_TEST names")
def test_main_1621_refuses_a_wrong_test_naming_no_case_only_its_own_red_or_a_missing_case_and_a_bad_argument_list(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    own_id = "test_a_planted_develop_prompt_that_makes_no_commit_and_the_real_prompts_directory_are_clean"
    usage = "usage: wrong-test-route.sh <green-report> <red-test-id>\n"
    lines = ("WRONG_TEST: the criterion contradicts nothing I can name",
             "WRONG_TEST: %s asserts the opposite of the criterion" % own_id,
             "WRONG_TEST: test_1621_no_such_case_exists_anywhere_in_the_tree asserts the opposite")
    results = []
    for number, line in enumerate(lines):
        report = tmp_path / ("report-%d.txt" % number)
        report.write_text("SUITE: make test\n" + line + "\n")
        code, stdout, stderr = run_cli(wrong_test_route, [str(report), own_id], cwd=ROOT)
        results.append((code, stdout))
    for argv in ([], [str(report)], [str(report), own_id, "extra"], ["", own_id], [str(report), ""]):
        code, stdout, stderr = run_cli(wrong_test_route, argv, cwd=ROOT)
        results.append((code, stdout, stderr))

    assert results == [(3, "revise\n")] * 3 + [(2, "", usage)] * 5


def test_main_1621_routes_a_revise_green_report_in_the_revise_template_shape_to_a_red_over_the_contradicted_case(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    contradicted = "test_main_counts_a_repair_text_as_a_repair"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n" % contradicted)
    report = tmp_path / "revise-green-report.txt"
    report.write_text(
        "OUTCOME: the revised green still fails the suite\n"
        "AGAINST_UNMODIFIED: N/A\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % contradicted)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % contradicted)


@pytest.mark.tree_audit("the repository's own tests directories, searched for the case a WRONG_TEST names")
def test_main_1621_prints_revise_when_a_wrong_test_names_only_the_step_own_red_passed_as_a_pytest_node_id(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    own_case = "test_a_planted_develop_prompt_that_makes_no_commit_and_the_real_prompts_directory_are_clean"
    own_id = "skills/tdd/scripts/tests/py/unit/test_commit_suffix" + ".py::" + own_case
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % own_case)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), own_id], cwd=ROOT)

    assert (code, stdout) == (3, "revise\n")


@pytest.mark.tree_audit("the repository's own tests directories, searched for the case a WRONG_TEST names")
def test_main_1621_prints_revise_when_a_wrong_test_quotes_a_string_in_a_real_suite_that_is_no_declared_case_name(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    not_a_name = ("through a symlink to the skill directory, from another working directory, "
                  "answers as in place")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: the case `%s` asserts the opposite of the criterion\n" % not_a_name)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=ROOT)

    assert (code, stdout) == (3, "revise\n")


@pytest.mark.tree_audit("the repository's own tests directories, searched for the case a WRONG_TEST names")
def test_main_1621_routes_a_wrong_test_naming_a_real_case_of_a_docs_tests_suite_to_a_red_over_that_case(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    docs_case = "#533 no chunk in docs/wt/commentary.py claims a line past the end of its script"
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: the case `%s` asserts the opposite of the criterion\n" % docs_case)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=ROOT)

    assert (code, stdout) == (0, "red %s\n" % docs_case)


def test_main_1621_routes_a_wrong_test_naming_a_case_in_a_repo_whose_tests_live_under_test_or_spec_to_red(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    pytest_case = "test_main_counts_a_repair_text_as_a_repair"
    bash_case = "a repair text counts as a repair"
    results = []
    for directory, filename, body, case in (
            ("test", "test_" + "ledger" + ".py", "def %s():\n    pass\n" % pytest_case, pytest_case),
            ("spec", "ledger" + ".test" + ".sh", 'name="%s"\nrun_case\n' % bash_case, bash_case)):
        repo = tmp_path / directory
        (repo / directory).mkdir(parents=True)
        (repo / directory / filename).write_text(body)
        report = repo / "green-report.txt"
        report.write_text(
            "SUITE: make test\n"
            "WRONG_TEST: the case `%s` asserts the opposite of the criterion\n" % case)
        code, stdout, stderr = run_cli(
            wrong_test_route, [str(report), "test_main_returns_zero"], cwd=repo)
        results.append((code, stdout))

    assert results == [(0, "red %s\n" % pytest_case), (0, "red %s\n" % bash_case)]


@pytest.mark.tree_audit("the repository's own Python files, searched for the case a WRONG_TEST names")
def test_main_1621_prints_revise_when_a_wrong_test_names_a_production_function_that_is_no_pytest_test(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: the case `main` asserts the opposite of the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=ROOT)

    assert (code, stdout) == (3, "revise\n")


def test_main_1621_counts_a_test_prefixed_python_function_only_when_defined_in_a_test_file(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    case = "test_totals_an_invoice"
    results = []
    for directory, filename in (("helpers", "pkg/helpers.py"), ("suffixed", "pkg/billing" + "_test" + ".py")):
        repo = tmp_path / directory
        (repo / "pkg").mkdir(parents=True)
        (repo / filename).write_text("def %s():\n    pass\n" % case)
        report = repo / "green-report.txt"
        report.write_text(
            "SUITE: make test\n"
            "WRONG_TEST: the case `%s` asserts the opposite of the criterion\n" % case)
        code, stdout, stderr = run_cli(
            wrong_test_route, [str(report), "test_main_returns_zero"], cwd=repo)
        results.append((code, stdout))

    assert results == [(3, "revise\n"), (0, "red %s\n" % case)]


def test_main_1736_prints_revise_when_the_named_case_exists_only_in_a_test_file_under_dot_git(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    case = "test_main_counts_a_repair_text_as_a_repair"
    hidden = tmp_path / ".git" / "hooks"
    hidden.mkdir(parents=True)
    (hidden / ("test_" + "ledger" + ".py")).write_text("def %s():\n    pass\n" % case)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % case)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1736_prints_revise_when_the_named_case_exists_only_in_a_test_file_under_another_runs_worktree(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    case = "test_main_counts_a_repair_text_as_a_repair"
    other_run = tmp_path / ".tdd" / "wt" / "1500" / "tests"
    other_run.mkdir(parents=True)
    (other_run / ("test_" + "ledger" + ".py")).write_text("def %s():\n    pass\n" % case)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % case)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1736_prints_revise_when_the_named_case_exists_only_in_a_test_file_under_venv(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    case = "test_main_counts_a_repair_text_as_a_repair"
    dependency = tmp_path / ".venv" / "lib" / "site-packages" / "dep"
    dependency.mkdir(parents=True)
    (dependency / ("test_" + "ledger" + ".py")).write_text("def %s():\n    pass\n" % case)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % case)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1736_prints_revise_when_the_named_case_exists_only_in_a_test_file_under_node_modules(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    case = "test_main_counts_a_repair_text_as_a_repair"
    dependency = tmp_path / "node_modules" / "dep" / "tests"
    dependency.mkdir(parents=True)
    (dependency / ("test_" + "ledger" + ".py")).write_text("def %s():\n    pass\n" % case)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % case)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1736_prints_revise_when_a_real_case_is_named_only_on_lines_other_than_wrong_test(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    case = "test_main_counts_a_repair_text_as_a_repair"
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    (suite / ("test_" + "ledger" + ".py")).write_text("def %s():\n    pass\n" % case)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "NOTE: %s looks suspicious\n"
        "VERDICT: REJECT because `%s` fails\n"
        "WRONG_TEST: none\n" % (case, case))

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1735_prints_revise_for_a_second_green_of_a_step_whose_log_already_holds_a_reroute_event(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    first, second = "test_main_counts_a_repair_text_as_a_repair", "test_main_totals_an_invoice"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (first, second))
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh routes a contradicted case"
    monkeypatch.setenv("VERI_STEP", step)
    results = []
    for number, case in enumerate((first, second)):
        report = tmp_path / ("green-report-%d.txt" % number)
        report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % case)
        code, stdout, stderr = run_cli(
            wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)
        results.append((code, stdout))
        (tmp_path / ".tdd" / "events.jsonl").write_text(
            '{"event": "reroute", "step": "%s"}\n' % step)

    assert results == [(0, "red %s\n" % first), (3, "revise\n")]


def test_main_1765_prints_repair_and_exits_0_when_the_wrong_test_names_a_case_in_a_file_of_the_steps_red_record(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    written = "test_main_totals_an_invoice"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n" % written)
    step = "wrong-test-route.sh routes a case its own red wrote"
    monkeypatch.setenv("VERI_STEP", step)
    (tmp_path / ".tdd").mkdir()
    digest = hashlib.sha256(os.fsencode(step)).hexdigest()[:16]
    (tmp_path / ".tdd" / ("tests-frozen-%s.record" % digest)).write_text(
        "0" * 64 + "  tests/py/unit/test_ledger.py\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % written)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % written)
