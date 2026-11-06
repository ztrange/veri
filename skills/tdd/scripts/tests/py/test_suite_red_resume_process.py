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


@pytest.mark.process("suite-red-resume.sh over a real git repository whose HEAD is a rebased tip")
def test_2884_rebased_tip_inserts_one_suite_repair_step_after_the_last_done_step_and_leaves_head(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [x] a wheel turns ⟦criterion 2⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    pre_rebase = git(repo, "rev-parse", "HEAD").strip()
    (repo / "main.txt").write_text("landed on main\n")
    git(repo, "add", "main.txt")
    git(repo, "commit", "-q", "-m", "feat: main moved (#1)")
    head = git(repo, "rev-parse", "HEAD").strip()
    red = tmp_path / "red"
    red.write_text("test_a.py — FAIL a\ntest_b.py\n")
    step = "- [ ] fix the full-suite failure: test_a.py — FAIL a; test_b.py ⟦suite-repair⟧ ⟦criterion 2⟧"

    ran = script("suite-red-resume.sh", "rebased-tip", str(ledger), str(red), pre_rebase, cwd=repo)

    lines = ledger.read_text().split("\n")
    assert ran[0] == 0, ran
    assert lines.count(step) == 1 and lines.index(step) == lines.index("- [x] a wheel turns ⟦criterion 2⟧") + 1
    assert "suite-repair" in (repo / ".tdd" / "issue-42-added.md").read_text()
    assert git(repo, "rev-parse", "HEAD").strip() == head


@pytest.mark.process("suite-red-resume.sh over a real git repository whose HEAD is a hand-resolved rebased tip")
def test_2884_rebased_tip_whose_rebase_conflicted_and_was_resolved_by_hand_inserts_the_step_and_keeps_that_tip(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [x] a wheel turns ⟦criterion 2⟧\n")
    (repo / "shared.txt").write_text("base\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    git(repo, "checkout", "-q", "-b", "tdd/42")
    (repo / "shared.txt").write_text("branch\n")
    git(repo, "commit", "-q", "-am", "feat: branch edit (#42)")
    pre_rebase = git(repo, "rev-parse", "HEAD").strip()
    git(repo, "checkout", "-q", "main")
    (repo / "shared.txt").write_text("main\n")
    git(repo, "commit", "-q", "-am", "feat: main edit (#1)")
    git(repo, "checkout", "-q", "tdd/42")
    conflicted = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com",
                                 "rebase", "main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert conflicted.returncode != 0
    (repo / "shared.txt").write_text("branch and main\n")
    git(repo, "add", "shared.txt")
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com",
                    "-c", "core.editor=true", "rebase", "--continue"], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    head = git(repo, "rev-parse", "HEAD").strip()
    red = tmp_path / "red"
    red.write_text("test_a.py — FAIL a\ntest_b.py\n")
    step = "- [ ] fix the full-suite failure: test_a.py — FAIL a; test_b.py ⟦suite-repair⟧ ⟦criterion 2⟧"

    ran = script("suite-red-resume.sh", "rebased-tip", str(ledger), str(red), pre_rebase, cwd=repo)

    lines = ledger.read_text().split("\n")
    assert head != pre_rebase
    assert ran[0] == 0, ran
    assert lines.count(step) == 1
    assert git(repo, "rev-parse", "HEAD").strip() == head
    assert (repo / "shared.txt").read_text() == "branch and main\n"


@pytest.mark.process("suite-red-resume.sh over a real git repository whose ledger already holds a done suite-repair step")
def test_2884_rebased_tip_on_a_ledger_already_holding_a_suite_repair_step_exits_1_and_adds_no_step(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [x] a wheel turns ⟦criterion 2⟧\n"
                      "- [x] fix the full-suite failure: test_a.py ⟦suite-repair⟧ ⟦criterion 2⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    pre_rebase = git(repo, "rev-parse", "HEAD").strip()
    (repo / "main.txt").write_text("landed on main\n")
    git(repo, "add", "main.txt")
    git(repo, "commit", "-q", "-m", "feat: main moved (#1)")
    red = tmp_path / "red"
    red.write_text("test_b.py — FAIL b\n")
    before = ledger.read_text()

    ran = script("suite-red-resume.sh", "rebased-tip", str(ledger), str(red), pre_rebase, cwd=repo)

    assert ran[0] == 1, ran
    assert ledger.read_text() == before


@pytest.mark.process("suite-red-resume.sh over a real git repository whose rebased tip is refused a second repair step")
def test_2884_rebased_tip_refused_by_exit_1_resets_hard_to_the_pre_rebase_sha(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [x] a wheel turns ⟦criterion 2⟧\n"
                      "- [x] fix the full-suite failure: test_a.py ⟦suite-repair⟧ ⟦criterion 2⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    pre_rebase = git(repo, "rev-parse", "HEAD").strip()
    (repo / "main.txt").write_text("landed on main\n")
    git(repo, "add", "main.txt")
    git(repo, "commit", "-q", "-m", "feat: main moved (#1)")
    assert git(repo, "rev-parse", "HEAD").strip() != pre_rebase
    red = tmp_path / "red"
    red.write_text("test_b.py — FAIL b\n")

    ran = script("suite-red-resume.sh", "rebased-tip", str(ledger), str(red), pre_rebase, cwd=repo)

    assert ran[0] == 1, ran
    assert git(repo, "rev-parse", "HEAD").strip() == pre_rebase
    assert not (repo / "main.txt").exists()


@pytest.mark.process("suite-red-resume.sh over a real git repository whose HEAD is a rebased tip")
def test_2884_rebased_tip_exit_0_records_the_pre_rebase_sha_in_rebase_lease_beside_the_ledger(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    ledger = repo / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [x] a wheel turns ⟦criterion 2⟧\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope #42 (#42)")
    pre_rebase = git(repo, "rev-parse", "HEAD").strip()
    (repo / "main.txt").write_text("landed on main\n")
    git(repo, "add", "main.txt")
    git(repo, "commit", "-q", "-m", "feat: main moved (#1)")
    red = tmp_path / "red"
    red.write_text("test_a.py — FAIL a\n")

    ran = script("suite-red-resume.sh", "rebased-tip", str(ledger), str(red), pre_rebase, cwd=repo)

    assert ran[0] == 0, ran
    lease = repo / ".tdd" / "rebase-lease"
    assert lease.exists() and lease.read_text().strip() == pre_rebase


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository and a stub alone-cmd")
def test_3113_test_only_exits_0_when_the_tree_differs_from_base_in_test_files_only_and_every_suite_passes_alone(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "prod.py").write_text("VALUE = 1\n")
    (repo / "tests" / "test_a.py").write_text("SHA = 'abc1234'\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text("SHA = '" + "a" * 40 + "'\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 0, ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository and a recording alone-cmd")
def test_3113_test_only_runs_every_named_suite_alone_through_the_alone_cmd_before_exiting_0(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "prod.py").write_text("VALUE = 1\n")
    (repo / "tests" / "test_a.py").write_text("SHA = 'abc1234'\n")
    (repo / "tests" / "test_b.py").write_text("SHA = 'abc1234'\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text("SHA = '" + "a" * 40 + "'\n")
    (repo / "tests" / "test_b.py").write_text("SHA = '" + "b" * 40 + "'\n")
    log = tmp_path / "ran-alone.log"

    ran = script("suite-red-resume.sh", "test-only", base, f'echo "$1" >> {log}', "tests/test_a.py", "tests/test_b.py",
                 cwd=repo)

    assert ran[0] == 0, ran
    assert log.read_text().split() == ["tests/test_a.py", "tests/test_b.py"]


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository and a failing alone-cmd")
def test_3113_test_only_exits_1_naming_the_suite_on_stderr_when_a_named_suite_is_still_red_alone(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "prod.py").write_text("VALUE = 1\n")
    (repo / "tests" / "test_a.py").write_text("SHA = 'abc1234'\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text("SHA = '" + "a" * 40 + "'\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 1\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 1, ran
    assert "tests/test_a.py" in ran[2], ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository whose diff deletes a test case")
def test_3113_test_only_exits_1_naming_the_case_on_stderr_when_the_diff_deletes_a_case_base_holds(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "prod.py").write_text("VALUE = 1\n")
    (repo / "tests" / "test_a.py").write_text(
        "def test_keeps():\n    assert True\n\n\ndef test_doomed_case():\n    assert True\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text("def test_keeps():\n    assert True\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 1, ran
    assert "test_doomed_case" in ran[2], ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository whose diff moves a test case")
def test_3113_test_only_exits_0_when_the_diff_moves_a_case_base_holds(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "prod.py").write_text("VALUE = 1\n")
    (repo / "tests" / "test_a.py").write_text(
        "def test_first():\n    assert True\n\n\ndef test_moved_case():\n    assert True\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text(
        "def test_moved_case():\n    assert True\n\n\ndef test_first():\n    assert True\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 0, ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository whose diff removes an assertion from a kept case")
def test_3113_test_only_exits_1_naming_the_case_on_stderr_when_the_diff_removes_an_assertion_from_a_case_it_keeps(
        tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "prod.py").write_text("VALUE = 1\n")
    (repo / "tests" / "test_a.py").write_text(
        "def test_weakened_case():\n    assert VALUE == 1\n    assert VALUE != 2\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text("def test_weakened_case():\n    assert VALUE == 1\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 1, ran
    assert "test_weakened_case" in ran[2], ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository whose diff touches a production file")
def test_3113_test_only_exits_1_naming_the_production_file_on_stderr_when_the_diff_touches_one_whatever_the_suites_do(
        tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "prod.py").write_text("VALUE = 1\n")
    (repo / "tests" / "test_a.py").write_text("SHA = 'abc1234'\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "prod.py").write_text("VALUE = 2\n")
    (repo / "tests" / "test_a.py").write_text("SHA = '" + "a" * 40 + "'\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 1, ran
    assert "prod.py" in ran[2], ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository whose diff deletes a case holding no assert")
def test_3113_test_only_exits_1_naming_a_deleted_case_that_holds_no_assert_line(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "tests" / "test_a.py").write_text(
        "def test_keeps():\n    pass\n\n\ndef test_doomed_bare_case():\n    pass\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text("def test_keeps():\n    pass\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 1, ran
    assert "test_doomed_bare_case is deleted" in ran[2], ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository and a base sha git cannot resolve")
def test_3113_test_only_exits_2_with_one_stderr_line_when_the_base_sha_does_not_resolve(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "tests" / "test_a.py").write_text("SHA = 'abc1234'\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", "deadbeef", str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 2, ran
    assert len(ran[2].splitlines()) == 1 and "deadbeef" in ran[2], ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository holding an untracked production file")
def test_3113_test_only_exits_1_naming_an_untracked_production_file(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "tests" / "test_a.py").write_text("SHA = 'abc1234'\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_a.py").write_text("SHA = '" + "a" * 40 + "'\n")
    (repo / "newprod.py").write_text("VALUE = 1\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_a.py", cwd=repo)

    assert ran[0] == 1, ran
    assert "newprod.py" in ran[2], ran


@pytest.mark.process("suite-red-resume.sh test-only over a real git repository holding an untracked test file")
def test_3113_test_only_exits_0_for_an_untracked_test_file(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "tests" / "test_a.py").write_text("SHA = 'abc1234'\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "tests" / "test_new.py").write_text("def test_new():\n    assert True\n")
    alone = tmp_path / "alone.sh"
    alone.write_text("#!/bin/sh\nexit 0\n")
    alone.chmod(0o755)

    ran = script("suite-red-resume.sh", "test-only", base, str(alone), "tests/test_new.py", cwd=repo)

    assert ran[0] == 0, ran
