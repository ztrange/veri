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
    return fenced_in(SKILL.read_text(), pattern)


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


STEP_PH = "<STEP>"
SINGLE_QUOTED_STEP = "'<STEP>'"
FRAGMENT_PH = r"<[^<>]*substring[^<>]*>"
SINGLE_QUOTED_FRAGMENT = "'" + FRAGMENT_PH + "'"
DOUBLE_QUOTED_FRAGMENT = '"' + FRAGMENT_PH + '"'


def fenced_in(text, pattern):
    out, fence = [], False
    for number, line in enumerate(text.splitlines(), 1):
        if re.match(r"\s*```", line):
            fence = not fence
        elif fence and re.search(pattern, line):
            out.append((number, line))
    return out


def prose_paragraphs(text):
    out, para, start, fence = [], [], 0, False
    for number, line in enumerate(text.splitlines(), 1):
        if re.match(r"\s*```", line):
            fence = not fence
            if para:
                out.append((start, " ".join(para)))
                para = []
        elif fence:
            continue
        elif not line.strip():
            if para:
                out.append((start, " ".join(para)))
                para = []
        else:
            if not para:
                start = number
            para.append(line)
    if para:
        out.append((start, " ".join(para)))
    return out


def step_title_rules(text):
    return [(n, p) for n, p in prose_paragraphs(text)
            if re.search("quot", p, re.I) and ("step title" in p or STEP_PH in p)]


def quoted_faults(lines, noun, placeholder, single, double, exempt=()):
    problems = []
    for number, text in lines:
        if number in exempt:
            continue
        if re.search(single, text):
            problems.append(f"{number}: single-quotes {noun}: {text}")
        elif re.search(placeholder, re.sub(double, "", text)):
            problems.append(f"{number}: carries {noun} outside double quotes: {text}")
    return problems


def title_guard(text, exempt=()):
    return quoted_faults(fenced_in(text, STEP_PH), "the step title", STEP_PH,
                         re.escape(SINGLE_QUOTED_STEP), re.escape(DOUBLE_QUOTED_STEP), exempt)


def test_skill_md_invokes_run_verdict_sh_on_every_verifier_launch_with_no_inlined_bash_c_command_string():
    verdict_launches = [(n, t) for n, t in launch_lines() if f"{LAUNCHER} verdict-" in t]
    assert verdict_launches, "no launch line naming supervise.sh and a verdict-<phase> leaf inside a fenced block"
    problems = []
    for number, text in verdict_launches:
        if VERDICT_LAUNCHER not in text:
            problems.append(f"{number}: does not invoke {VERDICT_LAUNCHER}: {text}")
        if "bash -c" in text:
            problems.append(f"{number}: still inlines the verifier call in a bash -c command string: {text}")
    assert problems == []


def test_skill_md_double_quotes_every_documented_command_line_that_passes_a_fragment_of_the_step_s_title():
    fragments = [(n, line) for n, line in enumerate(SKILL.read_text().splitlines(), 1)
                 if re.search(FRAGMENT_PH, line)
                 and re.search(r"\$S/|" + SINGLE_QUOTED_FRAGMENT + "|" + DOUBLE_QUOTED_FRAGMENT, line)]
    assert fragments, "no command line passing a fragment of the step's title"
    problems = quoted_faults(fragments, "a fragment of the step title", FRAGMENT_PH,
                             SINGLE_QUOTED_FRAGMENT, DOUBLE_QUOTED_FRAGMENT)
    assert problems == []


def test_skill_md_s_step_title_rule_says_the_title_reaches_a_command_line_as_data_not_hand_typed_in_double_quotes_and_names_what_the_launch_lines_read_it_through():
    text = SKILL.read_text()
    rules = step_title_rules(text)
    assert len(rules) == 1, "no single paragraph stating the step-title rule"
    readers = sorted({m for _, line in fenced_in(text, r'VERI_STEP="\$\(')
                      for call in re.findall(r'VERI_STEP="\$\([^)]*\)', line)
                      for m in re.findall(r"\$S/([A-Za-z0-9_.-]+)", call)})
    assert readers, "no launch line reading VERI_STEP through a script inside a fenced block"
    number, rule = rules[0]
    faults = []
    if not re.search(r"(^|[^a-z])data([^a-z]|$)", rule.lower()):
        faults.append("does not say the title reaches a command line as data")
    faults += [f"does not name {r}, which a launch line reads the title through" for r in readers if r not in rule]
    assert faults == [], f"{number}: states the step-title rule but {', and '.join(faults)}"


def step_title_rule_problems(text):
    rules = step_title_rules(text)
    if not rules:
        return ["states no rule for how a step title reaches a command line"]
    if len(rules) > 1:
        return [f"states the step-title rule in {len(rules)} places, at lines {','.join(str(n) for n, _ in rules)}"]
    number, rule = rules[0]
    faults = []
    if DOUBLE_QUOTED_STEP not in rule and "double quote" not in rule.lower():
        faults.append("does not say the title is carried in double quotes")
    if "apostrophe" not in rule.lower():
        faults.append("does not say why: a title carrying an apostrophe closes a single-quoted one early")
    problems = [f"{number}: states the step-title rule but {', and '.join(faults)}"] if faults else []
    if not fenced_in(text, STEP_PH):
        problems.append("no line carrying <STEP> inside a fenced block")
    return problems + title_guard(text)


