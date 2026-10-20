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
def test_main_1621_finds_a_real_pytest_function_from_the_repository_root(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    pytest_case = "test_a_planted_develop_prompt_that_makes_no_commit_and_the_real_prompts_directory_are_clean"
    report = tmp_path / "report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % pytest_case)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=ROOT)

    assert (code, stdout) == (0, "red %s\n" % pytest_case)


@pytest.mark.tree_audit("the repository's own tests directories, searched for the case a WRONG_TEST names")
def test_main_1621_refuses_a_wrong_test_naming_no_case_only_its_own_red_or_a_missing_case_and_a_bad_argument_list(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.chdir(ROOT)
    own_id = "test_a_planted_develop_prompt_that_makes_no_commit_and_the_real_prompts_directory_are_clean"
    usage = ("usage: wrong-test-route.sh <green-report> <red-test-id> "
             "(prints red <case>, missing <behaviour>, repair <case>, supersede <cases> or revise)\n")
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


def test_main_1765_prints_repair_for_a_wrong_test_naming_a_pytest_function_in_the_step_red_record_even_the_own_target(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    own, added = "test_main_returns_zero", "test_main_totals_an_invoice"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (own, added))
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh repairs a case red added"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\ncase: %s\n" % (own, added))
    results = []
    for number, case in enumerate((added, own)):
        report = tmp_path / ("green-report-%d.txt" % number)
        report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % case)
        code, stdout, stderr = run_cli(wrong_test_route, [str(report), own], cwd=tmp_path)
        results.append((code, stdout))

    assert results == [(0, "repair %s\n" % added), (0, "repair %s\n" % own)]


def test_main_1765_prints_repair_for_a_wrong_test_naming_a_bash_name_case_in_the_step_red_record(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests"
    suite.mkdir()
    added = "a repair text counts as a repair"
    (suite / ("ledger" + ".test" + ".sh")).write_text('name="%s"\nrun_case\n' % added)
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh repairs a bash case red added"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: the case `%s` asserts the opposite of the criterion\n" % added)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % added)


