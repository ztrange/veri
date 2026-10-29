"""In-process case: script headers and CLAUDE.md state no stale input claims."""
import re

from skill_sections import ROOT

SCRIPTS = ROOT / "skills" / "tdd" / "scripts"


def header(path):
    lines = path.read_text().splitlines()[1:]
    out = []
    for line in lines:
        if not line.startswith("#"):
            break
        out.append(line)
    return " ".join(out)


def blind_bullet():
    text = (ROOT / "CLAUDE.md").read_text()
    m = re.search(r"- \*\*The verifier is blind by construction\.\*\*.*?(?=\n- \*\*)", text, re.S)
    return " ".join(m.group(0).split())


def test_2524_headers_and_blind_bullet_state_no_stale_input_claims():
    bvp = SCRIPTS / "build-verify-prompt.sh"
    dtc = SCRIPTS / "detect-test-command.sh"
    bullet = blind_bullet()
    stale = []
    if re.search(r"only inputs are", " ".join(header(bvp).split())):
        stale.append("skills/tdd/scripts/build-verify-prompt.sh: header claims its only inputs are the spec and the test")
    dtc_purpose = dtc.read_text().splitlines()[1]
    if "the full suite of a repo" in dtc_purpose or "tier asked for" not in dtc_purpose:
        stale.append("skills/tdd/scripts/detect-test-command.sh: header does not say it prints the command of the tier asked for")
    if "takes only a phase" in bullet or "every input" not in bullet:
        stale.append("CLAUDE.md: blind bullet lists a closed set of inputs instead of the property of every input")
    for word in ("blind", "build-verify-prompt.sh", "rationale"):
        if word not in bullet:
            stale.append("CLAUDE.md: blind bullet lost the word " + word)
    assert stale == []
