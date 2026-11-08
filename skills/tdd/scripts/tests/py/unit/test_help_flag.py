"""`--help` as the only argument prints a script's usage on stdout and exits 0."""
from veri import add_ledger_step


def test_add_ledger_step_help_prints_usage_on_stdout_and_writes_nothing(run_cli, tmp_path):
    code, out, err = run_cli(add_ledger_step, ["--help"], cwd=tmp_path)

    assert (code, err, list(tmp_path.iterdir())) == (0, "", [])
    assert out.startswith("usage: add-ledger-step.sh")
