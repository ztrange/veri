"""Process cases for the write-ban hook command verify.py puts in a verifier leaf's --settings: run as the CLI runs it,
through `sh -c`, it blocks (exit 2) whatever fails, and lets an allowed call through (exit 0)."""
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
BAN = SCRIPTS / "veri" / "verifier_write_ban.py"


def run_hook(command, tool):
    call = json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {}})
    return subprocess.run(["sh", "-c", command], input=call.encode(), capture_output=True, timeout=20).returncode


@pytest.mark.process("the write-ban hook command run through sh -c, as the CLI runs a hook")
def test_the_hook_command_exits_2_when_its_interpreter_is_missing_or_its_module_fails_to_import_and_0_for_an_allowed_call(
        tmp_path):
    verify = importlib.import_module("veri.verify")
    alone = tmp_path / "verifier_write_ban.py"
    shutil.copyfile(BAN, alone)

    assert (run_hook(verify.write_ban_command(str(tmp_path / "no-python3"), str(BAN)), "Bash"),
            run_hook(verify.write_ban_command(sys.executable, str(alone)), "Bash"),
            run_hook(verify.write_ban_command(sys.executable, str(BAN)), "Write"),
            run_hook(verify.write_ban_command(sys.executable, str(BAN)), "Bash")) == (2, 2, 2, 0)
