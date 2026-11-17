"""In-process cases for veri/pr_body.py, the module pr-body.sh is a shim over."""
import importlib
import json

import pytest


@pytest.fixture
def pr_body():
    return importlib.import_module("veri.pr_body")


def test_main_with_no_argument_exits_2_with_a_usage_line_naming_pr_number_and_body_file_3453(run_cli, pr_body):
    code, out, err = run_cli(pr_body, [])

    assert (code, out) == (2, "")
    assert "pr-body.sh <pr-number> <body-file>" in err


BEGIN, END = "<!-- veri:run-body -->", "<!-- /veri:run-body -->"


def fake_gh_pr_body(fake_processes, current):
    """gh answered as GitHub: a body read gives <current>; a body write is recorded. Returns the written bodies."""
    written = []

    def gh(line, **kwargs):
        words = [str(arg) for arg in fake.argvs[-1]]
        body = [a[len("body="):] for a in words if a.startswith("body=")]
        if kwargs.get("input") is not None:
            body.append(kwargs["input"])
        if body:
            written.extend(body)
            return 0, "{}", ""
        return 0, current if ("--jq" in words or "-q" in words) else json.dumps({"body": current}), ""

    fake = fake_processes.answers({"gh": gh})
    return written


def test_main_keeps_review_notes_appended_after_the_runs_part_and_rewrites_only_the_runs_part_3453(run_cli, pr_body, fake_processes, tmp_path):
    notes = "## Review notes\n\n- the subagent found a gap\n"
    current = "%s\nCloses #7 — work in progress: 2 of 5 steps done\n%s\n\n%s" % (BEGIN, END, notes)
    written = fake_gh_pr_body(fake_processes, current)
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert len(written) == 1
    assert notes in written[0]
    assert "5 of 5 steps done" in written[0]
    assert "2 of 5 steps done" not in written[0]


def test_main_writes_a_run_part_holding_backslash_sequences_verbatim_3453(run_cli, pr_body, fake_processes, tmp_path):
    mine = "Closes #7 — keeps \\1 and \\g<0> and a lone \\"
    current = "%s\nCloses #7 — work in progress\n%s\n\n## Review notes\n" % (BEGIN, END)
    written = fake_gh_pr_body(fake_processes, current)
    body_file = tmp_path / "body.md"
    body_file.write_text(mine)

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert written == ["%s\n%s\n%s\n\n## Review notes\n" % (BEGIN, mine, END)]


