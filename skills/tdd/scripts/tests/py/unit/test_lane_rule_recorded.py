"""In-process case for CLAUDE.md's record of the two test lanes."""
import re
from pathlib import Path

CLAUDE_MD = Path(__file__).resolve().parents[6] / "CLAUDE.md"
TRAP_HEADING = "## The one trap"
DOCS_LANE = "docs[ -]lane|documentation lane|docs issue|docs merge"
LOWER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def section_text(heading):
    inside, body = False, []
    for line in CLAUDE_MD.read_text().splitlines():
        if not inside:
            inside = line == heading
        elif line.startswith("## "):
            break
        else:
            body.append(line)
    return " ".join(body).replace("*", "").replace("`", "").translate(LOWER) + " " if inside else ""


def says(problems, heading, text, fact, *regexes):
    for regex in regexes:
        if not re.search(regex, text):
            problems.append(f"CLAUDE.md's '{heading}' section does not say {fact}")
            return


def has_section(problems, heading, text):
    if text.replace(" ", "") != "":
        return True
    problems.append(f"CLAUDE.md has no '{heading}' section to read, so nothing states the lane rule where the agent reading that section would find it")
    return False


def test_claude_md_states_the_lane_rule_in_both_sections_an_agent_reads_the_page_is_the_other_lanes_work_and_a_development_run_never_runs_a_docs_target():
    problems = []
    trap = section_text(TRAP_HEADING)
    if has_section(problems, TRAP_HEADING, trap):
        says(problems, TRAP_HEADING, trap,
             "that the page and its inputs are the other lane's work, and that a development run never runs the target that rebuilds them",
             DOCS_LANE, "develop|leaf|veri run|tdd run", "never|refus|exit 2")
    assert problems == []
