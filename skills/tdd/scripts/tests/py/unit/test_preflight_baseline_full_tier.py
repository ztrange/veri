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
