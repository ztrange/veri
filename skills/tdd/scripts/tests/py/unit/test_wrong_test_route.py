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


def test_main_2596_prints_revise_and_exits_3_for_a_red_green_report_carrying_an_impl_path_and_no_wrong_test_line(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def test_main_returns_zero():\n    pass\n")
    report = tmp_path / "green-report.txt"
    report.write_text("IMPL_PATH: skills/tdd/scripts/veri/ledger.py\nSUITE: RED\n")

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
    pytest_case = "test_parse_reads_each_declared_format_refuses_none_and_a_required_format_without_suite_and_never_reads_an_outcome_line"
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
    own_id = "test_parse_reads_each_declared_format_refuses_none_and_a_required_format_without_suite_and_never_reads_an_outcome_line"
    usage = ("usage: wrong-test-route.sh <green-report> <red-test-id> "
             "(prints red <case>, missing <behaviour>, repair <case> <superseded>…, supersede <cases> or revise)\n")
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
    own_case = "test_parse_reads_each_declared_format_refuses_none_and_a_required_format_without_suite_and_never_reads_an_outcome_line"
    own_id = "skills/tdd/scripts/tests/py/unit/test_report_formats" + ".py::" + own_case
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

    def answers(reports):
        return [run_cli(wrong_test_route, [str(r), "test_other"], cwd=tmp_path)[:2]
                for r in reports]

    events.write_text('{"event": "reroute", "step": "another step"}\n')
    other_step = answers((missing, wrong))
    events.write_text('{"event": "reroute", "step": "%s", "kind": "missing"}\n' % step)
    after_missing = answers((wrong,))
    events.write_text('{"event": "reroute", "step": "%s", "kind": "repair"}\n' % step)
    after_repair = answers((wrong,))

    assert other_step == [(0, "missing a closed session is counted once\n"), (0, "repair %s\n" % added)]
    assert after_missing == [(3, "revise\n")]
    assert after_repair == [(3, "revise\n")]


def test_main_2573_prints_missing_behaviour_for_a_missing_test_report_once_the_step_log_holds_a_reroute_of_another_kind(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh answers a repeat missing route with missing"
    monkeypatch.setenv("VERI_STEP", step)
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "red"}\n' % step)
    report = tmp_path / "missing-report.txt"
    report.write_text("VERDICT: REJECT\nMISSING_TEST: a second guard is pinned by a case\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "missing a second guard is pinned by a case\n")


def test_main_2573_prints_missing_exhausted_and_exits_1_once_the_step_log_holds_as_many_missing_reroutes_as_the_budget(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh bounds repeat missing routes"
    monkeypatch.setenv("VERI_STEP", step)
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", "2")
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "missing"}\n' * 2 % (step, step))
    report = tmp_path / "missing-report.txt"
    report.write_text("VERDICT: REJECT\nMISSING_TEST: a third guard is pinned by a case\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (1, "missing-exhausted a third guard is pinned by a case\n")


def test_main_2568_prints_missing_behaviour_and_exits_0_when_the_only_missing_reroute_precedes_a_resume_event(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh counts missing reroutes after a resume"
    monkeypatch.setenv("VERI_STEP", step)
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", "1")
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "missing"}\n{"event": "resume"}\n' % step)
    report = tmp_path / "missing-report.txt"
    report.write_text("VERDICT: REJECT\nMISSING_TEST: a guard is pinned by a case\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "missing a guard is pinned by a case\n")


def test_main_2568_prints_missing_exhausted_and_exits_1_when_the_only_missing_reroute_has_no_resume_event_after_it(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh keeps a missing reroute spent without a resume"
    monkeypatch.setenv("VERI_STEP", step)
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", "1")
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "missing"}\n' % step)
    report = tmp_path / "missing-report.txt"
    report.write_text("VERDICT: REJECT\nMISSING_TEST: a guard is pinned by a case\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (1, "missing-exhausted a guard is pinned by a case\n")


def test_main_2573_defaults_the_missing_reroute_budget_to_3_when_the_variable_is_unset_or_empty(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh defaults the missing budget"
    monkeypatch.setenv("VERI_STEP", step)
    monkeypatch.delenv("VERI_MISSING_REROUTE_BUDGET", raising=False)
    events = tmp_path / ".tdd" / "events.jsonl"
    report = tmp_path / "missing-report.txt"
    report.write_text("VERDICT: REJECT\nMISSING_TEST: a guard is pinned by a case\n")
    line = '{"event": "reroute", "step": "%s", "kind": "missing"}\n' % step

    def answer():
        return run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)[:2]

    events.write_text(line * 2)
    unset_two = answer()
    events.write_text(line * 3)
    unset_three = answer()
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", "")
    empty_two = (events.write_text(line * 2), answer())[1]
    empty_three = (events.write_text(line * 3), answer())[1]

    assert [unset_two, unset_three, empty_two, empty_three] == [
        (0, "missing a guard is pinned by a case\n"),
        (1, "missing-exhausted a guard is pinned by a case\n"),
        (0, "missing a guard is pinned by a case\n"),
        (1, "missing-exhausted a guard is pinned by a case\n")]


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


@pytest.mark.parametrize("indent", [" ", "  ", "   "])
def test_main_1957_prints_revise_when_a_superseded_line_is_indented_by_one_to_three_spaces_since_it_is_prose(
        indent, run_cli, tmp_path, monkeypatch):
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
    report.write_text("SUITE: make test\n%sSUPERSEDED: %s\n" % (indent, older))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


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


def test_main_2568_prints_red_over_the_one_superseded_case_when_the_step_reroute_event_precedes_a_resume_event(
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
    step = "solvable-issues.sh usage mentions --not-running, rerouted before a resume"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "red"}\n{"event": "resume"}\n' % step)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_2568_prints_revise_and_exits_3_for_the_one_superseded_case_when_the_step_log_holds_a_red_reroute_and_no_resume_event(
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
    step = "solvable-issues.sh usage mentions --not-running, rerouted with no resume"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "red"}\n' % step)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def _superseded_2568(run_cli, tmp_path, monkeypatch, label, events):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    older = "test_main_prints_usage_on_no_arguments"
    (suite / "test_solvable.py").write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (older, added))
    (tmp_path / ".tdd").mkdir()
    step = "solvable-issues.sh usage mentions --not-running, " + label
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        "".join('{"event": "%s", "step": "%s", "kind": "red"}\n' % (e, step) for e in events))
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s\n" % older)
    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)
    return (code, stdout), older


def test_main_2568_prints_revise_and_exits_3_for_the_one_superseded_case_when_a_red_reroute_follows_the_latest_of_two_resume_events(
        run_cli, tmp_path, monkeypatch):
    answer, _ = _superseded_2568(run_cli, tmp_path, monkeypatch, "rerouted after the latest resume",
                                 ["reroute", "resume", "reroute", "resume", "reroute"])

    assert answer == (3, "revise\n")


def test_main_2568_prints_red_over_the_one_superseded_case_when_the_only_red_reroute_sits_between_two_resume_events(
        run_cli, tmp_path, monkeypatch):
    answer, older = _superseded_2568(run_cli, tmp_path, monkeypatch, "rerouted between two resumes",
                                     ["resume", "reroute", "resume"])

    assert answer == (0, "red %s\n" % older)


def _missing_2568(run_cli, tmp_path, monkeypatch, budget, events):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh counts missing reroutes after the latest resume"
    monkeypatch.setenv("VERI_STEP", step)
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", budget)
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        "".join('{"event": "%s", "step": "%s", "kind": "missing"}\n' % (e, step) for e in events))
    report = tmp_path / "missing-report.txt"
    report.write_text("VERDICT: REJECT\nMISSING_TEST: a guard is pinned by a case\n")
    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)
    return code, stdout


