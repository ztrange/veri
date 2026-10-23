"""Cases for veri/ledger_growth.py that start a real process."""
import importlib
import subprocess

import pytest


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, stdout=subprocess.PIPE, text=True).stdout


@pytest.mark.process("git")
def test_2213_record_existing_writes_a_record_per_step_the_plan_commit_lacked_and_the_check_then_exits_0(
        tmp_path, run_cli):
    ledger_growth = importlib.import_module("veri.ledger_growth")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    planned = "# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n"
    ledger.write_text(planned)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    plan_sha = git(repo, "rev-parse", "HEAD").strip()
    plan = tmp_path / "plan.md"
    plan.write_text(planned)
    lines = [
        "- [ ] repair the suite ⟦suite-repair⟧ ⟦criterion 1⟧",
        "- [ ] repair the ci ⟦ci-repair⟧ ⟦criterion 1⟧",
        "- [ ] a wheel turns ⟦added⟧ ⟦criterion 1⟧",
        "- [ ] a gear meshes ⟦criterion 3⟧",
    ]
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n" + "\n".join(lines) + "\n")
    git(repo, "commit", "-q", "-am", "chore: step done (#42)")
    assert git(repo, "log", "-1", "--format=%H", "--grep=^plan: ").strip() == plan_sha
    before = run_cli(ledger_growth, [str(plan), str(ledger)])
    recorded = run_cli(ledger_growth, ["record-existing", str(ledger)], cwd=repo)
    after = run_cli(ledger_growth, [str(plan), str(ledger)])
    added = repo / ".tdd" / "issue-42-added.md"
    assert (before[0], recorded[0], added.read_text() if added.exists() else None, after[0]) == (
        1, 0, "".join(line + "\n" for line in lines), 0)
