"""Cases for suite-reported.sh that start the real entry point, and supervise.sh around a stub leaf."""
import json
import os
import subprocess

import pytest

from conftest import SCRIPTS

CHECK = SCRIPTS / "suite-reported.sh"
SUPERVISE = SCRIPTS / "supervise.sh"
RUN_LEAF = SCRIPTS / "run-leaf.sh"


def check(work, leaf):
    ran = subprocess.run([str(CHECK), leaf], cwd=work, capture_output=True, text=True, env={**os.environ, "VERI_ISSUE": "1"})
    return ran.returncode


def leaf_stub(tmp_path):
    stubdir = tmp_path / "stub"
    stubdir.mkdir()
    claude = stubdir / "claude"
    claude.write_text('#!/bin/sh\nprintf \'{"type":"result","subtype":"success","is_error":false,'
                      '"result":"%s","usage":{"input_tokens":1,"output_tokens":1}}\\n\' "$FAKE_RESULT"\n')
    claude.chmod(0o755)
    return claude


def run_leaf(tmp_path, name, result):
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True, exist_ok=True)
    (work / "prompt.txt").write_text("Do the step.")
    with open(work / ".tdd" / f"{name}.out", "w") as out:
        ran = subprocess.run([str(SUPERVISE), name, str(RUN_LEAF), "prompt.txt"], cwd=work, stdout=out,
                             stderr=subprocess.DEVNULL, env={**os.environ, "CLAUDE_BIN": str(leaf_stub(tmp_path)),
                                                            "FAKE_RESULT": result, "VERI_ISSUE": "1"})
    return work, ran.returncode


@pytest.mark.process("supervise.sh launching a stub leaf, then suite-reported.sh")
def test_suite_reported_leaf_exit_0_with_no_suite_line_exit_2(tmp_path):
    work, leaf_code = run_leaf(tmp_path, "develop-diff", "Waiting on the make test run to exit.")

    assert leaf_code == 0
    assert check(work, "develop-diff") == 2


@pytest.mark.process("supervise.sh launching a stub leaf, then suite-reported.sh")
def test_suite_reported_leaf_exit_0_with_suite_green_line_exit_0(tmp_path):
    work, leaf_code = run_leaf(tmp_path, "develop-green", "SUITE: GREEN — 3 suites passed")

    assert leaf_code == 0
    assert check(work, "develop-green") == 0


@pytest.mark.process("suite-reported.sh run as a script")
def test_suite_reported_report_missing_event_on_exit_2_naming_leaf_and_suite_none_on_exit_0(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd/develop-diff.out").write_text("Waiting on the make test run to exit.\n")
    (tmp_path / ".tdd/develop-green.out").write_text("SUITE: GREEN - 3 suites passed\n")
    events = tmp_path / ".tdd/events.jsonl"

    assert check(tmp_path, "develop-green") == 0
    assert not events.exists() or events.read_text() == ""

    assert check(tmp_path, "develop-diff") == 2
    logged = [json.loads(line) for line in events.read_text().splitlines()]
    assert [e["event"] for e in logged] == ["report-missing"]
    assert logged[0]["name"] == "develop-diff"
    assert logged[0]["missing"] == "SUITE"
