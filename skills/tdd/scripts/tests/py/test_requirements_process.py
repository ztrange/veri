"""requirements.sh's entry point: the shim runs veri/requirements.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_requirements.py."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

REQUIREMENTS = SCRIPTS / "requirements.sh"


def run(*argv):
    ran = subprocess.run([str(REQUIREMENTS), *argv], stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


def usage():
    return importlib.import_module("veri.requirements").USAGE + "\n"


@pytest.mark.process("requirements.sh run as a script")
def test_the_shim_passes_exit_0_and_the_modules_stdout_through(tmp_path):
    path = tmp_path / "REQUIREMENTS.md"
    path.write_text("## skills/tdd/SKILL.md\n\n| ID | Requirement | Why |\n|----|-------------|-----|\n| A1 | Says. | Because. |\n")
    assert run("units", str(path)) == (0, "skills/tdd/SKILL.md\n", "")


@pytest.mark.process("requirements.sh run as a script")
def test_the_shim_passes_exit_2_and_the_modules_stderr_through():
    assert run() == (2, "", usage())


@pytest.mark.process("requirements.sh run as a script")
def test_help_prints_the_modules_usage_on_stdout_and_exits_0():
    assert run("--help") == (0, usage(), "")