def test_main_2568_prints_missing_exhausted_and_exits_1_when_the_missing_reroutes_after_the_latest_of_two_resume_events_reach_the_budget(
        run_cli, tmp_path, monkeypatch):
    answer = _missing_2568(run_cli, tmp_path, monkeypatch, "2",
                           ["reroute", "resume", "reroute", "resume", "reroute", "reroute"])

    assert answer == (1, "missing-exhausted a guard is pinned by a case\n")


def test_main_2568_prints_missing_behaviour_and_exits_0_when_the_only_missing_reroute_sits_between_two_resume_events(
        run_cli, tmp_path, monkeypatch):
    answer = _missing_2568(run_cli, tmp_path, monkeypatch, "1", ["resume", "reroute", "resume"])

    assert answer == (0, "missing a guard is pinned by a case\n")


def test_main_1865_drops_a_superseded_line_naming_a_case_no_test_file_defines(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py"
    suite.mkdir(parents=True)
    added = "test_main_prints_the_usage_with_not_running"
    (suite / "test_solvable.py").write_text("def %s():\n    pass\n" % added)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "solvable-issues.sh usage mentions --not-running, a ghost superseded case")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: test_a_case_nobody_defines\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1932_prints_repair_of_the_step_own_case_when_the_wrong_test_line_faults_it_and_cites_another_as_the_example_and_the_step_has_no_red_record(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    own = "test_conductor_sessions_prices_a_turn_at_the_rates_of_the_model_its_record_names_1859"
    example = "test_issue_1815_a_conductor_turn_is_priced_from_the_session_cost_price_table"
    (suite / ("test_" + "metrics" + ".py")).write_text(
        "def %s():\n    pass\n\ndef %s():\n    pass\n" % (example, own))
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "conductor sessions price a turn at its model's rates, no red record")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s patches veri.session_cost.PRICES, which metrics never reads;"
        " the correct example is %s, which patches metrics.session_cost.PRICES\n" % (own, example))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), own], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % own)


def test_main_1932_prints_repair_of_the_step_own_case_when_the_wrong_test_line_faults_it_and_cites_another_as_the_example_and_the_red_record_names_only_its_file(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    own = "test_conductor_sessions_prices_a_turn_at_the_rates_of_the_model_its_record_names_1859"
    example = "test_issue_1815_a_conductor_turn_is_priced_from_the_session_cost_price_table"
    name = suite / ("test_" + "metrics" + ".py")
    name.write_text("def %s():\n    pass\n\ndef %s():\n    pass\n" % (example, own))
    (tmp_path / ".tdd").mkdir()
    step = "conductor sessions price a turn at its model's rates, file-only record"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("%s  %s\n" % ("0" * 64, name.relative_to(tmp_path)))
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s patches veri.session_cost.PRICES, which metrics never reads;"
        " the correct example is %s, which patches metrics.session_cost.PRICES\n" % (own, example))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), own], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % own)


