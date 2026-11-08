"""`--help` as the only argument prints a script's usage on stdout and exits 0."""
import subprocess

from veri import add_ledger_step, run_conductor, stale_rows, stop_reason, stop_run, wait_ci, watch_runs


def test_add_ledger_step_help_prints_usage_on_stdout_and_writes_nothing(run_cli, tmp_path):
    code, out, err = run_cli(add_ledger_step, ["--help"], cwd=tmp_path)

    assert (code, err, list(tmp_path.iterdir())) == (0, "", [])
    assert out.startswith("usage: add-ledger-step.sh")


class Blocked(Exception):
    pass


def test_run_conductor_and_wait_ci_help_print_usage_on_stdout_and_write_nothing(run_cli, tmp_path, monkeypatch):
    def refuse_to_wait(*args, **kwargs):
        raise Blocked

    seen = {}
    for module, name in ((run_conductor, "run-conductor.sh"), (wait_ci, "wait-ci.sh")):
        with monkeypatch.context() as scope:
            scope.setattr(module.subprocess, "run", refuse_to_wait)
            try:
                code, out, err = run_cli(module, ["--help"], cwd=tmp_path)
                seen[name] = (code, err, out.startswith("usage: " + name), list(tmp_path.iterdir()))
            except Blocked:
                seen[name] = "blocked on a process"

    assert seen == {
        "run-conductor.sh": (0, "", True, []),
        "wait-ci.sh": (0, "", True, []),
    }


def test_stale_rows_stop_reason_stop_run_and_watch_runs_help_print_usage_on_stdout_and_write_nothing(
    run_cli, tmp_path, monkeypatch
):
    def refuse_to_wait(*args, **kwargs):
        raise Blocked

    seen = {}
    modules = (
        (stale_rows, "stale-rows.sh"),
        (stop_reason, "stop-reason.sh"),
        (stop_run, "stop-run.sh"),
        (watch_runs, "watch-runs.sh"),
    )
    for module, name in modules:
        with monkeypatch.context() as scope:
            scope.setattr(subprocess, "run", refuse_to_wait)
            try:
                code, out, err = run_cli(module, ["--help"], cwd=tmp_path)
                seen[name] = (code, err, out.startswith("usage: " + name), list(tmp_path.iterdir()))
            except Blocked:
                seen[name] = "blocked on a process"

    assert seen == {name: (0, "", True, []) for _, name in modules}
