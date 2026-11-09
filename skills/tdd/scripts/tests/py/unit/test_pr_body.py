"""In-process cases for veri/pr_body.py, the module pr-body.sh is a shim over."""
import importlib
import json
import subprocess

import pytest


@pytest.fixture
def pr_body():
    return importlib.import_module("veri.pr_body")


def test_main_with_no_argument_exits_2_with_a_usage_line_naming_pr_number_and_body_file_3453(run_cli, pr_body):
    code, out, err = run_cli(pr_body, [])

    assert (code, out) == (2, "")
    assert "pr-body.sh <pr-number> <body-file>" in err


BEGIN, END = "<!-- veri:run-body -->", "<!-- /veri:run-body -->"


def fake_gh_pr_body(monkeypatch, current):
    """subprocess.run answered as GitHub: a body read gives <current>; a body write is recorded. Returns the written bodies."""
    written = []

    def fake_run(args, **kwargs):
        args = tuple(str(arg) for arg in args)
        body = [a[len("body="):] for a in args if a.startswith("body=")]
        if kwargs.get("input") is not None:
            body.append(kwargs["input"])
        if body:
            written.extend(body)
            return subprocess.CompletedProcess(args, 0, "{}", "")
        out = current if ("--jq" in args or "-q" in args) else json.dumps({"body": current})
        return subprocess.CompletedProcess(args, 0, out, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return written


def test_main_keeps_review_notes_appended_after_the_runs_part_and_rewrites_only_the_runs_part_3453(run_cli, pr_body, monkeypatch, tmp_path):
    notes = "## Review notes\n\n- the subagent found a gap\n"
    current = "%s\nCloses #7 — work in progress: 2 of 5 steps done\n%s\n\n%s" % (BEGIN, END, notes)
    written = fake_gh_pr_body(monkeypatch, current)
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert len(written) == 1
    assert notes in written[0]
    assert "5 of 5 steps done" in written[0]
    assert "2 of 5 steps done" not in written[0]
