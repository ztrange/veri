"""Cases for veri/detach_command.py that start a real process: a detached child, a signal, a symlinked entry point."""
import importlib
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3]
DEAF = ("import os, signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('ready', os.getpid(), flush=True); "
        "time.sleep(60)")
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
            sid == [(tdd / "whole.pid").read_text().splitlines()[0]]) == (0, "0", True, True)


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


@pytest.mark.process("a real detached red command and a real alone command that fails for the named file")
def test_wait_alone_on_a_red_command_whose_named_file_is_still_red_alone_exits_1_with_the_code_and_writes_no_suite_flake_event_2912(
        tmp_path, run):
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text('#!/bin/sh\ncase "$1" in *b.test.mjs) exit 1;; esac\nexit 0\n')
    alone.chmod(0o755)

    run("start", "red", "sh", "-c", "echo 'FAIL scripts/b.test.mjs'; exit 3")
    result = run("wait", "red", "--alone", f'{alone} "$1"')

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (result, "suite-flake" in (events.read_text() if events.is_file() else "")) == ((1, "3\n", ""), False)


@pytest.mark.process("a real detached red command and a real alone command that passes for every named file")
def test_wait_alone_on_a_red_command_whose_named_files_each_pass_alone_exits_0_silently_and_writes_one_suite_flake_event_naming_each_2912(
        tmp_path, run):
    alone = tmp_path / "alone-cmd.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    run("start", "red", "sh", "-c", "echo 'FAIL scripts/a.test.mjs'; echo 'FAIL scripts/b.test.mjs'; exit 3")
    result = run("wait", "red", "--alone", f'{alone} "$1"')

    events = tmp_path / ".tdd" / "events.jsonl"
    text = events.read_text() if events.is_file() else ""
    assert (result, text.count("suite-flake"), "scripts/a.test.mjs" in text, "scripts/b.test.mjs" in text) == (
        (0, "", ""), 1, True, True)


@pytest.mark.process("a real detached python3 that ignores TERM, under the sh wrapper, stopped by wait --total")
def test_wait_total_kills_a_command_that_ignores_term_once_the_grace_passes_and_exits_2_naming_the_bound_4264(
        tmp_path, run_cli, detach_command):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    env = {"VERI_POLL": "0.05", "VERI_STOP_KILL_GRACE": "0.2"}
    run_cli(detach_command, ["start", "deaf", sys.executable, "-c", DEAF], env=env, cwd=tmp_path)
    group = int((tdd / "deaf.pid").read_text().splitlines()[0])
    try:
        deadline = time.monotonic() + 10
        while not (ready := re.findall(r"^ready (\d+)$", (tdd / "deaf.out").read_text(), re.M)) \
                and time.monotonic() < deadline:
            time.sleep(0.05)
        deaf = int(ready[0])

        result = run_cli(detach_command, ["wait", "deaf", "--total", "0"], env=env, cwd=tmp_path)

        gone, deadline = False, time.monotonic() + 5
        while not gone and time.monotonic() < deadline:
            try:
                os.kill(deaf, 0)
                time.sleep(0.05)
            except ProcessLookupError:
                gone = True
    finally:
        try:
            os.killpg(group, signal.SIGKILL)
        except OSError:
            pass
        try:
            os.waitpid(group, 0)
        except ChildProcessError:
            pass

    assert (result, gone) == (
        (2, "", "detach-command.sh: still running past --total 0 seconds; stopped its process group\n"), True)
