"""Cases for supervise.sh that start a real process."""
import fcntl
import os
import subprocess
import sys
import threading

import pytest

from conftest import SCRIPTS


@pytest.mark.process("supervise.sh run for real, supervising a real leaf that echoes its arguments and exits 1")
def test_supervise_sh_forwards_its_arguments_to_the_leaf_and_the_leafs_exit_code_as_its_own(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", 'echo "$1"; exit 1', "sh", "forwarded"],
                         cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout) == (1, "forwarded\n"), ran.stderr


@pytest.mark.process("supervise.sh and git run for real, from a subdirectory of a throwaway repo")
def test_supervise_sh_run_from_a_subdirectory_writes_its_run_state_under_the_repo_root_1895(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    sub = tmp_path / "skills"
    sub.mkdir()

    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", "exit 0"],
                         cwd=sub, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert (sorted(p.name for p in (tmp_path / ".tdd").glob("develop-red.*")), (sub / ".tdd").exists()) == (
        ["develop-red.exit", "develop-red.log", "develop-red.pid", "develop-red.rc"], False)


BROKEN_LOCK_WAIT = """\
import sys, time
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
pytest.main = lambda args: pytest.ExitCode.OK
pytest_leg.acquire_full_lock = lambda: time.sleep(3600)
sys.exit(pytest_leg.main([]))
"""


@pytest.mark.process("supervise.sh runs a real verify leaf whose full run sits in a lock wait that never returns")
@pytest.mark.timeout(60)
def test_2377_a_verify_leaf_whose_mutation_breaks_the_full_suite_lock_wait_is_killed_stuck_within_its_bound(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    script = work / "full_run.py"
    script.write_text(BROKEN_LOCK_WAIT % (str(SCRIPTS), str(SCRIPTS / "veri")))

    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "verify-rebase", sys.executable, str(script)],
                         cwd=work, capture_output=True, text=True, timeout=30,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "VERI_TIMEOUT": "2", "VERI_HEARTBEAT": "600",
                              "HOME": str(tmp_path), "VERI_PYTEST_LEGS": str(tmp_path / "legs"),
                              "VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1",
                              "VERI_PYTEST_XDIST_IMPORTABLE": "1", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr


SHORT_FULL_RUN = """\
import sys
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
pytest.main = lambda args: pytest.ExitCode.OK
sys.exit(pytest_leg.main([]))
"""


@pytest.mark.process("supervise.sh runs a real leaf whose full run queues behind a lock the test holds past VERI_TIMEOUT")
@pytest.mark.timeout(60)
def test_2380_a_leaf_queued_on_the_full_suite_lock_past_the_hard_timeout_is_not_killed_stuck(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    script = work / "full_run.py"
    script.write_text(SHORT_FULL_RUN % (str(SCRIPTS), str(SCRIPTS / "veri")))
    held = open(str(tmp_path / "legs") + "-full.lock", "a+")
    fcntl.flock(held, fcntl.LOCK_EX)
    release = threading.Timer(3.5, lambda: (fcntl.flock(held, fcntl.LOCK_UN), held.close()))
    release.start()

    try:
        ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "verify-rebase", sys.executable, str(script)],
                             cwd=work, capture_output=True, text=True, timeout=30,
                             env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                                  "VERI_POLL": "0.05", "VERI_TIMEOUT": "2", "VERI_HEARTBEAT": "600",
                                  "HOME": str(tmp_path), "VERI_PYTEST_LEGS": str(tmp_path / "legs"),
                                  "VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1",
                                  "VERI_PYTEST_XDIST_IMPORTABLE": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    finally:
        release.join()

    assert ran.returncode == 0, ran.stderr
