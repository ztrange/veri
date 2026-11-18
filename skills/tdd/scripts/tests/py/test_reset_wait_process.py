"""Entry-point contract cases for reset-wait.sh: the real shim, run as a script."""
import subprocess
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV

SHIM = Path(__file__).resolve().parents[2] / "reset-wait.sh"


def run_shim(tmp_path, *args, env=None):
    (tmp_path / ".git").mkdir(exist_ok=True)
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    return subprocess.run([str(SHIM), *args], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, timeout=20, env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path),
                                                      "VERI_VENV": INTERPRETER_VENV, "VERI_POLL": "0.05", **(env or {})})


@pytest.mark.process("reset-wait.sh run as a script")
def test_the_shim_answers_recovered_with_the_marker_and_a_later_recovered_at_instead_of_failing_to_import(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    (tmp_path / ".tdd" / "role-dev.state").write_text("recovered-at=2026-11-12T10:02:30\n")

    done = run_shim(tmp_path, "recovered", "dev", "5")

    assert (done.returncode, done.stdout, done.stderr) == (0, "recovered dev 2026-11-12T10:02:30\n", "")


@pytest.mark.process("reset-wait.sh run as a script")
def test_the_shim_answers_marker_from_the_main_trees_tdd_dir(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "reset-request-dev-a").write_text("2026-11-12T11:00:00\n")

    marker = run_shim(tmp_path, "marker", "dev", "--lane", "a")

    assert (marker.returncode, marker.stdout) == (0, "reset-request dev 2026-11-12T11:00:00\n")


BAD_ARGUMENTS = [
    ("marker", "foo"),
    ("recovered", "foo"),
    ("recovered", "foo", "5"),
    ("recovered", "dev", "x", "5", "5"),
    ("marker", "dev", "x", "5"),
    ("recovered", "dev", "--lane"),
    ("bogus", "dev"),
]


@pytest.mark.process("reset-wait.sh run as a script with no state files at all")
@pytest.mark.parametrize("args", BAD_ARGUMENTS, ids=lambda a: " ".join(a))
def test_bad_arguments_exit_2_with_the_usage_on_stderr_and_no_traceback_whatever_files_exist(tmp_path, args):
    done = run_shim(tmp_path, *args)

    assert (done.returncode, done.stdout) == (2, "")
    assert done.stderr.startswith("usage: reset-wait.sh")
    assert "Traceback" not in done.stderr
