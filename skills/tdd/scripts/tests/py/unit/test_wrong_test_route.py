"""In-process cases for veri/wrong_test_route.py, the module wrong-test-route.sh is a shim over."""
import importlib

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
    bash_case = "run through a symlink to the skill directory from another directory, answers as in place"
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
