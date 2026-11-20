"""In-process cases for veri/skill_edit_half.py, the module skill-edit-half.sh is a shim over (PRD 038.4, #4450)."""
import importlib


def test_run_with_no_argument_prints_its_usage_line_on_stderr_and_exits_2(run_cli):
    skill_edit_half = importlib.import_module("veri.skill_edit_half")

    code, out, err = run_cli(skill_edit_half, [])

    assert (code, out, err.strip()) == (
        2, "", 'usage: skill-edit-half.sh <n> [--change "<change>"]'), (code, out, err)
