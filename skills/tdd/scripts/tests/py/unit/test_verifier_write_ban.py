"""In-process cases for veri/verifier_write_ban.py, the PreToolUse hook command a verifier leaf's settings carry."""
import importlib
import json

import pytest


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit", "NotebookEdit"])
def test_main_blocks_a_file_writing_tool_call_with_exit_2_and_one_line_saying_the_verifier_may_not_modify_files(
        tool, run_cli):
    ban = importlib.import_module("veri.verifier_write_ban")
    call = json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"file_path": "src.py"}})

    code, out, err = run_cli(ban, [], stdin=call)

    assert (code, out, err) == (2, "", "verifier-write-ban: the verifier may not modify files (%s)\n" % tool)


@pytest.mark.parametrize("tool", ["Bash", "Read"])
def test_main_lets_any_other_tool_call_through_with_exit_0_and_nothing_printed(tool, run_cli):
    ban = importlib.import_module("veri.verifier_write_ban")
    call = json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": "ls"}})

    assert run_cli(ban, [], stdin=call) == (0, "", "")


@pytest.mark.parametrize("stdin", ["", "not json", "[]", '{"tool_input": {}}'])
def test_main_blocks_a_call_it_cannot_read_with_exit_2_so_the_ban_fails_closed(stdin, run_cli):
    ban = importlib.import_module("veri.verifier_write_ban")

    code, out, err = run_cli(ban, [], stdin=stdin)

    assert (code, out, err.startswith("verifier-write-ban.sh: ")) == (2, "", True)
