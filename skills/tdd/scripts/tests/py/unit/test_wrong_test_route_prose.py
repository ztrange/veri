"""In-process cases for wrong_test_route.py reading an unquoted prose SUPERSEDED: case name."""
import importlib


def test_main_2416_resolves_a_superseded_line_with_an_unquoted_prose_name_behind_an_issue_reference_to_the_case_a_test_file_defines(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    title = "typing 7 birth-date digits and clicking Ingresar shows the invalid banner"
    suite = tmp_path / "src" / "__tests__"
    suite.mkdir(parents=True)
    (suite / "login.test.tsx").write_text("it('%s', () => {});\n" % title)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: #590 %s\n" % title)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % title)


def test_main_2416_resolves_a_superseded_line_with_an_unquoted_prose_name_and_no_issue_reference_to_the_case_a_test_file_defines(
        run_cli, tmp_path):
    wrong_test_route = importlib.import_module("veri.wrong_test_route")
    title = "with a 6-digit employee number and a 5-digit date, clicking Ingresar shows the invalid banner"
    suite = tmp_path / "src" / "__tests__"
    suite.mkdir(parents=True)
    (suite / "login.test.tsx").write_text("it('%s', () => {});\n" % title)
    report = tmp_path / "green-report.txt"
    report.write_text("SUITE: make test\nSUPERSEDED: %s\n" % title)

    code, stdout, stderr = run_cli(wrong_test_route, [str(report), "test_other"], cwd=tmp_path)

    assert (code, stdout) == (0, "red %s\n" % title)
