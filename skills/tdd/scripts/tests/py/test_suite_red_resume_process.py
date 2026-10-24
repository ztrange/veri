"""Conductor-level cases for suite-red-resume.sh: real scripts over a real git repository."""
import json
import subprocess

import pytest

from conftest import SCRIPTS


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, stdout=subprocess.PIPE, text=True).stdout


def script(name, *argv, cwd, stdin=None):
    ran = subprocess.run([str(SCRIPTS / name), *argv], cwd=cwd, input=stdin, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, stdin=None if stdin is not None else subprocess.DEVNULL)
    return ran.returncode, ran.stdout, ran.stderr


@pytest.mark.process("suite-red-resume.sh, next-unchecked.sh and ledger-growth.sh over a real git repository")
def test_2226_a_resume_after_a_suite_red_bail_inserts_one_suite_repair_step_for_branch_red_suites_and_refuses_one_also_red_on_default(
        tmp_path):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    planned = "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n"
    ledger.write_text(planned)
    plan = tmp_path / "plan.md"
    plan.write_text(planned)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    events = repo / ".tdd" / "events.jsonl"
    events.write_text("".join(json.dumps(e) + "\n" for e in (
        {"event": "bail", "cause": "suite-red"}, {"event": "resume"})))
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\ntest_b.py\n")
    green = tmp_path / "default-green"
    green.write_text("none\n")
    red_too = tmp_path / "default-red"
    red_too.write_text("test_b.py — FAIL b\n")
    step = "- [ ] fix the full-suite failure: test_a.py — FAIL a; test_b.py ⟦suite-repair⟧ ⟦criterion 2⟧"

    refused = script("suite-red-resume.sh", "check", str(ledger), str(branch), str(red_too), cwd=repo)
    untouched = ledger.read_text()
    checked = script("suite-red-resume.sh", "check", str(ledger), str(branch), str(green), cwd=repo)
    inserted = script("suite-red-resume.sh", "insert", str(ledger), str(branch), cwd=repo)
    handed = script("next-unchecked.sh", cwd=repo, stdin=ledger.read_text())
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "chore: suite-repair step inserted (#42)")
    grown = script("ledger-growth.sh", str(plan), str(ledger), cwd=repo)

    assert refused[0] == 1 and "test_b.py" in refused[2] and "test_a.py" not in refused[2]
    assert untouched == planned
    assert checked[:2] == (0, "test_a.py — FAIL a\ntest_b.py\n")
    assert inserted[0] == 0
    assert ledger.read_text().count("⟦suite-repair⟧") == 1 and step in ledger.read_text().split("\n")
    assert handed[:2] == (0, step[len("- [ ] "):] + "\n")
    assert grown[0] == 0