def test_main_1932_prints_repair_of_the_step_own_case_when_the_wrong_test_line_faults_it_and_cites_another_as_the_example_and_the_red_record_names_it_as_a_path_and_id(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    own = "test_conductor_sessions_prices_a_turn_at_the_rates_of_the_model_its_record_names_1859"
    example = "test_issue_1815_a_conductor_turn_is_priced_from_the_session_cost_price_table"
    name = suite / ("test_" + "metrics" + ".py")
    name.write_text("def %s():\n    pass\n\ndef %s():\n    pass\n" % (example, own))
    (tmp_path / ".tdd").mkdir()
    step = "conductor sessions price a turn at its model's rates, path and id record"
    monkeypatch.setenv("VERI_STEP", step)
    own_id = "%s::%s" % (name.relative_to(tmp_path), own)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % own_id)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: %s patches veri.session_cost.PRICES, which metrics never reads;"
        " the correct example is %s, which patches metrics.session_cost.PRICES\n" % (own, example))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), own_id], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % own)


def test_main_1932_prints_revise_when_a_missing_test_line_is_indented_as_a_quote_inside_prose(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "an indented quote is not a route line")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "The verifier's last report read:\n\n"
        "    MISSING_TEST: the router ignores quoted lines\n\n"
        "which I could not satisfy.\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1932_prints_red_over_the_case_a_bulleted_superseded_line_names(
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
    step = "solvable-issues.sh usage mentions --not-running, a bulleted superseded line"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: - %s\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1932_prints_revise_when_the_missing_test_line_says_none(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "MISSING_TEST: NONE names no behaviour")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nMISSING_TEST: NONE\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1932_prints_red_over_the_one_case_a_backticked_superseded_line_names_before_a_backticked_reason(
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
    step = "solvable-issues.sh usage mentions --not-running, a backticked case and reason"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: `%s` asserts the old `usage`\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


@pytest.mark.parametrize("indent", [" ", "  ", "   "])
def test_main_1957_prints_revise_when_a_wrong_test_line_is_indented_by_one_to_three_spaces_since_it_is_prose(
        indent, run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    contradicted = "test_main_counts_a_repair_text_as_a_repair"
    (suite / "test_ledger.py").write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n" % contradicted)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "a space-indented quote is not a route line")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\n%sWRONG_TEST: %s asserts the opposite\n" % (indent, contradicted))

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1932_prints_revise_when_a_wrong_test_line_is_indented_by_a_tab_inside_prose(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    contradicted = "test_main_counts_a_repair_text_as_a_repair"
    (suite / "test_ledger.py").write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n" % contradicted)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "a tab-indented quote is not a route line")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "The verifier's last report read:\n\n"
        "\tWRONG_TEST: %s asserts the opposite of the criterion\n\n"
        "which I could not satisfy.\n" % contradicted)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1932_prints_red_over_the_case_a_star_bulleted_superseded_line_names(
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
    step = "solvable-issues.sh usage mentions --not-running, a star-bulleted superseded line"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % added)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: * %s\n" % older)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), added], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_1932_prints_revise_with_nothing_on_stderr_when_missing_test_none_precedes_a_well_formed_missing_test_line(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "MISSING_TEST: NONE stops the search")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "MISSING_TEST: NONE\n"
        "MISSING_TEST: the router ignores quoted lines\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout, stderr) == (3, "revise\n", "")


def test_main_1957_routes_a_wrong_test_naming_in_backticks_an_it_title_in_a_foo_test_ts_file_to_a_red_over_that_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "src"
    suite.mkdir()
    sibling = "rejects an empty name"
    (suite / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "src/foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % sibling)


@pytest.mark.parametrize("filename", [
    "foo.test.js", "foo.test.jsx", "foo.test.tsx", "foo.test.mjs", "foo.test.cjs",
    "foo.spec.js", "foo.spec.jsx", "foo.spec.ts", "foo.spec.tsx", "foo.spec.mjs", "foo.spec.cjs"])
def test_main_1957_routes_a_wrong_test_naming_an_it_title_to_a_red_when_the_file_is_a_test_or_spec_file_over_each_js_ts_extension(
        run_cli, tmp_path, filename):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "src"
    suite.mkdir()
    sibling = "rejects an empty name"
    (suite / filename).write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "src/%s::foo accepts a name" % filename], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % sibling)


