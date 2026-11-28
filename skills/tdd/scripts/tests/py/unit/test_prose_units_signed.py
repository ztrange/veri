"""This repository's graded prose units carry a GRADED line, and their rows sit under their units.
Plain reads of GRADED and REQUIREMENTS.md: whether a signature is current is prose-owed.sh's to say, and `make test`
and `make unit` run it over the whole tree once (#4837)."""
import importlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
PROMPTS = "skills/tdd/scripts/prompts/"


def graded_units(graded):
    """The units a GRADED file signs, each unit field decoded as grade_prose reads it (#4016)."""
    grade_prose = importlib.import_module("veri.grade_prose")
    return {fields[0] for fields in grade_prose.graded_lines(str(graded)) if fields[0]}


def unsigned(*names):
    graded = graded_units(REPO / "skills/tdd/GRADED")
    return [PROMPTS + n for n in names if PROMPTS + n not in graded]


def unlisted(*names):
    headings = set((REPO / PROMPTS / "REQUIREMENTS.md").read_text().splitlines())
    return [PROMPTS + n for n in names if "## " + PROMPTS + n not in headings]


def test_2675_the_eight_red_develop_prompt_units_are_signed():
    assert unsigned(
        "develop-red.md", "develop-red-missing.md", "develop-red-supersede.md", "develop-red-repair.md",
        "_develop-red-valid-test.md", "_develop-red-run-and-report.md",
        "_develop-red-spec-and-testability.md", "_affected-suites-working-tree.md") == []


def test_2676_the_nine_green_develop_prompt_units_are_signed():
    assert unsigned(
        "develop-green.md", "_develop-green-freeze-rule.md", "_develop-green-replaces-case.md",
        "_develop-green-suite-repair.md", "_develop-green-fixture-repair.md",
        "_develop-guard-subject-grant.md", "_develop-repair-test-edit.md", "_develop-split.md",
        "_develop-wrong-test-report.md") == []


def test_2682_the_six_verify_fragment_units_are_listed_and_signed():
    units = ("_verify-plan-refactor.md", "_verify-comments-allowed.md", "_verify-comments-never-reject.md",
             "_verify-red-bug.md", "_verify-coverage-probe.md", "_verify-red-fast.md")

    assert (unsigned(*units), unlisted(*units)) == ([], [])


def test_2684_the_four_interface_phase_verify_units_are_listed_and_signed():
    units = ("verify-contract-a.md", "verify-contract-b.md", "verify-expand.md", "verify-migrate.md")

    assert (unsigned(*units), unlisted(*units)) == ([], [])


def test_2678_the_nine_shared_leaf_rule_units_are_signed():
    assert unsigned(
        "_develop-shared.md", "_leaf-safety.md", "_probe-restore.md", "_signal-own-processes.md",
        "_shared.md", "_exit-status-back.md", "_run-suite-lead.md", "_run-suite-same-way.md",
        "_develop-run-suite-same-way.md") == []


def test_2677_the_refactor_develop_prompt_and_its_two_flag_fragments_are_signed():
    assert unsigned("develop-refactor.md", "_flag-uncovered-spec.md", "_flag-beyond-spec.md") == []


def test_2680_the_seven_red_slot_filler_and_replaces_report_units_are_signed():
    assert unsigned(
        "develop-replaces-report.md", "_develop-red-cases-replaces-case.md", "_develop-red-cases.md",
        "_develop-node-id-rule.md", "_develop-red-lead.md", "_develop-red-ci-repair.md",
        "_develop-red-bug.md") == []


def test_2681_the_seven_diff_and_revise_slot_filler_units_are_signed():
    assert unsigned(
        "develop-diff.md", "develop-revise-diff.md", "_develop-diff-run-fast-affected.md",
        "_develop-revise-freeze-test.md", "_develop-revise-freeze-production.md",
        "_develop-test-rewrite-grant.md", "_develop-test-move-contract-a.md") == []


def test_2683_the_eight_cover_to_revise_develop_prompt_units_are_signed():
    assert unsigned(
        "develop-cover.md", "develop-cover-new.md", "develop-transform.md", "develop-structural.md",
        "develop-predicate.md", "develop-exhausted.md", "develop-over-budget.md", "develop-revise.md") == []


def test_2685_the_eight_verify_prompt_units_are_signed():
    assert unsigned(
        "verify-red.md", "verify-green.md", "verify-refactor.md", "verify-pin.md",
        "verify-plan.md", "verify-rebase.md", "verify-transform.md", "verify-diff.md") == []


def test_2679_the_five_verify_green_fragment_units_are_signed():
    assert unsigned(
        "_verify-green-replaces-case.md", "_replaces-case-lead.md", "_verify-green-suite-repair.md",
        "_verify-green-ci-repair.md", "_verify-green-fixture-repair.md") == []


def test_2782_the_eleven_wording_rows_sit_under_their_units_and_the_seven_units_are_signed():
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
        for line in (REPO / path).read_text().splitlines():
            if line.startswith("## "):
                under = line == "## " + unit
            elif under and line.startswith("|"):
                rows.add(line.split("|")[1].strip())
        missing += [unit + ":" + i for i in ids if i not in rows]
    graded = graded_units(REPO / "skills/tdd/GRADED") | graded_units(REPO / "skills/vdev/GRADED")

    assert (missing, [u for u in owed if u not in graded]) == ([], [])


def test_4472_the_four_branch_stage_prose_units_are_signed():
    units = ["skills/tdd/DRAFT-PR.md", "skills/tdd/PREFLIGHT.md", "skills/tdd/BAIL.md",
             "skills/tdd/scripts/prompts/verify-branch.md"]
    graded = graded_units(REPO / "skills/tdd/GRADED")

    assert [u for u in units if u not in graded] == []
