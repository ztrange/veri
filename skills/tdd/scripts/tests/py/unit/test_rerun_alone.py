"""Cases for veri/rerun_alone.py, the logic behind rerun-alone.sh."""
import importlib


def test_main_with_no_argument_prints_a_usage_line_naming_rerun_alone_sh_on_stderr_and_exits_2_2905(run_cli):
    rerun_alone = importlib.import_module("veri.rerun_alone")

    code, out, err = run_cli(rerun_alone, [])

    assert (code, out) == (2, "")
    assert "usage: rerun-alone.sh" in err