def test_main_1957_routes_a_wrong_test_naming_an_it_title_to_a_red_when_the_file_is_a_js_or_ts_file_under_a_tests_directory_without_test_or_spec_in_its_name(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "src" / "__tests__"
    suite.mkdir(parents=True)
    sibling = "rejects an empty name"
    (suite / "foo.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "src/__tests__/foo.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % sibling)


def test_main_1957_prints_revise_when_the_named_it_title_is_found_only_in_dts_files_since_a_dts_file_is_never_a_test_file(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "src" / "__tests__"
    suite.mkdir(parents=True)
    sibling = "rejects an empty name"
    (tmp_path / "src" / "foo.test.d.ts").write_text("it('%s', () => {});\n" % sibling)
    (suite / "types.d.ts").write_text("it('%s', () => {});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "src/foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (3, "revise\n", "")


def test_main_1957_prints_revise_when_the_named_it_title_is_found_only_in_non_test_source_files_such_as_config_ts_and_src_testing_config_js(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    testing = tmp_path / "src" / "testing"
    testing.mkdir(parents=True)
    sibling = "rejects an empty name"
    (tmp_path / "config.ts").write_text("it('%s', () => {});\n" % sibling)
    (testing / "config.js").write_text("it('%s', () => {});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "src/foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (3, "revise\n", "")


def test_main_1957_routes_a_wrong_test_naming_the_title_of_a_double_quoted_test_call_in_a_js_ts_test_file_to_a_red_over_that_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        'describe("foo", () => {\n'
        '  test("accepts a name", () => {});\n'
        '  test("%s", () => {});\n'
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % sibling)


@pytest.mark.parametrize("call", ["it.only", "it.skip", "test.only", "test.skip"])
def test_main_1957_routes_a_wrong_test_naming_the_title_of_an_only_or_skip_form_of_it_or_test_to_a_red_over_that_title(
        run_cli, tmp_path, call):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  %s('%s', () => {});\n"
        "});\n" % (call, sibling))
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % sibling)


@pytest.mark.parametrize("head", ["it.each([1, 2])", "test.each([[1, 2]])", "it.each`\n  a | b\n  ${1} | ${2}\n`"])
def test_main_1957_routes_a_wrong_test_naming_the_title_of_the_call_after_an_each_head_to_a_red_over_that_title(
        run_cli, tmp_path, head):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  %s('%s', () => {});\n"
        "});\n" % (head, sibling))
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % sibling)


