"""In-process cases for veri/restart_conductor.py, the module restart-conductor.sh is a shim over."""
import importlib


def test_3223_called_with_no_run_number_exits_2_with_a_usage_line_naming_the_script_and_writes_nothing(tmp_path, run_cli):
    restart_conductor = importlib.import_module("veri.restart_conductor")

    code, out, err = run_cli(restart_conductor, [], cwd=tmp_path)

    assert (code, out, "restart-conductor.sh" in err, list(tmp_path.iterdir())) == (2, "", True, [])
