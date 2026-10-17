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
    bash_case = ("through a symlink to the skill directory, from another working directory, "
                 "answers as in place")
    results = []
    for line in ("WRONG_TEST: %s asserts the opposite of the criterion" % pytest_case,
                 "WRONG_TEST: the case `%s` asserts the opposite of the criterion" % bash_case):
        report = tmp_path / ("report-%d.txt" % len(results))
        report.write_text("SUITE: make test\n" + line + "\n")
        code, stdout, stderr = run_cli(
            wrong_test_route, [str(report), "test_main_returns_zero"], cwd=ROOT)
        results.append((code, stdout))

    assert results == [(0, "red %s\n" % pytest_case), (0, "red %s\n" % bash_case)]
