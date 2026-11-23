"""This repository's graded prose units owe no grade, audited through prose-owed.sh.
They audit the tree, not prose_owed's logic (tests/py/unit/test_prose_owed.py holds that), and stay subprocess cases:
the module's waiver reads HEAD with git, which no case may start in-process against the repository the tests live in."""
import importlib
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


def graded_units(graded):
    """The units a GRADED file signs, each unit field decoded as grade_prose reads it (#4016)."""
    grade_prose = importlib.import_module("veri.grade_prose")
    return {fields[0] for fields in grade_prose.graded_lines(str(graded)) if fields[0]}


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2307_this_repository_owes_no_grade_for_any_prose_unit():
    repo = SCRIPTS.parents[2]

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2675_the_eight_red_develop_prompt_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "develop-red.md", "develop-red-missing.md", "develop-red-supersede.md", "develop-red-repair.md",
        "_develop-red-valid-test.md", "_develop-red-run-and-report.md",
        "_develop-red-spec-and-testability.md", "_affected-suites-working-tree.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2676_the_nine_green_develop_prompt_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "develop-green.md", "_develop-green-freeze-rule.md", "_develop-green-replaces-case.md",
        "_develop-green-suite-repair.md", "_develop-green-fixture-repair.md",
        "_develop-guard-subject-grant.md", "_develop-repair-test-edit.md", "_develop-split.md",
        "_develop-wrong-test-report.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2682_the_six_verify_fragment_units_are_listed_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "_verify-plan-refactor.md", "_verify-comments-allowed.md", "_verify-comments-never-reject.md",
        "_verify-red-bug.md", "_verify-coverage-probe.md", "_verify-red-fast.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")
    headings = set((repo / prompts / "REQUIREMENTS.md").read_text().splitlines())

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], [u for u in units if "## " + u not in headings],
            ran.returncode, ran.stdout) == ([], [], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2684_the_four_interface_phase_verify_units_are_listed_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "verify-contract-a.md", "verify-contract-b.md", "verify-expand.md", "verify-migrate.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")
    headings = set((repo / prompts / "REQUIREMENTS.md").read_text().splitlines())

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], [u for u in units if "## " + u not in headings],
            ran.returncode, ran.stdout) == ([], [], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2678_the_nine_shared_leaf_rule_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "_develop-shared.md", "_leaf-safety.md", "_probe-restore.md", "_signal-own-processes.md",
        "_shared.md", "_exit-status-back.md", "_run-suite-lead.md", "_run-suite-same-way.md",
        "_develop-run-suite-same-way.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2677_the_refactor_develop_prompt_and_its_two_flag_fragments_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in ("develop-refactor.md", "_flag-uncovered-spec.md", "_flag-beyond-spec.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2680_the_seven_red_slot_filler_and_replaces_report_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "develop-replaces-report.md", "_develop-red-cases-replaces-case.md", "_develop-red-cases.md",
        "_develop-node-id-rule.md", "_develop-red-lead.md", "_develop-red-ci-repair.md",
        "_develop-red-bug.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2681_the_seven_diff_and_revise_slot_filler_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "develop-diff.md", "develop-revise-diff.md", "_develop-diff-run-fast-affected.md",
        "_develop-revise-freeze-test.md", "_develop-revise-freeze-production.md",
        "_develop-test-rewrite-grant.md", "_develop-test-move-contract-a.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2683_the_eight_cover_to_revise_develop_prompt_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "develop-cover.md", "develop-cover-new.md", "develop-transform.md", "develop-structural.md",
        "develop-predicate.md", "develop-exhausted.md", "develop-over-budget.md", "develop-revise.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2685_the_eight_verify_prompt_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "verify-red.md", "verify-green.md", "verify-refactor.md", "verify-pin.md",
        "verify-plan.md", "verify-rebase.md", "verify-transform.md", "verify-diff.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2679_the_five_verify_green_fragment_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    prompts = "skills/tdd/scripts/prompts/"
    units = [prompts + name for name in (
        "_verify-green-replaces-case.md", "_replaces-case-lead.md", "_verify-green-suite-repair.md",
        "_verify-green-ci-repair.md", "_verify-green-fixture-repair.md")]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_2782_the_eleven_wording_rows_sit_under_their_units_and_the_five_units_owe_no_grade():
    repo = SCRIPTS.parents[2]
    owed = {
        "skills/tdd/SKILL.md#The scripts (this skill's `scripts/` directory)":
            ("skills/tdd/REQUIREMENTS.md", ["SS1", "SS2", "SS3"]),
        "skills/tdd/SKILL.md#2. Scope & plan → the ledger": ("skills/tdd/REQUIREMENTS.md", ["PL63"]),
        "skills/tdd/SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)":
            ("skills/tdd/REQUIREMENTS.md", ["CY129"]),
        "skills/tdd/PREFLIGHT.md": ("skills/tdd/REQUIREMENTS.md", ["PF37", "PF38"]),
        "skills/tdd/REFACTOR-KIND.md": ("skills/tdd/REQUIREMENTS.md", ["PL64"]),
        "skills/tdd/scripts/prompts/develop-revise.md": ("skills/tdd/scripts/prompts/REQUIREMENTS.md", ["DV5"]),
        "skills/vdev/SKILL.md": ("skills/vdev/REQUIREMENTS.md", ["D22"]),
    }
    missing = []
    for unit, (path, ids) in owed.items():
        rows, under = set(), False
        for line in (repo / path).read_text().splitlines():
            if line.startswith("## "):
                under = line == "## " + unit
            elif under and line.startswith("|"):
                rows.add(line.split("|")[1].strip())
        missing += [unit + ":" + i for i in ids if i not in rows]
    graded = graded_units(repo / "skills/tdd/GRADED")
    graded |= graded_units(repo / "skills/vdev/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (missing, [u for u in owed if u not in graded], ran.returncode, ran.stdout) == ([], [], 0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script")
@pytest.mark.tree_audit("the repository's own graded prose units")
def test_4472_the_four_branch_stage_prose_units_are_signed_and_owe_no_grade():
    repo = SCRIPTS.parents[2]
    units = ["skills/tdd/DRAFT-PR.md", "skills/tdd/PREFLIGHT.md", "skills/tdd/BAIL.md",
             "skills/tdd/scripts/prompts/verify-branch.md"]
    graded = graded_units(repo / "skills/tdd/GRADED")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(repo)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert ([u for u in units if u not in graded], ran.returncode, ran.stdout) == ([], 0, ""), ran.stderr
