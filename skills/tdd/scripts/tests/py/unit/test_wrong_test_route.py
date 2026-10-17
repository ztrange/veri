"""In-process cases for veri/wrong_test_route.py, the module wrong-test-route.sh is a shim over."""
import importlib


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
