"""Cases for veri/detach_command.py that start a real process: a detached child, a signal, a symlinked entry point."""
import importlib
import os
import subprocess
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3]
PIPE_SCRIPT = """exec 2> "$2"
s="$(printf '%070000d' 0)"
printf '%s\\n' x "$s" "$s" "$s" "$s" "$s" | { IFS= read -r _; }
printf '%s\\n' "${PIPESTATUS[0]}" > "$1"
"""


@pytest.fixture
def detach_command():
    return importlib.import_module("veri.detach_command")


@pytest.fixture
def run(tmp_path, run_cli, detach_command):
    (tmp_path / ".tdd").mkdir()

    def call(*argv):
        return run_cli(detach_command, list(argv), env={"VERI_POLL": "0.05"}, cwd=tmp_path)

    return call


@pytest.mark.process("a real detached bash writer whose reader closes early, killed by SIGPIPE")
def test_a_writer_whose_reader_closes_early_dies_of_sigpipe_silently_as_it_does_from_a_shell(tmp_path, run):
    script, status, err = tmp_path / "pipe-writer.sh", tmp_path / "pipe-writer.status", tmp_path / "pipe-writer.err"
    script.write_text(PIPE_SCRIPT)

    run("start", "pipe", "bash", str(script), str(status), str(err))
    run("wait", "pipe", "30")

    assert (status.read_text() if status.is_file() else None, err.read_text() if err.is_file() else None) == ("141\n", "")


@pytest.mark.process("a real detached sh whose session id is read back by python3")
def test_start_still_runs_its_command_in_a_session_of_its_own_records_exit_and_out_and_wait_exits_0_for_a_clean_finish(
        tmp_path, run):
    run("start", "whole", "sh", "-c", 'echo "sid $(python3 -c "import os; print(os.getsid(0))")"; echo out-line')
    code = run("wait", "whole", "30")[0]

    tdd = tmp_path / ".tdd"
    lines = (tdd / "whole.out").read_text().splitlines()
    sid = [line[4:] for line in lines if line.startswith("sid ")]
    assert (code, (tdd / "whole.exit").read_text().strip(), "out-line" in lines,
            sid == [(tdd / "whole.pid").read_text().strip()]) == (0, "0", True, True)


@pytest.mark.process("the symlinked shim run from another working directory with a real detached child")
def test_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_start_and_wait_use_that_directorys_tdd_and_create_none_beside_the_skill(
        tmp_path):
    link = tmp_path / "skill-link"
    link.symlink_to(SKILL_DIR)
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / ".tdd").mkdir(parents=True)
    beside = [SKILL_DIR / ".tdd", SKILL_DIR / "scripts" / ".tdd"]
    before = [p.exists() for p in beside]
    env = dict(os.environ, VERI_POLL="0.05")
    shim = str(link / "scripts" / "detach-command.sh")

    def call(*argv):
        return subprocess.run([shim, *argv], cwd=elsewhere, env=env, stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode

    started = call("start", "linked", "sh", "-c", "echo linked-line")
    waited = call("wait", "linked", "30")
    tdd = elsewhere / ".tdd"
    assert (started, waited, [(tdd / f"linked.{f}").is_file() for f in ("out", "exit", "pid")],
            "linked-line" in (tdd / "linked.out").read_text().splitlines(),
            [p.exists() for p in beside]) == (0, 0, [True] * 3, True, before)


@pytest.mark.process("a real detached bash and python3 reading their inherited signal dispositions")
def test_a_command_started_by_start_sees_sigint_sigquit_and_sigxfsz_ignored_and_sigpipe_at_its_default(tmp_path, run):
    run("start", "sigs", "bash", "-c",
        'trap -p > .tdd/sigs.traps; python3 -c "import signal as s; print(s.getsignal(s.SIGINT), s.getsignal(s.SIGQUIT))" > .tdd/sigs.py')
    run("wait", "sigs", "30")

    tdd = tmp_path / ".tdd"
    traps = sorted((tdd / "sigs.traps").read_text().splitlines())
    assert (traps, (tdd / "sigs.py").read_text().strip()) == (
        ["trap -- '' SIGINT", "trap -- '' SIGQUIT", "trap -- '' SIGXFSZ"], "1 1")
