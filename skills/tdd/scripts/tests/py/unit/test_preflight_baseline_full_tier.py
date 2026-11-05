"""What skills/tdd/PREFLIGHT.md step 3 tells a conductor about reusing a measured full-tier time, read as text."""
import pathlib
import re

PREFLIGHT = pathlib.Path(__file__).resolve().parents[4] / "PREFLIGHT.md"


def test_2847_preflight_step_3_names_both_baseline_full_tier_modes_the_fallback_to_a_real_run_and_the_fast_tier_baseline_in_both():
    text = PREFLIGHT.read_text()
    start = re.search(r"^3\. ", text, re.M)
    end = re.search(r"^4\. ", text, re.M)
    assert start and end, "PREFLIGHT.md has no numbered steps 3 and 4"
    step = " ".join(text[start.start():end.start()].split())
    assert re.search(r"VERI_BASELINE_FULL_TIER` takes `run`, the default, or `reuse`", step), "step 3 names no run/reuse modes"
    assert re.search(r"no usable time, the full tier runs anyway", step), "step 3 states no fallback to a real full-tier run"
    assert re.search(r"fast-tier baseline runs in both modes", step), "step 3 does not say the fast-tier baseline runs in both modes"


def test_2847_skill_draft_pr_step_names_full_tier_time_sh_as_where_a_green_branch_full_run_records_its_time():
    text = (PREFLIGHT.parent / "SKILL.md").read_text()
    start = re.search(r"^### 4\. ", text, re.M)
    assert start, "SKILL.md has no numbered section 4"
    end = re.search(r"^#{1,3} ", text[start.end():], re.M)
    section = " ".join(text[start.start():start.end() + (end.start() if end else len(text))].split())
    assert re.search(r"green, record its elapsed seconds and its command with `\$S/full-tier-time\.sh --record", section), \
        "the Draft PR step does not say a green branch full run records its time through $S/full-tier-time.sh"
