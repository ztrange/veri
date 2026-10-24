"""A pytest run started with INT, TERM and HUP ignored still delivers the signals its cases send."""
import os
import pathlib
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
SIGNAL_CASE = ("test_supervise.py::test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_"
               "lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently")
DETACH_CASE = ("test_detach_leaf.py::test_main_launches_a_child_that_writes_its_completion_file_after_a_term_to_the_"
               "launchers_process_group_where_a_nohup_child_does_not")


@pytest.mark.process("a child pytest session started with SIGINT, SIGTERM and SIGHUP ignored, running a real signal case")
def test_a_signal_case_passes_in_a_pytest_run_started_with_int_term_and_hup_ignored_2294():
    command = "trap '' INT TERM HUP; exec \"$0\" -m pytest -p no:cacheprovider -q --timeout=10 \"$1\""
    try:
        done = subprocess.run(["sh", "-c", command, sys.executable, str(HERE / SIGNAL_CASE)],
                              cwd=HERE, capture_output=True, text=True, timeout=25)
    except subprocess.TimeoutExpired as exc:
        pytest.fail("the signal case did not finish in 25 s: %r" % (exc.stdout,))

    assert done.returncode == 0, done.stdout[-1500:]


@pytest.mark.process("a child pytest session started with SIGINT, SIGTERM and SIGHUP ignored, running a detach-leaf signal case")
def test_a_detach_leaf_signal_case_passes_in_a_pytest_run_started_with_int_term_and_hup_ignored_2294():
    command = "trap '' INT TERM HUP; exec \"$0\" -m pytest -p no:cacheprovider -q --timeout=10 \"$1\""
    guard = os.path.dirname(os.environ["PUSH_BACKOFF_LOG"])
    path = os.pathsep.join(entry for entry in os.environ["PATH"].split(os.pathsep) if entry != guard)
    try:
        done = subprocess.run(["sh", "-c", command, sys.executable, str(HERE / DETACH_CASE)],
                              cwd=HERE, env=dict(os.environ, PATH=path), capture_output=True, text=True, timeout=25)
    except subprocess.TimeoutExpired as exc:
        pytest.fail("the detach-leaf signal case did not finish in 25 s: %r" % (exc.stdout,))

    assert done.returncode == 0, done.stdout[-1500:]


CASES_AFTER_A_PROCESS_CASE = '''
import signal

import pytest


@pytest.mark.process("stands in for a case that signals a child")
def test_process_case():
    pass


def test_unmarked_case_sees_hup_still_ignored():
    assert signal.getsignal(signal.SIGHUP) == signal.SIG_IGN
'''


@pytest.mark.process("a child pytest session started with SIGHUP ignored, running a process case then an unmarked one")
def test_an_unmarked_case_after_a_process_case_still_sees_hup_ignored_in_a_run_started_with_it_ignored_2294(tmp_path):
    (tmp_path / "test_order.py").write_text(CASES_AFTER_A_PROCESS_CASE)
    command = "trap '' HUP; exec \"$0\" -m pytest -p conftest -p no:cacheprovider -q --timeout=10 test_order.py"
    env = dict(os.environ, PYTHONPATH=str(HERE))
    done = subprocess.run(["sh", "-c", command, sys.executable], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=25)

    assert done.returncode == 0, done.stdout[-1500:]
