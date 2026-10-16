"""How skills/tdd/SKILL.md launches, waits for and verifies a leaf, read as text."""
import pathlib
import re

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[2].parent / "SKILL.md"

DETACHER = "detach-leaf.sh"
LAUNCHER = "supervise.sh"
VERDICT_LAUNCHER = "run-verdict.sh"
LAUNCH_RE = r"supervise\.sh|verify\.sh|run-verdict\.sh"
SECTION = "## Launching a leaf — detach, then wait in the foreground"

SPEC_RE = r"(\.tdd/issue-<n>-spec\.md|<spec-file>)"
DOUBLE_QUOTED_STEP = '"<STEP>"'
LEDGER_READ_RE = (r"cat \.tdd/issue-<n>\.md \| \$S/(next-(unchecked|pending-refactor)\.sh"
                  r"|ledger-steps\.sh (current|current-or-last-done))")
LAST_DONE_RE = r"\{ cat \.tdd/issue-<n>\.md \| \$S/ledger-steps\.sh last-done; \}"
LEDGER_STEP_RE = (r'"\$\(' + LEDGER_READ_RE + r"( \|\| (" + LEDGER_READ_RE + "|" + LAST_DONE_RE + r"))?\)" + '"')
BLIND_RE = (
    "^(--step (" + DOUBLE_QUOTED_STEP + "|" + LEDGER_STEP_RE + r")( --fast-cmd '<fast-cmd>')? "
    r"(red|green|refactor|pin|<phase>) " + SPEC_RE + r" <test-path> (<target-test-id>|<green-sha>|<base-sha>|\[target\])"
    "|--step (" + DOUBLE_QUOTED_STEP + "|" + LEDGER_STEP_RE + ") rebase " + SPEC_RE + " <onto-sha> <pre-rebase-sha>"
    "|--step (" + DOUBLE_QUOTED_STEP + "|" + LEDGER_STEP_RE + ") transform " + SPEC_RE
    + r" \.tdd/issue-<n>-predicate <base-sha>"
    "|plan " + SPEC_RE + r" \.tdd/issue-<n>\.md)$"
)


def fenced_lines(pattern):
    out, fence = [], False
    for number, line in enumerate(SKILL.read_text().splitlines(), 1):
        if re.match(r"\s*```", line):
            fence = not fence
        elif fence and re.search(pattern, line):
            out.append((number, line))
    return out


def launch_lines():
    return fenced_lines(LAUNCH_RE)


def section_prose():
    prose, fence = [], False
    for line in skill_sections.section(SKILL, SECTION).splitlines():
        if re.match(r"\s*```", line):
            fence = not fence
        elif not fence:
            prose.append(line)
    return "\n".join(prose).lower()


def inventory_entry(script):
    want = "- `$S/" + script
    entry, inside = [], False
    for line in SKILL.read_text().splitlines():
        if line.startswith(want):
            inside = True
            entry.append(line)
        elif inside and (line.startswith("- ") or line.startswith("#") or not line.strip()):
            inside = False
        elif inside:
            entry.append(line)
    return " ".join(entry).lower()


def blind_args(text):
    tail = text.split(VERDICT_LAUNCHER + " ", 1)[1]
    return tail.split(" > .tdd/verify-", 1)[0]


def test_skill_md_launches_every_developer_and_verifier_leaf_through_detach_leaf_sh_and_no_launch_line_uses_nohup():
    launches = launch_lines()
    assert launches, "no leaf launch line inside a fenced block"
    problems = [f"{number}: {text}" for number, text in launches
                if DETACHER not in text or "nohup" in text]
    assert problems == []


def test_skill_md_s_launching_a_leaf_says_why_nohup_alone_is_not_enough():
    prose = section_prose()
    assert "nohup" in prose
    assert re.search(r"(sighup|hang-?up)", prose)
    assert "process group" in prose


def test_skill_md_clears_tdd_name_pid_together_with_tdd_name_exit_on_every_launch():
    clears = fenced_lines(r"rm -f .*\.tdd/[^ ]*\.exit")
    assert clears, "no line clearing a completion file inside a fenced block"
    problems = []
    for number, text in clears:
        exitfile = re.search(r"\.tdd/[^ ]*\.exit", text).group(0)
        pidfile = exitfile[:-len(".exit")] + ".pid"
        if pidfile not in text:
            problems.append(f"{number}: clears {exitfile} but not {pidfile}: {text}")
    assert problems == []


def test_skill_md_s_wait_leaf_sh_entry_says_a_2_also_means_the_supervisor_died_without_recording_a_status_and_takes_the_killed_stuck_branch():
    entry = inventory_entry("wait-leaf.sh")
    assert entry, "no script inventory entry for wait-leaf.sh"
    assert re.search(r"supervisor[^.]*(died|dead|gone)[^.]*(without|never|no)[^.]*(record|status|completion)", entry)
    assert "killed-stuck" in entry


def test_skill_md_passes_verify_sh_only_the_blind_parameters_on_every_supervised_verifier_launch():
    supervised = [(number, text) for number, text in launch_lines()
                  if VERDICT_LAUNCHER in text and LAUNCHER in text and re.search(SPEC_RE, text)]
    assert supervised, "no supervised verifier launch line naming a spec file inside a fenced block"
    problems = [f"{number}: passes verify.sh more than the blind parameters: {blind_args(text)}"
                for number, text in supervised if not re.search(BLIND_RE, blind_args(text))]
    assert problems == []
