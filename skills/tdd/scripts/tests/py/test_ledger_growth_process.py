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


@pytest.mark.process("git")
def test_2213_record_existing_refuses_when_the_added_file_already_exists_and_leaves_it_byte_identical(
        tmp_path, run_cli):
    ledger_growth = importlib.import_module("veri.ledger_growth")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦added⟧ ⟦criterion 1⟧\n")
    git(repo, "commit", "-q", "-am", "chore: step added (#42)")
    added = repo / ".tdd" / "issue-42-added.md"
    existing = b"- [ ] a hand-written record \xe2\x9f\xa6added\xe2\x9f\xa7\n"
    added.write_bytes(existing)
    code, _, err = run_cli(ledger_growth, ["record-existing", str(ledger)], cwd=repo)
    assert (code, added.read_bytes(), "issue-42-added.md" in err) == (2, existing, True)


@pytest.mark.process("git")
def test_2213_record_existing_exits_2_naming_the_cause_and_writes_nothing_when_the_history_holds_no_plan_commit(
        tmp_path, run_cli):
    ledger_growth = importlib.import_module("veri.ledger_growth")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "chore: a ledger without a plan commit (#42)")
    code, _, err = run_cli(ledger_growth, ["record-existing", str(ledger)], cwd=repo)
    added = repo / ".tdd" / "issue-42-added.md"
    assert (code, added.exists(), "no plan commit" in err) == (2, False, True)


@pytest.mark.process("git")
def test_2213_record_existing_exits_2_naming_the_cause_and_writes_nothing_when_the_ledger_cannot_be_read(
        tmp_path, run_cli):
    ledger_growth = importlib.import_module("veri.ledger_growth")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    ledger.unlink()
    code, _, err = run_cli(ledger_growth, ["record-existing", str(ledger)], cwd=repo)
    added = repo / ".tdd" / "issue-42-added.md"
    assert (code, added.exists(), "cannot read" in err) == (2, False, True)


@pytest.mark.process("git")
def test_2213_record_existing_takes_its_baseline_from_the_newest_of_two_plan_commits(tmp_path, run_cli):
    ledger_growth = importlib.import_module("veri.ledger_growth")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n")
    git(repo, "commit", "-q", "-am", "plan: rewrite #42's plan (#42)")
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n"
                      "- [ ] a gear meshes ⟦added⟧ ⟦criterion 2⟧\n")
    git(repo, "commit", "-q", "-am", "chore: step added (#42)")

    code, _, err = run_cli(ledger_growth, ["record-existing", str(ledger)], cwd=repo)

    assert (code, (repo / ".tdd" / "issue-42-added.md").read_text()) == (
        0, "- [ ] a gear meshes ⟦added⟧ ⟦criterion 2⟧\n"), err


@pytest.mark.process("git")
def test_4251_split_reads_the_oldest_plan_scope_commit_of_the_ledgers_own_history_from_a_real_repository(
        tmp_path, run_cli):
    ledger_growth = importlib.import_module("veri.ledger_growth")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [ ] another issue's only step ⟦criterion 1⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #7 into 1 step (#7)")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 into 2 steps (#42)")
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n"
                      "- [ ] a gear meshes ⟦criterion 2⟧\n")
    git(repo, "commit", "-q", "-am", "plan: rewrite #42 after verify-plan (#42)")
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n"
                      "- [ ] a gear meshes ⟦criterion 2⟧\n- [ ] a belt runs ⟦criterion 3⟧\n")
    git(repo, "commit", "-q", "-am", "plan: rewrite #42 on the owner's answer (#42)")

    (repo / ".tdd" / "issue-9.md").write_text("# Plan for #9\n\n- [ ] never committed ⟦criterion 1⟧\n")
    grown = run_cli(ledger_growth, ["split", ".tdd/issue-42.md"], env={"VERI_STEP_GROWTH_PERCENT": "50"}, cwd=repo)
    unscoped = run_cli(ledger_growth, ["split", ".tdd/issue-9.md"], cwd=repo)

    assert grown == (0, "plan grew from 2 to 4 steps, past the growth bound of 1 (VERI_STEP_GROWTH_PERCENT 50% of 2,"
                        " rounded up)\nsplit suggested after criterion 1: criteria 1–1 (1 steps) here, criteria 2–3"
                        " (3 steps) in a follow-up issue\n", "")
    assert (unscoped[0], unscoped[1]) == (2, "")
