"""Cases for drop-ledger-step.sh that start the real entry point."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

SEED = (
    "# Plan for #42\n\n"
    "- [x] lowercase the slug ⟦criterion 1⟧\n"
    "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    "- [ ] strip edge hyphens ⟦criterion 3⟧\n"
)

# The script commits with the repo's own identity (no fallback), so a runner with none needs one handed in.
IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}


@pytest.mark.process("drop-ledger-step.sh run on a ledger committed in a scratch git repository")
def test_issue_3692_drop_ledger_step_removes_the_named_unchecked_step_and_keeps_every_other_line(tmp_path):
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "l.md").write_text(SEED)
    subprocess.run([*git, "add", "l.md"], cwd=tmp_path, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "plan"], cwd=tmp_path, check=True)

    ran = subprocess.run([str(SCRIPTS / "drop-ledger-step.sh"), "l.md", "collapse to single hyphen"],
                         cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                         env={**os.environ, **IDENT})

    assert ran.returncode == 0
    assert (tmp_path / "l.md").read_text() == SEED.replace("- [ ] collapse to single hyphen ⟦criterion 2⟧\n", "")


@pytest.mark.process("drop-ledger-step.sh refusals, on a ledger in a scratch git repository")
def test_issue_3692_drop_ledger_step_refuses_bad_calls_and_changes_nothing(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    ledger = tmp_path / "l.md"
    ledger.write_text(SEED)
    script = str(SCRIPTS / "drop-ledger-step.sh")

    def run(argv):
        return subprocess.run(argv, cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    bare = run([script])
    extra = run([script, "l.md", "collapse to single hyphen", "surplus"])
    none = run([script, "l.md", "no such step"])
    many = run([script, "l.md", "hyphen"])
    ticked = run([script, "l.md", "lowercase the slug"])

    assert (bare.returncode, "usage" in bare.stderr.lower()) == (2, True)
    assert (extra.returncode, "usage" in extra.stderr.lower()) == (2, True)
    assert (none.returncode, many.returncode, ticked.returncode) == (1, 1, 1)
    assert "ticked" in ticked.stderr
    assert ledger.read_text() == SEED


@pytest.mark.process("drop-ledger-step.sh run on a ledger committed in a scratch git repository, then git read back")
def test_issue_3692_drop_ledger_step_commits_the_removal_as_a_plan_commit_holding_only_the_ledger(tmp_path):
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]

    def out(*args):
        return subprocess.run([*git, *args], cwd=tmp_path, check=True, capture_output=True, text=True).stdout

    subprocess.run([*git, "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "l.md").write_text(SEED)
    (tmp_path / "other.txt").write_text("committed\n")
    out("add", "l.md", "other.txt")
    out("commit", "-q", "-m", "plan")
    before = out("rev-parse", "HEAD")
    (tmp_path / "other.txt").write_text("dirty\n")

    ran = subprocess.run([str(SCRIPTS / "drop-ledger-step.sh"), "l.md", "collapse to single hyphen"],
                         cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                         env={**os.environ, **IDENT})

    assert ran.returncode == 0
    assert out("status", "--porcelain") == " M other.txt\n"
    assert out("rev-parse", "HEAD~1") == before
    assert out("log", "-1", "--format=%s").startswith("plan:")
    assert out("show", "--name-only", "--format=", "HEAD").split() == ["l.md"]
    assert "collapse to single hyphen" not in out("show", "HEAD:l.md")


@pytest.mark.process("drop-ledger-step.sh run on a ledger outside any git work tree")
def test_issue_3692_drop_ledger_step_fails_loudly_outside_a_git_work_tree_and_leaves_the_ledger(tmp_path):
    (tmp_path / "l.md").write_text(SEED)

    ran = subprocess.run([str(SCRIPTS / "drop-ledger-step.sh"), "l.md", "collapse to single hyphen"],
                         cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                         env={**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path.parent)})

    assert ran.returncode == 2
    assert len(ran.stderr.strip().splitlines()) == 1
    assert "git" in ran.stderr
    assert (tmp_path / "l.md").read_text() == SEED
