"""In-process cases for the two root documents' record of the per-role model tunables."""
import re

from conftest import ROOT
from skill_sections import LOWER, lines_of

SUPERVISE_SH = "skills/tdd/scripts/supervise.sh"


def test_1485_supervise_shs_tunables_env_header_names_all_four_model_knobs_and_the_shipped_defaults_sonnet_and_opus_and_no_longer_says_a_default_run_carries_no_model():
    on, body = False, []
    for line in lines_of(ROOT / SUPERVISE_SH):
        if re.match(r"# Tunables \(env\)", line):
            on = True
        if on and line.startswith("#"):
            body.append(line)
        elif on:
            break
    header = "".join(line.translate(LOWER) + " " for line in body)
    problems = []
    for want in ("veri_model_developer", "veri_model_verifier", "veri_model_revise", "sonnet", "opus"):
        if want not in header:
            problems.append(f"supervise.sh's Tunables header does not name {want}")
    if re.search(r"no `?--model", header):
        problems.append("supervise.sh's Tunables header still says a default run carries no --model")
    assert problems == []