def test_main_on_a_body_with_no_run_part_writes_the_file_as_the_run_part_so_the_next_write_keeps_appended_notes_3453(run_cli, pr_body, fake_processes, tmp_path):
    notes = "## Review notes\n\n- appended later\n"
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")
    first = fake_gh_pr_body(fake_processes, "")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert first == ["%s\nCloses #7 — ready: 5 of 5 steps done\n%s" % (BEGIN, END)]

    second = fake_gh_pr_body(fake_processes, first[0] + "\n\n" + notes)
    body_file.write_text("Closes #7 — resumed: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert len(second) == 1
    assert notes in second[0]
    assert "resumed" in second[0]
    assert "ready" not in second[0]


def test_main_writes_the_body_redacted_a_token_and_a_listed_value_replaced_issue_3968(run_cli, pr_body, fake_processes, tmp_path, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    token = "github_pat_" + "FAKEfake0123" * 2 + "_" + "FAKEfake0123" * 5
    written = fake_gh_pr_body(fake_processes, "")
    body_file = tmp_path / "body.md"
    body_file.write_text("step 3 FAIL_OUTPUT: %s fake-gh-token-value" % token)

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert (code, written) == (0, ["%s\nstep 3 FAIL_OUTPUT: [redacted] [redacted]\n%s" % (BEGIN, END)]), err


def test_main_when_the_current_body_cannot_be_read_exits_2_naming_the_pr_and_writes_nothing_3453(run_cli, pr_body, fake_processes, tmp_path):
    fake = fake_processes.answers({"gh": (1, "", "HTTP 502")})
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 2
    assert "42" in err
    assert [c for c in fake.argvs if "PATCH" in c or any(str(a).startswith("body=") for a in c)] == []


def test_main_on_a_null_body_treats_it_as_empty_and_writes_the_file_as_the_run_part_3453(run_cli, pr_body, fake_processes, tmp_path):
    written = fake_gh_pr_body(fake_processes, None)
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert written == ["%s\n%s\n%s" % (BEGIN, "Closes #7 — ready: 5 of 5 steps done", END)]


def test_main_when_the_write_of_the_body_fails_exits_2_naming_the_pr_3453(run_cli, pr_body, fake_processes, tmp_path):
    def gh(line, **kwargs):
        words = [str(arg) for arg in fake.argvs[-1]]
        if "PATCH" in words or any(a.startswith("body=") for a in words):
            return 1, "", "HTTP 502"
        return 0, json.dumps({"body": ""}), ""

    fake = fake_processes.answers({"gh": gh})
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 2
    assert "42" in err


def test_main_on_a_legacy_body_with_no_run_markers_replaces_it_with_the_run_part_alone_3453(run_cli, pr_body, fake_processes, tmp_path):
    written = fake_gh_pr_body(fake_processes, "Closes #7 — legacy text a run wrote before markers")
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert written == ["%s\n%s\n%s" % (BEGIN, "Closes #7 — ready: 5 of 5 steps done", END)]
    assert "legacy text" not in written[0]


def test_main_with_an_extra_argument_exits_2_with_the_usage_line_and_writes_nothing_3453(run_cli, pr_body, fake_processes, tmp_path):
    written = fake_gh_pr_body(fake_processes, "%s\nCloses #7\n%s\n" % (BEGIN, END))
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #7 — ready: 5 of 5 steps done")

    code, out, err = run_cli(pr_body, ["42", str(body_file), "extra"])

    assert (code, out) == (2, "")
    assert "pr-body.sh <pr-number> <body-file>" in err
    assert written == []


def test_main_keeps_foreign_text_between_two_run_parts_byte_identical_3502(run_cli, pr_body, fake_processes, tmp_path):
    foreign = "## Review notes\nhuman text"
    current = "%s\na\n%s\n\n%s\n\n%s\nb\n%s" % (BEGIN, END, foreign, BEGIN, END)
    written = fake_gh_pr_body(fake_processes, current)
    body_file = tmp_path / "body.md"
    body_file.write_text("new")

    code, out, err = run_cli(pr_body, ["42", str(body_file)])

    assert code == 0, err
    assert written == ["%s\nnew\n%s\n\n%s\n\n%s\nnew\n%s" % (BEGIN, END, foreign, BEGIN, END)]


def test_main_writes_no_local_path_host_or_account_name_in_the_lint_section_or_any_other_line_4122(
        run_cli, pr_body, fake_processes, tmp_path, monkeypatch):
    home = tmp_path / "home-of-zorblat"
    run = home / "code" / "repo"
    temp = tmp_path / "temp-of-zorblat"
    run.mkdir(parents=True)
    temp.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(temp))
    monkeypatch.setattr(importlib.import_module("tempfile"), "tempdir", str(temp))
    monkeypatch.setattr(importlib.import_module("socket"), "gethostname", lambda: "zorblat-mbp.local")
    written = fake_gh_pr_body(fake_processes, "")
    body_file = tmp_path / "body.md"
    body_file.write_text(
        "## Summary\nbuilt in %s/scratch on zorblat-mbp as home-of-zorblat\n\n"
        "### Lint\n\n`make lint` exited 1.\n\n~~~text\n%s/src/a.py:3: E1 unused\n"
        "/var/folders/ab/cd0123/T/tmp9/x.py:1: E2\n%s/notes.txt: W3 (home-of-zorblat@zorblat-mbp)\n~~~\n"
        % (temp, str(run).lower(), home))

    code, out, err = run_cli(pr_body, ["42", str(body_file)], cwd=str(run))

    sent = written[0].lower() if written else ""
    assert (code, err, [leak for leak in (str(tmp_path).lower(), "/var/folders/", "zorblat-mbp", "home-of-zorblat")
                        if leak in sent], "`make lint` exited 1." in sent) == (0, "", [], True)
