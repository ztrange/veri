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


def test_main_writes_a_run_part_holding_backslash_sequences_verbatim_3453(run_cli, pr_body, monkeypatch, tmp_path):
    mine = "Closes #7 — keeps \\1 and \\g<0> and a lone \\"
    current = "%s\nCloses #7 — work in progress\n%s\n\n## Review notes\n" % (BEGIN, END)
    written = fake_gh_pr_body(monkeypatch, current)
    body_file = tmp_path / "body.md"
    body_file.write_text(mine)

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert written == ["%s\n%s\n%s\n\n## Review notes\n" % (BEGIN, mine, END)]


def test_main_on_a_body_with_no_run_part_writes_the_file_as_the_run_part_so_the_next_write_keeps_appended_notes_3453(run_cli, pr_body, monkeypatch, tmp_path):
    notes = "## Review notes\n\n- appended later\n"
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")
    first = fake_gh_pr_body(monkeypatch, "")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert first == ["%s\nCloses #7 — ready: 5 of 5 steps done\n%s" % (BEGIN, END)]

    second = fake_gh_pr_body(monkeypatch, first[0] + "\n\n" + notes)
    body_file.write_text("Closes #7 — resumed: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert len(second) == 1
    assert notes in second[0]
    assert "resumed" in second[0]
    assert "ready" not in second[0]


def test_main_when_the_current_body_cannot_be_read_exits_2_naming_the_pr_and_writes_nothing_3453(run_cli, pr_body, monkeypatch, tmp_path):
    calls = []

    def fake_run(args, **kwargs):
        args = tuple(str(arg) for arg in args)
        calls.append(args)
        return subprocess.CompletedProcess(args, 1, "", "HTTP 502")

    monkeypatch.setattr(subprocess, "run", fake_run)
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 2
    assert "42" in err
    assert [c for c in calls if "PATCH" in c or any(a.startswith("body=") for a in c)] == []


def test_main_on_a_null_body_treats_it_as_empty_and_writes_the_file_as_the_run_part_3453(run_cli, pr_body, monkeypatch, tmp_path):
    written = fake_gh_pr_body(monkeypatch, None)
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert written == ["%s\n%s\n%s" % (BEGIN, "Closes #7 — ready: 5 of 5 steps done", END)]


def test_main_when_the_write_of_the_body_fails_exits_2_naming_the_pr_3453(run_cli, pr_body, monkeypatch, tmp_path):
    def fake_run(args, **kwargs):
        args = tuple(str(arg) for arg in args)
        if "PATCH" in args or any(a.startswith("body=") for a in args):
            return subprocess.CompletedProcess(args, 1, "", "HTTP 502")
        return subprocess.CompletedProcess(args, 0, json.dumps({"body": ""}), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 2
    assert "42" in err


def test_main_on_a_legacy_body_with_no_run_markers_replaces_it_with_the_run_part_alone_3453(run_cli, pr_body, monkeypatch, tmp_path):
    written = fake_gh_pr_body(monkeypatch, "Closes #7 — legacy text a run wrote before markers")
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert written == ["%s\n%s\n%s" % (BEGIN, "Closes #7 — ready: 5 of 5 steps done", END)]
    assert "legacy text" not in written[0]
