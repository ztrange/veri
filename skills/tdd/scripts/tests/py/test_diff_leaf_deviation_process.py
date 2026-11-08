"""Cases for veri/diff_leaf_deviation.py that start a real process."""
import importlib
import json
import subprocess

import pytest


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, stdout=subprocess.PIPE, text=True).stdout


@pytest.mark.process("git")
def test_issue_3351_one_commit_since_the_step_base_exits_3_writes_no_event_and_stays_head(tmp_path, run_cli):
    diff_leaf_deviation = importlib.import_module("veri.diff_leaf_deviation")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦diff-checked⟧ ⟦criterion 1⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "cog.txt").write_text("cog\n")
    git(repo, "add", "cog.txt")
    git(repo, "commit", "-q", "-m", "feat: a cog (#42)")
    head = git(repo, "rev-parse", "HEAD").strip()

    code, out, err = run_cli(diff_leaf_deviation, ["develop-diff", base, ".tdd/issue-42.md"], cwd=repo)

    events = repo / ".tdd" / "events.jsonl"
    assert (code, events.read_text() if events.exists() else "", git(repo, "rev-parse", "HEAD").strip()) == (3, "", head)


@pytest.mark.process("git")
def test_issue_3351_two_commits_since_the_step_base_exit_0_append_one_event_and_stay_in_place(tmp_path, run_cli):
    diff_leaf_deviation = importlib.import_module("veri.diff_leaf_deviation")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦diff-checked⟧ ⟦criterion 1⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    base = git(repo, "rev-parse", "HEAD").strip()
    for name in ("cog.txt", "wheel.txt"):
        (repo / name).write_text(name + "\n")
        git(repo, "add", name)
        git(repo, "commit", "-q", "-m", "feat: " + name + " (#42)")
    head = git(repo, "rev-parse", "HEAD").strip()

    code, out, err = run_cli(diff_leaf_deviation, ["develop-diff", base, ".tdd/issue-42.md"], cwd=repo)

    events = repo / ".tdd" / "events.jsonl"
    lines = [json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
    found = [(e.get("event"), e.get("leaf"), e.get("base"), e.get("head"), str(e.get("commits"))) for e in lines]
    commits = git(repo, "rev-list", "--count", base + "..HEAD").strip()
    assert (code, found, git(repo, "rev-parse", "HEAD").strip(), commits) == (
        0, [("diff-leaf-deviation", "develop-diff", base, head, "2")], head, "2")
