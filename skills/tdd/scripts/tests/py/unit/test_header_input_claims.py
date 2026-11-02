"""In-process case: script headers state no stale input claims."""
import re

from conftest import ROOT

SCRIPTS = ROOT / "skills" / "tdd" / "scripts"


def header(path):
    lines = path.read_text().splitlines()[1:]
    out = []
    for line in lines:
        if not line.startswith("#"):
            break
        out.append(line)
    return " ".join(out)


def test_2524_headers_and_blind_bullet_state_no_stale_input_claims():
    bvp = SCRIPTS / "build-verify-prompt.sh"
    dtc = SCRIPTS / "detect-test-command.sh"
    stale = []
    if re.search(r"only inputs are", " ".join(header(bvp).split())):
        stale.append("skills/tdd/scripts/build-verify-prompt.sh: header claims its only inputs are the spec and the test")
    dtc_purpose = dtc.read_text().splitlines()[1]
    if "the full suite of a repo" in dtc_purpose or "tier asked for" not in dtc_purpose:
        stale.append("skills/tdd/scripts/detect-test-command.sh: header does not say it prints the command of the tier asked for")
    assert stale == []