def test_skill_md_states_the_step_title_rule_in_one_place_and_every_fenced_command_carrying_the_title_follows_it():
    assert step_title_rule_problems(SKILL.read_text()) == []


def test_the_431_guard_still_refuses_a_single_quoted_step_title_and_its_exemption_table_still_holds_over_the_rewritten_skill_md():
    text = SKILL.read_text()
    title_linenos = [n for n, _ in fenced_in(text, STEP_PH)]
    assert title_linenos, "no fenced line carrying <STEP>"
    planted_line = title_linenos[0]
    lines = text.splitlines()
    lines[planted_line - 1] = lines[planted_line - 1].replace(DOUBLE_QUOTED_STEP, SINGLE_QUOTED_STEP)
    planted = "\n".join(lines) + "\n"
    refused = "\n".join(title_guard(planted))
    assert f"{planted_line}: single-quotes the step title" in refused, \
        f"the guard did not refuse {SINGLE_QUOTED_STEP} planted at line {planted_line} — it reported: {refused or 'nothing'}"
    answered = title_guard(planted, exempt={planted_line})
    assert not any(p.startswith(f"{planted_line}:") for p in answered)


def test_skill_md_s_revise_launch_hands_build_develop_prompt_sh_revise_the_run_s_fast_command_fast_cmd():
    revise_builds = fenced_lines(r"build-develop-prompt\.sh revise <phase>")
    assert revise_builds, "no line building the revise prompt with build-develop-prompt.sh revise inside a fenced block"
    problems = [f"{n}: builds the revise prompt without the run's fast command '<fast-cmd>': {t}"
                for n, t in revise_builds if "'<fast-cmd>'" not in t]
    assert problems == []


VERIFIER = "verify.sh"


def verifier_launches_without_supervisor(text):
    launch = r"supervise\.sh|verify\.sh|run-verdict\.sh"
    verifier = r"verify\.sh|run-verdict\.sh"
    launches = [(n, t) for n, t in fenced_in(text, launch) if re.search(verifier, t)]
    assert launches, f"no launch line naming {VERIFIER} or {VERDICT_LAUNCHER} inside a fenced block"
    return [f"{n}: reaches {VERIFIER} without {LAUNCHER}: {t}" for n, t in launches if LAUNCHER not in t]


def test_skill_md_launches_every_verifier_through_supervise_sh_the_way_it_launches_a_developer_leaf():
    assert verifier_launches_without_supervisor(SKILL.read_text()) == []


SUPERVISED_VERDICT_FRAGMENT = "$S/supervise.sh verdict-red "
STEP_ANCHOR = "$S/refactor-owed.sh append "


def plant_in_line(text, line_number, old, new):
    lines = text.splitlines()
    assert old in lines[line_number - 1], f"line {line_number} does not carry {old!r}"
    lines[line_number - 1] = lines[line_number - 1].replace(old, new, 1)
    return "\n".join(lines) + "\n"


def carrier_of(text, fragment):
    carriers = [n for n, line in enumerate(text.splitlines(), 1) if fragment in line]
    assert len(carriers) == 1, f"{fragment!r} is carried by lines {carriers}, want exactly 1"
    return carriers[0]


def step_line_planted_single_quoted():
    text = SKILL.read_text()
    step_line = carrier_of(text, STEP_ANCHOR)
    return step_line, plant_in_line(text, step_line, DOUBLE_QUOTED_STEP, SINGLE_QUOTED_STEP)


def test_skill_leaf_launch_sh_fails_over_a_skill_md_whose_verifier_launch_has_lost_supervise_sh_naming_that_line_and_nothing_else_and_passes_over_the_document_as_committed():
    text = SKILL.read_text()
    assert verifier_launches_without_supervisor(text) == []
    planted_line = carrier_of(text, SUPERVISED_VERDICT_FRAGMENT)
    planted = plant_in_line(text, planted_line, SUPERVISED_VERDICT_FRAGMENT, "")
    refused = verifier_launches_without_supervisor(planted)
    assert len(refused) == 1, f"want only line {planted_line} named, got: {refused}"
    assert refused[0].startswith(f"{planted_line}: reaches {VERIFIER} without {LAUNCHER}")


def test_skill_leaf_launch_sh_fails_over_a_skill_md_whose_launch_line_carries_single_quoted_step_unless_its_exemption_table_names_it_with_a_reason():
    step_line, planted = step_line_planted_single_quoted()
    refused = title_guard(planted)
    assert len(refused) == 1 and refused[0].startswith(f"{step_line}: single-quotes the step title"), refused
    assert title_guard(planted, exempt={step_line}) == []


def test_skill_leaf_launch_sh_s_431_guard_pin_still_answers_over_a_skill_md_whose_one_double_quoted_step_line_is_planted_single_quoted_and_exempted_with_a_reason():
    step_line, planted = step_line_planted_single_quoted()
    assert any(p.startswith(f"{step_line}: single-quotes the step title") for p in title_guard(planted))
    assert not any(p.startswith(f"{step_line}:") for p in title_guard(planted, exempt={step_line}))
