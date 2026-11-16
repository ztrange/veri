"""rerun-alone.sh's entry point: the shim runs veri/rerun_alone.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_rerun_alone.py."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

RERUN = str(SCRIPTS / "rerun-alone.sh")


def run(*argv, cwd=None):
    ran = subprocess.run([RERUN, *argv], cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


def usage():
    return importlib.import_module("veri.rerun_alone").USAGE + "\n"


@pytest.mark.process("rerun-alone.sh run as a script, its alone command `true`")
def test_the_shim_passes_exit_0_through_when_every_target_passes_alone(tmp_path):
    (tmp_path / ".git").mkdir()
    red = tmp_path / "red-output.txt"
    red.write_text("FAIL src/a.test.ts\n1 failed\n")

    assert run("true", str(red), cwd=tmp_path) == (0, "", "")
    assert "src/a.test.ts" in (tmp_path / ".tdd" / "events.jsonl").read_text()


@pytest.mark.process("rerun-alone.sh run as a script")
def test_the_shim_passes_exit_2_and_the_modules_stderr_through_for_no_arguments(tmp_path):
    assert run(cwd=tmp_path) == (2, "", usage())


@pytest.mark.process("rerun-alone.sh run as a script")
def test_help_prints_the_modules_usage_on_stdout_and_exits_0(tmp_path):
    assert run("--help", cwd=tmp_path) == (0, usage(), "")