def test_main_1765_prints_red_for_a_wrong_test_naming_an_older_case_in_the_same_file_as_a_red_record_case(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    older, added = "test_main_totals_an_invoice", "test_main_returns_zero"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh keeps red for an older case in a red file"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1765_prints_red_for_a_wrong_test_naming_an_older_case_when_the_red_record_names_no_case_only_its_file(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    older, edited = "test_main_totals_an_invoice", "test_main_returns_zero"
    name = suite / ("test_" + "ledger" + ".py")
    name.write_text("def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, edited))
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh never routes a case-less record by file"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("%s  %s\n" % ("0" * 64, name.relative_to(tmp_path)))
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), edited], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1765_prints_repair_for_a_wrong_test_naming_an_existing_case_the_step_red_edited_and_listed_in_its_record(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    older, edited = "test_main_totals_an_invoice", "test_main_returns_zero"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def %s():\n    pass\n\ndef %s():\n    assert True\n" % (older, edited))
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh repairs a case red edited"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % edited)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % edited)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), older], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % edited)


def test_main_1765_prints_revise_for_a_wrong_test_naming_a_case_outside_the_step_red_record_and_in_no_suite(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    added, outside = "test_main_returns_zero", "test_main_totals_an_invoice"
    (suite / ("test_" + "ledger" + ".py")).write_text("def %s():\n    pass\n" % added)
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh revises for a case outside the red record"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % outside)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1765_prints_revise_for_a_wrong_test_naming_a_red_record_case_once_the_step_log_holds_a_reroute_event(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    added = "test_main_returns_zero"
    (suite / ("test_" + "ledger" + ".py")).write_text("def %s():\n    pass\n" % added)
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh bounds a repair by the shared reroute bound"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    (tmp_path / ".tdd" / "events.jsonl").write_text('{"event": "reroute", "step": "%s"}\n' % step)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % added)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1808_prints_missing_behaviour_for_a_verify_green_reject_carrying_a_missing_test_line(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "wrong-test-route.sh routes a missing case")
    report = tmp_path / "verify-green-report.txt"
    report.write_text(
        "VERDICT: REJECT\n"
        "REASON: no test requires the line that stops a closed session being counted twice\n"
        "MISSING_TEST: a closed conductor session is counted once\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "missing a closed conductor session is counted once\n")


def test_main_1808_prints_missing_behaviour_for_a_revise_green_impossible_report_carrying_a_missing_test_line(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "wrong-test-route.sh routes an impossible revise")
    report = tmp_path / "revise-green-report.txt"
    report.write_text(
        "OUTCOME: IMPOSSIBLE — the fix is a test the step lacks\n"
        "MISSING_TEST: a bare force-with-lease is refused\n"
        "AGAINST_UNMODIFIED: N/A\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "missing a bare force-with-lease is refused\n")


def test_main_1808_prints_revise_for_a_missing_test_or_wrong_test_report_once_the_step_log_holds_a_reroute_of_any_route_and_ignores_another_steps(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    older, added = "test_main_totals_an_invoice", "test_main_returns_zero"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh shares the reroute bound with the missing route"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    missing = tmp_path / "missing-report.txt"
    missing.write_text("VERDICT: REJECT\nMISSING_TEST: a closed session is counted once\n")
    wrong = tmp_path / "wrong-report.txt"
    wrong.write_text("SUITE: make test\nWRONG_TEST: %s and %s contradict the criterion\n" % (older, added))
    events = tmp_path / ".tdd" / "events.jsonl"

    def answers():
        return [run_cli(wrong_test_route, [str(r), "test_other"], cwd=tmp_path)[:2]
                for r in (missing, wrong)]

    events.write_text('{"event": "reroute", "step": "another step"}\n')
    other_step = answers()
    events.write_text('{"event": "reroute", "step": "%s", "route": "missing"}\n' % step)
    after_missing = answers()
    events.write_text('{"event": "reroute", "step": "%s", "route": "repair"}\n' % step)
    after_repair = answers()

    assert other_step == [(0, "missing a closed session is counted once\n"), (0, "repair %s\n" % added)]
    assert after_missing == [(3, "revise\n"), (3, "revise\n")]
    assert after_repair == [(3, "revise\n"), (3, "revise\n")]


def test_main_1808_prints_revise_and_exits_3_for_a_product_defect_reject_and_for_a_missing_test_line_with_an_empty_behaviour(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "wrong-test-route.sh keeps product defects on revise")
    defect = tmp_path / "defect-report.txt"
    defect.write_text("VERDICT: REJECT\nREASON: the function returns the wrong exit code for an empty list\n")
    empty = tmp_path / "empty-report.txt"
    empty.write_text("VERDICT: REJECT\nREASON: a line is unpinned\nMISSING_TEST:   \n")

    answers = [run_cli(wrong_test_route, [str(r), "test_other"], cwd=tmp_path)[:2]
               for r in (defect, empty)]

    assert answers == [(3, "revise\n"), (3, "revise\n")]


def test_main_1862_prints_supersede_naming_every_older_case_a_green_report_lists_as_superseded_when_a_step_changes_a_usage_string_two_of_them_compare_against(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    first, second = "test_main_prints_usage_on_no_arguments", "test_main_prints_usage_on_a_bad_flag"
    (suite / "test_solvable.py").write_text(
        "USAGE = 'usage: solvable-issues.sh'\n\n"
        "def %s():\n    assert USAGE\n\n"
        "def %s():\n    assert USAGE\n\n"
        "def %s():\n    pass\n" % (first, second, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s\nSUPERSEDED: %s\n" % (first, second))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "supersede %s %s\n" % (first, second))


def test_main_1862_prints_revise_when_superseded_lines_are_joined_by_a_wrong_test_naming_another_older_case_the_step_does_not_supersede(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    first, second = "test_main_prints_usage_on_no_arguments", "test_main_prints_usage_on_a_bad_flag"
    unrelated = "test_main_totals_an_invoice"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n\ndef %s():\n    pass\n\ndef %s():\n    pass\n"
        % (first, second, unrelated, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, one case not superseded"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\nSUPERSEDED: %s\nSUPERSEDED: %s\n"
        "WRONG_TEST: %s asserts the opposite of the criterion\n" % (first, second, unrelated))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1865_prints_red_over_another_existing_case_a_wrong_test_line_says_contradicts_the_step_criterion(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    own, contradicting = "test_main_prices_a_turn_at_the_rates_of_its_model", "test_main_totals_an_invoice"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (own, contradicting))
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s contradicts the step's criterion, it asserts the opposite\n" % contradicting)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), own], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % contradicting)


def test_main_1865_prints_repair_of_the_step_own_case_when_the_wrong_test_line_faults_it_and_cites_another_existing_case_only_as_the_pattern_to_follow(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    own = "test_conductor_sessions_prices_a_turn_at_the_rates_of_the_model_its_record_names_1859"
    pattern = "test_issue_1815_a_conductor_turn_is_priced_from_the_session_cost_price_table"
    (suite / ("test_" + "metrics" + ".py")).write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (pattern, own))
    (tmp_path / ".tdd").mkdir()
    step = "conductor sessions price a turn at its model's rates"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % own)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s patches veri.session_cost.PRICES, which metrics never reads;"
        " the correct pattern is %s, which patches metrics.session_cost.PRICES\n" % (own, pattern))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), own], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % own)


def test_main_1865_prints_missing_behaviour_of_the_first_well_formed_missing_test_line_skipping_an_empty_one_before_it(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "wrong-test-route.sh skips an empty missing test line")
    report = tmp_path / "verify-green-report.txt"
    report.write_text(
        "VERDICT: REJECT\n"
        "MISSING_TEST:   \n"
        "MISSING_TEST: a closed conductor session is counted once\n"
        "MISSING_TEST: a second behaviour\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "missing a closed conductor session is counted once\n")


def test_main_1865_prints_revise_and_says_on_stderr_no_well_formed_missing_test_line_was_found_when_every_missing_test_line_is_empty(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "wrong-test-route.sh falls back on empty missing test lines")
    report = tmp_path / "verify-green-report.txt"
    report.write_text(
        "VERDICT: REJECT\n"
        "MISSING_TEST:\n"
        "MISSING_TEST:   \n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout, "no well-formed MISSING_TEST: line" in stderr) == (3, "revise\n", True)


def test_main_1865_prints_red_over_the_one_case_a_green_report_lists_as_superseded(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    older = "test_main_prints_usage_on_no_arguments"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, one case superseded"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1865_prints_red_over_the_one_case_the_remaining_superseded_lines_name_when_another_superseded_line_is_empty(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    older = "test_main_prints_usage_on_no_arguments"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, an empty superseded line"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED:\nSUPERSEDED: %s\nSUPERSEDED:   \n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1865_prints_red_over_the_one_case_a_superseded_line_names_in_backticks(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    older = "test_main_prints_usage_on_no_arguments"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, a backticked superseded line"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: `%s`\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1865_prints_red_over_the_one_case_an_indented_superseded_line_names(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    older = "test_main_prints_usage_on_no_arguments"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, an indented superseded line"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\n  SUPERSEDED: %s\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1865_prints_red_over_the_one_case_a_superseded_line_names_before_a_trailing_reason(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    older = "test_main_prints_usage_on_no_arguments"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, a superseded line with a reason"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s asserts the old usage\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1865_prints_repair_keeping_the_superseded_cases_a_repair_report_also_carries(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    own = "test_main_prints_the_usage_with_not_running"
    older = "test_main_prints_usage_on_no_arguments"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, own))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, a repair carrying a superseded case"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % own)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\nWRONG_TEST: %s asserts the wrong usage\nSUPERSEDED: %s\n" % (own, older))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), own], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s %s\n" % (own, older))


def test_main_1865_prints_revise_for_one_or_several_superseded_lines_once_the_step_log_holds_a_reroute_event(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    first, second = "test_main_prints_usage_on_no_arguments", "test_main_prints_usage_on_a_bad_flag"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n\ndef %s():\n    pass\n" % (first, second, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, rerouted once"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    (tmp_path / ".tdd" / "events.jsonl").write_text('{"event": "reroute", "step": "%s"}\n' % step)
    one = tmp_path / "one-report.txt"
    one.write_text("SUITE: make test\nSUPERSEDED: %s\n" % first)
    several = tmp_path / "several-report.txt"
    several.write_text("SUITE: make test\nSUPERSEDED: %s\nSUPERSEDED: %s\n" % (first, second))

    answers = [run_cli(wrong_test_route, [str(r), added], cwd=tmp_path)[:2] for r in (one, several)]

    assert answers == [(3, "revise\n"), (3, "revise\n")]
