"""prose-owed.sh's entry point: the shim runs veri/prose_owed.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_prose_owed.py."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

PROSE_OWED = SCRIPTS / "prose-owed.sh"
LISTED = "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"


def run(*argv):
    ran = subprocess.run([str(PROSE_OWED), *argv], stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


def usage():
    return importlib.import_module("veri.prose_owed").USAGE + "\n"


@pytest.mark.process("prose-owed.sh run as a script")
def test_the_shim_passes_exit_0_through_when_nothing_is_owed(tmp_path):
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("Some prose with no list.\n")

    assert run(str(tmp_path)) == (0, "", "")


@pytest.mark.process("prose-owed.sh run as a script")
def test_the_shim_passes_exit_1_and_the_modules_stdout_through_when_a_unit_is_owed(tmp_path):
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(LISTED)

    assert run(str(tmp_path)) == (1, "skills/demo/SKILL.md\n", "")


@pytest.mark.process("prose-owed.sh run as a script")
def test_the_shim_passes_exit_2_and_the_modules_stderr_through_for_no_arguments():
    assert run() == (2, "", usage())


@pytest.mark.process("prose-owed.sh run as a script")
def test_help_prints_the_modules_usage_on_stdout_and_exits_0():
    assert run("--help") == (0, usage(), "")
