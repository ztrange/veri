"""Process case for stop-reason.sh, the shim over veri/stop_reason.py."""
import subprocess

import pytest

from conftest import SCRIPTS, shim_problems


@pytest.mark.process("stop-reason.sh run for real with no argument and for an issue with no run")
@pytest.mark.tree_audit("every script under skills/tdd/scripts")
def test_stop_reason_is_a_canonical_shim_listed_in_scripts_md_that_exits_2_with_a_usage_line_for_no_argument_and_for_an_issue_with_no_run(
        tmp_path):
    script = SCRIPTS / "stop-reason.sh"
    assert script.is_file()
    assert [p for p in shim_problems(SCRIPTS, {"build-develop-prompt.sh": "x", "build-verify-prompt.sh": "x",
                                               "render-leaf-log.sh": "x", "run-leaf.sh": "x", "run-verdict.sh": "x",
                                               "stop-run.sh": "x"}) if p.startswith("stop-reason.sh")] == []
    assert "$S/stop-reason.sh" in (SCRIPTS.parent / "SCRIPTS.md").read_text()

    bare = subprocess.run([str(script)], capture_output=True, text=True, cwd=str(tmp_path))
    assert bare.returncode == 2 and bare.stdout == ""
    assert "usage" in bare.stderr.lower() and "stop-reason.sh" in bare.stderr

    absent = subprocess.run([str(script), "7"], capture_output=True, text=True, cwd=str(tmp_path))
    assert absent.returncode == 2 and absent.stdout == ""


@pytest.mark.process("stop-reason.sh run for real on an events log of only blank lines")
def test_stop_reason_on_an_events_log_of_only_blank_lines_exits_2_with_a_refusal_on_stderr_and_nothing_on_stdout_2191(
        tmp_path):
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "events.jsonl").write_text("\n\n  \n\n")
    (tdd / "conductor-7.log").write_text('{"type": "system", "subtype": "init"}\n'
                                         '{"type": "result", "result": "finished"}\n')

    blank = subprocess.run([str(SCRIPTS / "stop-reason.sh"), "7"], capture_output=True, text=True,
                           cwd=str(tmp_path))
    assert blank.returncode == 2 and blank.stdout == ""
    assert "stop-reason.sh" in blank.stderr
