"""In-process cases for veri/restart_conductor.py, the module restart-conductor.sh is a shim over."""
import importlib


def test_3223_called_with_no_run_number_exits_2_with_a_usage_line_naming_the_script_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    code, out, err = run_cli(restart_conductor, [], cwd=tmp_path)

    assert (code, out, "restart-conductor.sh" in err, list(tmp_path.iterdir())) == (2, "", True, [])


def test_3223_called_with_a_run_number_that_is_not_a_positive_integer_exits_2_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    results = [run_cli(restart_conductor, [n], cwd=tmp_path) for n in ("abc", "0", "-3", "1.5")]

    assert ([code for code, _, _ in results], [out for _, out, _ in results], list(tmp_path.iterdir())) == ([2] * 4, [""] * 4, [])


def test_3223_called_with_a_non_ascii_digit_run_number_exits_2_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    code, out, err = run_cli(restart_conductor, ["٣"], cwd=tmp_path)

    assert (code, out, list(tmp_path.iterdir())) == (2, "", [])


def test_3223_a_growth_knob_that_is_not_a_whole_number_of_at_least_1_exits_2_naming_the_variable_and_value_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")
    values = ("abc", "0", "-5", "1.5", "")

    results = [run_cli(restart_conductor, ["7"], env={"VERI_RESET_GROWTH_CONDUCTOR": v}, cwd=tmp_path) for v in values]

    assert (
        [code for code, _, _ in results],
        [out for _, out, _ in results],
        [("VERI_RESET_GROWTH_CONDUCTOR" in err, repr(v) in err) for (_, _, err), v in zip(results, values)],
        list(tmp_path.iterdir()),
    ) == ([2] * 5, [""] * 5, [(True, True)] * 5, [])