def test_main_1957_prints_revise_when_the_named_it_title_is_found_only_in_a_call_commented_out_with_slashes(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  // it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (3, "revise\n", "")


def test_main_1957_routes_a_wrong_test_naming_the_title_of_a_live_call_after_a_string_containing_slashes(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  const u = \"http://a\"; it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (0, "red %s\n" % sibling, "")


def test_main_1957_prints_revise_when_the_named_it_title_is_found_only_in_a_call_inside_a_block_comment(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  /*\n"
        "  it('%s', () => {});\n"
        "  */\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (3, "revise\n", "")


def test_main_1957_routes_a_wrong_test_naming_in_double_quotes_the_title_of_a_js_ts_case_to_a_red_over_that_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        'WRONG_TEST: "%s" contradicts the criterion\n' % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (0, "red %s\n" % sibling, "")


def test_main_1957_routes_a_wrong_test_naming_in_curly_quotes_the_title_of_a_js_ts_case_to_a_red_over_that_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: “%s” contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (0, "red %s\n" % sibling, "")


def test_main_1957_routes_a_wrong_test_name_ending_in_either_ellipsis_form_to_a_red_over_the_one_title_it_is_a_prefix_of(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name with a clear message"
    results = []
    for directory, ellipsis in (("unicode", "…"), ("dots", "...")):
        repo = tmp_path / directory
        repo.mkdir()
        (repo / "foo.test.ts").write_text(
            "describe('foo', () => {\n"
            "  it('accepts a name', () => {});\n"
            "  it('%s', () => {});\n"
            "});\n" % sibling)
        report = repo / "green-report.txt"
        report.write_text(
            "SUITE: make test\n"
            "WRONG_TEST: `rejects an empty name%s` contradicts the criterion\n" % ellipsis)
        code, stdout, stderr = run_cli(
            wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=repo)
        results.append((code, stdout, stderr))

    assert results == [(0, "red %s\n" % sibling, "")] * 2


def test_main_1957_prints_revise_when_the_wrong_test_name_is_the_title_tail_of_the_step_own_describe_title_test_id(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `accepts a name` contradicts the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (3, "revise\n", "")


def test_main_1957_routes_a_wrong_test_name_that_is_the_exact_title_of_a_sibling_js_ts_case_to_that_sibling_even_when_it_is_also_one_word_of_the_own_id(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `name` contradicts the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (0, "red name\n", "")


def test_main_1957_prints_repair_listing_the_js_ts_case_a_quoted_superseded_line_names_by_its_title(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "  it('accepts a long name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    step = "foo accepts names, a quoted superseded title"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: accepts a long name\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        'WRONG_TEST: "accepts a long name" contradicts the criterion\n'
        'SUPERSEDED: "rejects an empty name" asserts the old behaviour\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "repair accepts a long name rejects an empty name\n")


def test_main_1957_prints_red_over_the_full_title_when_a_superseded_line_names_a_js_ts_case_by_a_cut_name_ending_in_an_ellipsis(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "foo accepts names, a cut superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nSUPERSEDED: "rejects an empty n…"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_1957_prints_revise_when_a_wrong_test_cut_name_ending_in_an_ellipsis_expands_to_the_step_own_case(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nWRONG_TEST: "accepts a n…" contradicts the criterion\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_prints_revise_when_a_wrong_test_bare_ellipsis_expands_to_the_step_own_case(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nWRONG_TEST: "…" contradicts the criterion\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_prints_revise_when_a_wrong_test_cut_name_is_a_prefix_of_more_than_one_js_ts_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "  it('rejects an empty list', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nWRONG_TEST: "rejects an empty…" contradicts the criterion\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_routes_a_wrong_test_naming_the_title_of_a_live_it_call_on_a_line_below_a_slash_comment_to_a_red_over_that_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    sibling = "rejects an empty name"
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  // the next case is live\n"
        "  it('%s', () => {});\n"
        "});\n" % sibling)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `%s` contradicts the criterion\n" % sibling)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (0, "red %s\n" % sibling, "")


def test_main_1957_prints_revise_when_the_named_title_is_found_only_in_an_emit_call_of_a_js_ts_test_file(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  emit('rejects an empty name');\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `rejects an empty name` contradicts the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_prints_revise_when_the_named_title_is_found_only_in_a_markdown_file_under_a_tests_directory(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "__tests__").mkdir()
    (tmp_path / "__tests__" / "notes.md").write_text(
        "describe('foo', () => {\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `rejects an empty name` contradicts the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_prints_revise_when_the_named_title_is_the_tail_of_an_own_id_written_describe_gt_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `accepts a name` contradicts the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo > accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


@pytest.mark.parametrize("indent", [" ", "  ", "   "])
def test_main_1957_prints_revise_when_a_missing_test_line_is_indented_by_one_to_three_spaces_since_it_is_prose(
        indent, run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "a space-indented missing test is not a route line")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\n%sMISSING_TEST: the router ignores quoted lines\n" % indent)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_prints_red_over_the_whole_title_when_a_cut_name_expands_to_a_double_quoted_title_holding_a_single_quote(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it(\"doesn't crash on null\", () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `doesn…` contradicts the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (0, "red doesn't crash on null\n", "")


def test_main_1957_prints_red_over_the_whole_title_when_a_cut_name_expands_to_a_single_quoted_title_holding_double_quotes(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('says \"hi\" loudly', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `says…` contradicts the criterion\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout, stderr) == (0, 'red says "hi" loudly\n', "")


def test_main_1957_prints_revise_when_a_lone_superseded_cut_name_expands_to_the_step_own_case_and_the_wrong_test_line_names_no_case_that_routes(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "foo accepts names, a superseded cut own case")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        'WRONG_TEST: "a case nobody defines" contradicts the criterion\n'
        'SUPERSEDED: "accepts a n…"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_prints_revise_when_a_superseded_cut_name_on_the_repair_path_expands_to_the_step_own_case(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    step = "foo accepts names, a repair with a cut own superseded"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: accepts a name\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        'WRONG_TEST: "accepts a name" contradicts the criterion\n'
        'SUPERSEDED: "accepts a n…"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1957_prints_repair_without_a_duplicate_when_a_superseded_cut_name_expands_to_the_recorded_repair_case(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    step = "foo accepts names, a repair with a cut recorded superseded"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: rejects an empty name\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        'WRONG_TEST: "rejects an empty name" contradicts the criterion\n'
        'SUPERSEDED: "rejects an empty n…"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "repair rejects an empty name\n")


def test_main_1957_prints_repair_without_the_other_recorded_case_when_a_two_case_record_and_a_superseded_cut_name_expands_to_the_second_recorded_case(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "  it('accepts a long name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    step = "foo accepts names, a repair with a two-case record and a cut recorded superseded"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text(
        "case: accepts a long name\ncase: rejects an empty name\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        'WRONG_TEST: "accepts a long name" contradicts the criterion\n'
        'SUPERSEDED: "rejects an empty n…"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "repair accepts a long name\n")


def test_main_1957_prints_revise_when_a_lone_superseded_cut_name_expands_to_a_recorded_case_and_the_wrong_test_names_no_case_that_routes(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    step = "foo accepts names, a lone cut recorded superseded"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: rejects an empty name\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        'WRONG_TEST: "accepts a name" contradicts the criterion\n'
        'SUPERSEDED: "rejects an empty n…"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_1977_prints_revise_when_the_step_reroute_event_follows_a_line_of_the_log_that_is_not_json(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    case = "test_main_counts_a_repair_text_as_a_repair"
    (suite / ("test_" + "ledger" + ".py")).write_text(
        "def test_main_returns_zero():\n    pass\n\ndef %s():\n    pass\n" % case)
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh reads past a line that is not JSON"
    monkeypatch.setenv("VERI_STEP", step)
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        'this line is not json\n{"event": "reroute", "step": "%s"}\n' % step)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: %s asserts the opposite of the criterion\n" % case)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_2172_prints_fixture_with_the_test_file_path_when_a_wrong_test_names_a_python_helper_with_no_test_prefix(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "backend" / "tests"
    suite.mkdir(parents=True)
    (suite / "test_router.py").write_text(
        "def admin_on_clock(client):\n    client.post('/admin/password')\n\n"
        "def test_session_expires():\n    pass\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `admin_on_clock` sets a password without the injected clock\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_session_expires"], cwd=tmp_path)

    assert (code, stdout) == (0, "fixture backend/tests/test_router.py admin_on_clock\n")


def test_main_2172_prints_revise_when_a_wrong_test_names_a_python_method_without_test_prefix_defined_only_in_a_test_class(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "test_router.py").write_text(
        "class TestRouter:\n"
        "    def admin_on_clock(self, client):\n        client.post('/admin/password')\n\n"
        "    def test_session_expires(self):\n        pass\n")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `admin_on_clock` sets a password without the injected clock\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_session_expires"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_2172_prints_fixture_for_a_ts_function_helper_in_a_test_ts_file_and_revise_when_it_sits_only_in_a_non_test_ts_file(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    helper = "async function adminOnClock(app) {\n  await app.post('/admin/password');\n}\n"
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `adminOnClock` sets a password without the injected clock\n")
    with_test = tmp_path / "with-test"
    (with_test / "backend" / "src").mkdir(parents=True)
    (with_test / "backend" / "src" / "router.test.ts").write_text(
        helper + "it('expires an idle session', () => {});\n")
    without_test = tmp_path / "without-test"
    (without_test / "backend" / "src").mkdir(parents=True)
    (without_test / "backend" / "src" / "router.ts").write_text(helper)

    found = run_cli(wrong_test_route, [str(report), "expires an idle session"], cwd=with_test)
    missed = run_cli(wrong_test_route, [str(report), "expires an idle session"], cwd=without_test)

    assert (found[0], found[1], missed[0], missed[1]) == (
        0, "fixture backend/src/router.test.ts adminOnClock\n", 3, "revise\n")


def test_main_2172_prints_fixture_for_a_const_arrow_helper_in_a_spec_file_and_a_const_function_expression_helper_in_a_tests_directory_file(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `adminOnClock` sets a password without the injected clock\n")
    arrow = tmp_path / "arrow"
    (arrow / "backend" / "src").mkdir(parents=True)
    (arrow / "backend" / "src" / "router.spec.ts").write_text(
        "const adminOnClock = async (app) => {\n  await app.post('/admin/password');\n};\n"
        "it('expires an idle session', () => {});\n")
    expression = tmp_path / "expression"
    (expression / "backend" / "__tests__").mkdir(parents=True)
    (expression / "backend" / "__tests__" / "router.ts").write_text(
        "const adminOnClock = function (app) {\n  return app.post('/admin/password');\n};\n"
        "it('expires an idle session', () => {});\n")

    first = run_cli(wrong_test_route, [str(report), "expires an idle session"], cwd=arrow)
    second = run_cli(wrong_test_route, [str(report), "expires an idle session"], cwd=expression)

    assert (first[0], first[1], second[0], second[1]) == (
        0, "fixture backend/src/router.spec.ts adminOnClock\n",
        0, "fixture backend/__tests__/router.ts adminOnClock\n")


def test_main_2172_prints_red_when_a_wrong_test_name_is_both_a_js_it_title_and_a_helper_and_revise_when_it_is_found_nowhere(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    shared = tmp_path / "shared"
    (shared / "backend" / "src").mkdir(parents=True)
    (shared / "backend" / "src" / "router.test.ts").write_text(
        "function adminOnClock(app) {\n  return app.post('/admin/password');\n}\n"
        "it('adminOnClock', () => {});\n"
        "it('expires an idle session', () => {});\n")
    nowhere = tmp_path / "nowhere"
    nowhere.mkdir()
    (nowhere / "router.test.ts").write_text("it('expires an idle session', () => {});\n")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: `adminOnClock` sets a password without the clock\n")

    case = run_cli(wrong_test_route, [str(report), "expires an idle session"], cwd=shared)
    missed = run_cli(wrong_test_route, [str(report), "expires an idle session"], cwd=nowhere)

    assert (case[0], case[1], missed[0], missed[1]) == (0, "red adminOnClock\n", 3, "revise\n")


def test_main_2172_prints_revise_for_a_wrong_test_naming_a_helper_in_a_test_file_once_the_step_log_holds_a_reroute_event(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "backend" / "src").mkdir(parents=True)
    (tmp_path / "backend" / "src" / "router.test.ts").write_text(
        "function adminOnClock(app) {\n  return app.post('/admin/password');\n}\n"
        "it('expires an idle session', () => {});\n")
    (tmp_path / ".tdd").mkdir()
    step = "the fixture route shares the step's one free reroute"
    monkeypatch.setenv("VERI_STEP", step)
    (tmp_path / ".tdd" / "events.jsonl").write_text('{"event": "reroute", "step": "%s"}\n' % step)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nWRONG_TEST: `adminOnClock` sets a password without the clock\n")

    code, stdout, _ = run_cli(wrong_test_route, [str(report), "expires an idle session"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_2227_prints_red_over_the_title_when_a_superseded_line_names_a_js_ts_case_by_a_backticked_path_then_a_double_quoted_title(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "foo accepts names, a path-prefixed superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nSUPERSEDED: `foo.test.ts` "rejects an empty name"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2227_prints_red_over_the_title_when_a_superseded_line_names_a_js_ts_case_by_a_backticked_path_then_a_curly_quoted_title(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "foo accepts names, a curly-quoted superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nSUPERSEDED: `foo.test.ts` “rejects an empty name”\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2227_prints_red_over_the_title_when_a_superseded_line_names_a_js_ts_case_by_a_path_then_a_separator_then_an_unquoted_title(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "foo accepts names, a separator-form superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: foo.test.ts › rejects an empty name\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2227_prints_red_over_the_title_when_a_superseded_line_names_a_js_ts_case_by_a_path_then_a_separator_then_a_double_quoted_title(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "foo accepts names, a quoted separator-form superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nSUPERSEDED: foo.test.ts › "rejects an empty name"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2227_prints_revise_when_a_superseded_line_holds_only_a_backticked_test_file_path_and_names_no_title(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "foo accepts names, a path-only superseded line")
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: `foo.test.ts`\n")

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (3, "revise\n")


def test_main_2227_prints_red_over_the_full_title_when_a_superseded_title_has_an_ellipsis_in_the_middle(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    full = "shows the earlier ocupación, deporte answer and sexo of the titular when a removed titular is added again"
    (tmp_path / "CotizadorPage.test.tsx").write_text(
        "describe('CotizadorPage', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % full)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "cotizador accepts names, a middle-ellipsis superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text(
        'SUITE: make test\nSUPERSEDED: `CotizadorPage.test.tsx` '
        '"shows the earlier ocupación, deporte answer and sexo … when a removed titular is added again"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "CotizadorPage.test.tsx::CotizadorPage accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red " + full + "\n")


def test_main_2227_prints_red_over_the_full_title_when_a_superseded_title_has_three_dots_in_the_middle(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    full = "shows the earlier ocupación, deporte answer and sexo of the titular when a removed titular is added again"
    (tmp_path / "CotizadorPage.test.tsx").write_text(
        "describe('CotizadorPage', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % full)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "cotizador accepts names, a three-dot superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text(
        'SUITE: make test\nSUPERSEDED: `CotizadorPage.test.tsx` '
        '"shows the earlier ocupación, deporte answer and sexo ... when a removed titular is added again"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "CotizadorPage.test.tsx::CotizadorPage accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red " + full + "\n")


def test_main_2227_prints_red_over_the_full_title_when_a_superseded_title_ends_in_an_ellipsis_prefix(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    full = "shows the earlier ocupación, deporte answer and sexo of the titular when a removed titular is added again"
    (tmp_path / "CotizadorPage.test.tsx").write_text(
        "describe('CotizadorPage', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('%s', () => {});\n"
        "});\n" % full)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setenv("VERI_STEP", "cotizador accepts names, a trailing-ellipsis superseded title")
    report = tmp_path / "green-report.txt"
    report.write_text(
        'SUITE: make test\nSUPERSEDED: `CotizadorPage.test.tsx` '
        '"shows the earlier ocupación, deporte answer and sexo …"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "CotizadorPage.test.tsx::CotizadorPage accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red " + full + "\n")


def test_main_2227_prints_red_over_the_title_when_a_wrong_test_line_names_a_js_ts_case_by_a_backticked_path_then_a_double_quoted_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nWRONG_TEST: `foo.test.ts` "rejects an empty name"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2227_prints_red_over_the_title_when_a_wrong_test_line_names_a_js_ts_case_by_a_backticked_path_then_a_curly_quoted_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nWRONG_TEST: `foo.test.ts` “rejects an empty name”\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2227_prints_red_over_the_title_when_a_wrong_test_line_names_a_js_ts_case_by_a_path_then_a_separator_then_an_unquoted_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nWRONG_TEST: foo.test.ts › rejects an empty name\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2227_prints_red_over_the_title_when_a_wrong_test_line_names_a_js_ts_case_by_a_path_then_a_separator_then_a_double_quoted_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / "foo.test.ts").write_text(
        "describe('foo', () => {\n"
        "  it('accepts a name', () => {});\n"
        "  it('rejects an empty name', () => {});\n"
        "});\n")
    report = tmp_path / "green-report.txt"
    report.write_text('SUITE: make test\nWRONG_TEST: foo.test.ts › "rejects an empty name"\n')

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "foo.test.ts::foo accepts a name"], cwd=tmp_path)

    assert (code, stdout) == (0, "red rejects an empty name\n")


def test_main_2254_prints_red_over_the_full_name_when_a_lone_superseded_line_names_an_earlier_pytest_case_by_a_bare_name_cut_short_with_an_ellipsis(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    older = "test_take_without_pid_records_the_parent_process"
    (suite / "test_take.py").write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n" % older)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s…\n" % older[:-8])

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_main_2254_prints_red_over_the_older_case_a_revise_green_report_names_only_on_a_superseded_line_as_a_node_id(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    suite = tmp_path / "tests" / "py" / "unit"
    suite.mkdir(parents=True)
    older = "test_take_without_pid_records_the_parent_process"
    (suite / "test_take.py").write_text(
        "def test_main_returns_zero():\n    pass\n\n"
        "def %s():\n    pass\n" % older)
    report = tmp_path / "revise-green-report.txt"
    report.write_text(
        "OUTCOME: the revised green still fails the suite\n"
        "AGAINST_UNMODIFIED: N/A\n"
        "SUPERSEDED: tests/py/unit/test_take.py::%s asserts the old behaviour\n" % older)

    code, stdout, stderr = run_cli(
        wrong_test_route, [str(report), "test_main_returns_zero"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % older)


def test_superseded_2453_writes_no_unresolved_line_for_a_case_the_step_itself_records(
        monkeypatch, capsys, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.setattr(wrong_test_route, "_recorded_cases", lambda step: {"the_steps_own_case"})
    report = tmp_path / "report.txt"
    report.write_text('SUPERSEDED: "the_steps_own_case"\n')

    cases = wrong_test_route._superseded(str(report), "step")

    assert (cases, capsys.readouterr().err) == ([], "")


def test_superseded_2453_says_the_line_carried_no_case_name_when_the_body_yields_none(
        monkeypatch, capsys, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.setattr(wrong_test_route, "_recorded_cases", lambda step: set())
    monkeypatch.setattr(wrong_test_route, "_exists", lambda case: None)
    report = tmp_path / "report.txt"
    report.write_text("SUPERSEDED:   \n")

    cases = wrong_test_route._superseded(str(report), "step")
    err = capsys.readouterr().err

    assert (cases, "no case name" in err, "no defined test case resolves" in err) == ([], True, False)


def test_superseded_2453_still_writes_the_unresolved_line_for_a_case_name_that_resolves_to_nothing(
        monkeypatch, capsys, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    monkeypatch.setattr(wrong_test_route, "_recorded_cases", lambda step: set())
    monkeypatch.setattr(wrong_test_route, "_exists", lambda case: None)
    report = tmp_path / "report.txt"
    report.write_text('SUPERSEDED: "a_case_nobody_defines"\n')

    cases = wrong_test_route._superseded(str(report), "step")

    assert (cases, capsys.readouterr().err) == (
        [], 'no defined test case resolves: SUPERSEDED: "a_case_nobody_defines"\n')


def test_main_2573_counts_only_missing_kind_reroutes_against_the_missing_budget_so_a_red_reroute_leaves_a_budget_of_1_unspent(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh counts reroutes by kind"
    monkeypatch.setenv("VERI_STEP", step)
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", "1")
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "red"}\n' % step)
    report = tmp_path / "missing-report.txt"
    report.write_text("VERDICT: REJECT\nMISSING_TEST: a guard is pinned by a case\n")

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "missing a guard is pinned by a case\n")


def test_main_2596_prints_repair_for_a_wrong_test_naming_the_own_vitest_case_with_a_describe_prefix_when_the_record_names_it_by_title(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "src" / "services" / "mock"
    suite.mkdir(parents=True)
    title = "marks a within-limit applicant eligible"
    (suite / "underwriting.test.ts").write_text(
        'describe("mock underwriting", () => {\n  it("%s", () => {});\n});\n' % title)
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh repairs a prefixed vitest case"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % title)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `mock underwriting > %s` uses ISO dates the code cannot parse\n" % title)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), title], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % title)


def test_main_2596_prints_repair_with_the_bare_recorded_case_name_for_a_wrong_test_naming_the_own_vitest_case_under_nested_describes(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "src" / "services" / "mock"
    suite.mkdir(parents=True)
    title = "marks a within-limit applicant eligible"
    (suite / "underwriting.test.ts").write_text(
        'describe("mock", () => {\n  describe("underwriting", () => {\n'
        '    it("%s", () => {});\n  });\n});\n' % title)
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh repairs a nested vitest case"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % title)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `mock > underwriting > %s` uses ISO dates the code cannot parse\n" % title)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), title], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % title)


def test_main_2596_prints_repair_with_the_bare_recorded_case_name_for_a_wrong_test_naming_the_own_python_method_with_its_class_prefix_and_file_path(
        run_cli, tmp_path, monkeypatch):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    suite = tmp_path / "tests"
    suite.mkdir()
    case = "test_marks_a_within_limit_applicant_eligible"
    (suite / "test_thing.py").write_text(
        "class TestThing:\n    def %s(self):\n        assert True\n" % case)
    (tmp_path / ".tdd").mkdir()
    step = "wrong-test-route.sh repairs a class-prefixed python method"
    monkeypatch.setenv("VERI_STEP", step)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    (tmp_path / record_path.rstrip("\n")).write_text("case: %s\n" % case)
    report = tmp_path / "green-report.txt"
    report.write_text(
        "SUITE: make test\n"
        "WRONG_TEST: `tests/test_thing.py::TestThing::%s` uses ISO dates the code cannot parse\n" % case)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), case], cwd=tmp_path)

    assert (code, stdout) == (0, "repair %s\n" % case)


def test_main_2565_resolves_an_unquoted_superseded_line_naming_a_case_whose_own_title_begins_with_an_issue_reference_to_the_full_title(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    title = "#553 a peso of 70,5 is stored as 70.5"
    suite = tmp_path / "src" / "features"
    suite.mkdir(parents=True)
    (suite / "ValidationModal.app.test.tsx").write_text("it('%s', () => {});\n" % title)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s\n" % title)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout, "no defined test case resolves:" in stderr) == (0, "red %s\n" % title, False)
