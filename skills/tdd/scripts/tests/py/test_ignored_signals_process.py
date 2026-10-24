"""A pytest run started with INT, TERM and HUP ignored still delivers the signals its cases send."""
import pathlib
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
SIGNAL_CASE = ("test_supervise.py::test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_"
               "lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently")


@pytest.mark.process("a child pytest session started with SIGINT, SIGTERM and SIGHUP ignored, running a real signal case")
def test_a_signal_case_passes_in_a_pytest_run_started_with_int_term_and_hup_ignored_2294():
    command = "trap '' INT TERM HUP; exec \"$0\" -m pytest -p no:cacheprovider -q --timeout=10 \"$1\""
    try:
        done = subprocess.run(["sh", "-c", command, sys.executable, str(HERE / SIGNAL_CASE)],
                              cwd=HERE, capture_output=True, text=True, timeout=25)
    except subprocess.TimeoutExpired as exc:
        pytest.fail("the signal case did not finish in 25 s: %r" % (exc.stdout,))

    assert done.returncode == 0, done.stdout[-1500:]
