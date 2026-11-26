"""`--help` as the only argument prints a script's usage on stdout and exits 0."""
import importlib

import pytest
from veri import (
    add_ledger_step,
    run_conductor,
    stale_rows,
    stop_reason,
    stop_run,
    wait_ci,
    watch_runs,
)


def test_add_ledger_step_help_prints_usage_on_stdout_and_writes_nothing(run_cli, tmp_path):
    code, out, err = run_cli(add_ledger_step, ["--help"], cwd=tmp_path)

    assert (code, err, list(tmp_path.iterdir())) == (0, "", [])
    assert out.startswith("usage: add-ledger-step.sh")


def test_run_conductor_and_wait_ci_help_print_usage_on_stdout_and_write_nothing(run_cli, tmp_path, fake_processes):
    fake = fake_processes.answers({})
    seen = {}
    for module, name in ((run_conductor, "run-conductor.sh"), (wait_ci, "wait-ci.sh")):
        code, out, err = run_cli(module, ["--help"], cwd=tmp_path)
        seen[name] = (code, err, out.startswith("usage: " + name), list(tmp_path.iterdir()))

    assert seen == {
        "run-conductor.sh": (0, "", True, []),
        "wait-ci.sh": (0, "", True, []),
    }
    assert fake.calls == []


def test_stale_rows_stop_reason_stop_run_and_watch_runs_help_print_usage_on_stdout_and_write_nothing(
    run_cli, tmp_path, fake_processes
):
    fake = fake_processes.answers({})
    seen = {}
    modules = (
        (stale_rows, "stale-rows.sh"),
        (stop_reason, "stop-reason.sh"),
        (stop_run, "stop-run.sh"),
        (watch_runs, "watch-runs.sh"),
    )
    for module, name in modules:
        code, out, err = run_cli(module, ["--help"], cwd=tmp_path)
        seen[name] = (code, err, out.startswith("usage: " + name), list(tmp_path.iterdir()))

    assert seen == {name: (0, "", True, []) for _, name in modules}
    assert fake.calls == []


LISTED_SCRIPTS = (
    "add-ledger-step capture-spec classify-bail detach-command detach-leaf grade-prose ledger-growth "
    "merge-lock metrics park-issue parked-issues prose-owed queued-merge ready-check report-cache "
    "run-conductor solvable-issues stale-rows status stop-reason stop-run update-veri wait-ci watch-runs"
).split()


@pytest.mark.parametrize("name", LISTED_SCRIPTS)
def test_listed_script_help_prints_usage_on_stdout_and_starts_nothing_and_writes_nothing(
    name, run_cli, tmp_path, fake_processes
):
    fake = fake_processes.answers({})
    module = importlib.import_module("veri." + name.replace("-", "_"))
    code, out, err = run_cli(module, ["--help"], cwd=tmp_path)

    assert (code, err, out.startswith("usage: " + name + ".sh"), list(tmp_path.iterdir())) == (0, "", True, [])
    assert fake.calls == []


def test_restart_conductor_help_prints_usage_on_stdout_and_starts_nothing_and_writes_nothing(
    run_cli, tmp_path, fake_processes
):
    from veri import restart_conductor

    fake = fake_processes.answers({})
    code, out, err = run_cli(restart_conductor, ["--help"], cwd=tmp_path)

    assert (code, err, out.startswith("usage: restart-conductor.sh"), list(tmp_path.iterdir())) == (0, "", True, [])
    assert fake.calls == []
