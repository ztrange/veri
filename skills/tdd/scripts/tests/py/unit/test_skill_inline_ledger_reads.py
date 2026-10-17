"""Source-text audit of SKILL.md: the conductor reads the ledger through ledger-steps.sh, never an inline pipeline."""
import pathlib

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

TITLE = "# tdd — the veri conductor"
INLINE_READS = ("|| $S/next-unchecked.sh", "|| cat .tdd/issue-<n>.md", "tail -1 | cut -f7-", "sed -n '<k>p'")


def test_skill_md_spells_none_of_the_inline_current_step_last_done_and_criterion_k_pipelines_reading_each_through_ledger_steps_sh_current_last_done_and_criterion_k():
    lines = skill_sections.section(SKILL, TITLE).splitlines()

    offenders = [line for line in lines if any(read in line for read in INLINE_READS)]

    assert offenders == [], "spells a ledger read inline, want ledger-steps.sh current, last-done or criterion <k>"
