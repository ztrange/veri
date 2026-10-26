"""In-process cases for the two root documents' record of the per-role model tunables."""
import re

from skill_sections import LOWER, ROOT, lines_of, plain

CLAUDE_MD = "CLAUDE.md"
SUPERVISE_SH = "skills/tdd/scripts/supervise.sh"

MODEL_ANY = r"veri_model([^_a-z]|$)"
MODEL_DEV = "veri_model_developer"
MODEL_VER = "veri_model_verifier"
MODEL_REV = "veri_model_revise"


def records(path):
    out, rec = [], ""
    for line in lines_of(path):
        if re.match(r"[-*] ", line):
            if rec != "":
                out.append(rec)
            rec = line
        elif re.match(r"\s*$", line):
            if rec != "":
                out.append(rec)
            rec = ""
        elif rec == "":
            rec = line
        else:
            rec = rec + " " + line
    if rec != "":
        out.append(rec)
    return [plain(r) for r in out]


def says(problems, passage_from, passage_lines, fact, *regexes):
    for line in passage_lines:
        if all(re.search(r, line) for r in regexes):
            return
    problems.append(f"{passage_from} does not say {fact}")


def need_claude_md_records(problems, claude_path):
    recs = records(claude_path)
    if "".join(recs).replace(" ", "") != "":
        return CLAUDE_MD, recs
    problems.append(f"{CLAUDE_MD} could not be read, so nothing could be asked of what it records")
    return None


def names_all_four(problems, passage_from, lines, what):
    says(problems, passage_from, lines,
         f"{what} — it names no single passage carrying VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_REVISE and VERI_MODEL_VERIFIER",
         MODEL_ANY, MODEL_DEV, MODEL_REV, MODEL_VER)


def probe_claude_md_names_them_and_why(problems, claude_path):
    found = need_claude_md_records(problems, claude_path)
    if not found:
        return
    names_all_four(problems, *found, "names the four model tunables")
    says(problems, *found,
         "why the developer's and the verifier's models are separate knobs — the two roles named, that the knobs are not one, and how each one's regression shows up: a changed verdict distribution against more revise cycles",
         "developer", "verifier", "separate|two knobs|one knob|independent|its own|their own|never merged", "verdict", "revise")


def test_1485_the_knob_probes_name_the_document_in_a_problem_when_skill_mds_supervise_sh_bullet_or_claude_mds_model_knob_invariant_stops_naming_veri_model_revise(tmp_path):
    claude = tmp_path / "CLAUDE.md"
    claude.write_text((ROOT / CLAUDE_MD).read_text().replace("VERI_MODEL_REVISE", "VERI_MODEL_GONE"))
    problems = []
    probe_claude_md_names_them_and_why(problems, claude)
    assert any(p.startswith(CLAUDE_MD) and "VERI_MODEL_REVISE" in p for p in problems)
    assert len(problems) == 1


def test_1485_skill_mds_supervise_sh_bullet_and_claude_mds_model_knob_invariant_state_the_shipped_defaults_sonnet_and_opus_and_no_longer_say_a_default_run_carries_no_model():
    problems = []
    found = need_claude_md_records(problems, ROOT / CLAUDE_MD)
    if found:
        passage_from, lines = found
        says(problems, passage_from, lines, "the shipped defaults, sonnet and opus, beside VERI_MODEL_REVISE",
             MODEL_REV, "sonnet", "opus")
        if any(re.search(r"no --model", line) for line in lines):
            problems.append(f"{passage_from} still says a default run carries no --model")
    assert problems == []


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
