"""How skills/tdd/SKILL.md launches, waits for and verifies a leaf, read as text.

Every check below takes the document's path and the exemption table and answers the problems it
finds, each addressed `<line>: ...` where it names a line. `leaf_guard` runs them all, the way
the bash suite these cases came from ran every case over one document: the verifier-launch guard
cases plant a line into a copy of SKILL.md and ask what the whole guard says about it.
"""
import pathlib
import re

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DETACHER = "detach-leaf.sh"
LAUNCHER = "supervise.sh"
VERIFIER = "verify.sh"
VERDICT_LAUNCHER = "run-verdict.sh"
LAUNCH_RE = r"supervise\.sh|verify\.sh|run-verdict\.sh"
SECTION = "## Launching a leaf — detach, then wait in the foreground"

SPEC_RE = r"(\.tdd/issue-<n>-spec\.md|<spec-file>)"
STEP_PH = "<STEP>"
DOUBLE_QUOTED_STEP = '"<STEP>"'
SINGLE_QUOTED_STEP = "'<STEP>'"
FRAGMENT_PH = r"<[^<>]*substring[^<>]*>"
SINGLE_QUOTED_FRAGMENT = "'" + FRAGMENT_PH + "'"
DOUBLE_QUOTED_FRAGMENT = '"' + FRAGMENT_PH + '"'
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

# SKILL.md line -> the reason that line may keep a quoting the step-title checks refuse.
# An entry whose reason is empty says nothing, so it excuses nothing.
EXEMPT = {}


def table(exempt):
    return EXEMPT if exempt is None else exempt


def exempted(number, exempt):
    return bool(exempt.get(number, ""))


def fenced_in(text, pattern):
    out, fence = [], False
    for number, line in enumerate(text.splitlines(), 1):
        if re.match(r"\s*```", line):
            fence = not fence
        elif fence and re.search(pattern, line):
            out.append((number, line))
    return out


def launch_lines(text):
    return fenced_in(text, LAUNCH_RE)


def section_prose(path):
    prose, fence = [], False
    for line in skill_sections.section(path, SECTION).splitlines():
        if re.match(r"\s*```", line):
            fence = not fence
        elif not fence:
            prose.append(line)
    return "\n".join(prose).lower()


def inventory_entry(text, script):
    want = "- `$S/" + script
    entry, inside = [], False
    for line in text.splitlines():
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


def quoted_faults(lines, noun, placeholder, single, double, exempt):
    problems = []
    for number, text in lines:
        if exempted(number, exempt):
            continue
        if re.search(single, text):
            problems.append(f"{number}: single-quotes {noun}: {text}")
        elif re.search(placeholder, re.sub(double, "", text)):
            problems.append(f"{number}: carries {noun} outside double quotes: {text}")
    return problems


def title_guard(text, exempt=None):
    return quoted_faults(fenced_in(text, STEP_PH), "the step title", STEP_PH,
                         re.escape(SINGLE_QUOTED_STEP), re.escape(DOUBLE_QUOTED_STEP), table(exempt))


def detach_problems(path, exempt=None):
    launches = launch_lines(path.read_text())
    if not launches:
        return ["no leaf launch line inside a fenced block"]
    return [f"{number}: {text}" for number, text in launches if DETACHER not in text or "nohup" in text]


def nohup_reason_problems(path, exempt=None):
    prose = section_prose(path)
    faults = []
    if "nohup" not in prose:
        faults.append("never names nohup")
    if not re.search(r"(sighup|hang-?up)", prose):
        faults.append("does not say nohup survives a hang-up")
    if "process group" not in prose:
        faults.append("does not say nohup leaves the leaf in the launching call's process group")
    return [f"*{SECTION}* {', and '.join(faults)}"] if faults else []


def clear_problems(path, exempt=None):
    clears = fenced_in(path.read_text(), r"rm -f .*\.tdd/[^ ]*\.exit")
    if not clears:
        return ["no line clearing a completion file inside a fenced block"]
    problems = []
    for number, text in clears:
        exitfile = re.search(r"\.tdd/[^ ]*\.exit", text).group(0)
        pidfile = exitfile[:-len(".exit")] + ".pid"
        if pidfile not in text:
            problems.append(f"{number}: clears {exitfile} but not {pidfile}: {text}")
    return problems


def wait_leaf_problems(path, exempt=None):
    entry = inventory_entry(SKILL.with_name("SCRIPTS.md").read_text(), "wait-leaf.sh")
    if not entry:
        return ["no script inventory entry for wait-leaf.sh"]
    faults = []
    if not re.search(r"supervisor[^.]*(died|dead|gone)[^.]*(without|never|no)[^.]*(record|status|completion)", entry):
        faults.append("does not say a 2 means the supervisor died without recording a status")
    if "killed-stuck" not in entry:
        faults.append("does not say that 2 takes the killed-stuck branch")
    return [f"wait-leaf.sh entry {', and '.join(faults)}"] if faults else []


def verifier_launches_without_supervisor(text):
    launches = [(n, t) for n, t in launch_lines(text) if re.search(r"verify\.sh|run-verdict\.sh", t)]
    if not launches:
        return [f"no launch line naming {VERIFIER} or {VERDICT_LAUNCHER} inside a fenced block"]
    return [f"{n}: reaches {VERIFIER} without {LAUNCHER}: {t}" for n, t in launches if LAUNCHER not in t]


def supervisor_problems(path, exempt=None):
    return verifier_launches_without_supervisor(path.read_text())


def blind_problems(path, exempt=None):
    supervised = [(number, text) for number, text in launch_lines(path.read_text())
                  if VERDICT_LAUNCHER in text and LAUNCHER in text and re.search(SPEC_RE, text)]
    if not supervised:
        return ["no supervised verifier launch line naming a spec file inside a fenced block"]
    return [f"{number}: passes verify.sh more than the blind parameters: {blind_args(text)}"
            for number, text in supervised if not re.search(BLIND_RE, blind_args(text))]


def verdict_launcher_problems(path, exempt=None):
    verdict_launches = [(n, t) for n, t in launch_lines(path.read_text()) if f"{LAUNCHER} verdict-" in t]
    if not verdict_launches:
        return ["no launch line naming supervise.sh and a verdict-<phase> leaf inside a fenced block"]
    problems = []
    for number, text in verdict_launches:
        if VERDICT_LAUNCHER not in text:
            problems.append(f"{number}: does not invoke {VERDICT_LAUNCHER}: {text}")
        if "bash -c" in text:
            problems.append(f"{number}: still inlines the verifier call in a bash -c command string: {text}")
    return problems


def step_title_rule_problems(text, exempt=None):
    rules = step_title_rules(text)
    problems = []
    if not rules:
        problems.append("states no rule for how a step title reaches a command line")
    elif len(rules) > 1:
        problems.append(f"states the step-title rule in {len(rules)} places, at lines {','.join(str(n) for n, _ in rules)}")
    else:
        number, rule = rules[0]
        faults = []
        if DOUBLE_QUOTED_STEP not in rule and "double quote" not in rule.lower():
            faults.append("does not say the title is carried in double quotes")
        if "apostrophe" not in rule.lower():
            faults.append("does not say why: a title carrying an apostrophe closes a single-quoted one early")
        if faults:
            problems.append(f"{number}: states the step-title rule but {', and '.join(faults)}")
    if not fenced_in(text, STEP_PH):
        problems.append("no line carrying <STEP> inside a fenced block")
    return problems + title_guard(text, exempt)


def step_title_problems(path, exempt=None):
    return step_title_rule_problems(path.read_text(), exempt)


def fragment_problems(path, exempt=None):
    lines = (path.read_text() + SKILL.with_name("SCRIPTS.md").read_text()).splitlines()
    fragments = [(n, line) for n, line in enumerate(lines, 1)
                 if re.search(FRAGMENT_PH, line)
                 and re.search(r"\$S/|" + SINGLE_QUOTED_FRAGMENT + "|" + DOUBLE_QUOTED_FRAGMENT, line)]
    if not fragments:
        return ["no command line passing a fragment of the step's title"]
    return quoted_faults(fragments, "a fragment of the step title", FRAGMENT_PH,
                         SINGLE_QUOTED_FRAGMENT, DOUBLE_QUOTED_FRAGMENT, table(exempt))


def rule_data_problems(path, exempt=None):
    text = path.read_text()
    rules = step_title_rules(text)
    if len(rules) != 1:
        return ["no single paragraph stating the step-title rule"]
    readers = sorted({m for _, line in fenced_in(text, r'VERI_STEP="\$\(')
                      for call in re.findall(r'VERI_STEP="\$\([^)]*\)', line)
                      for m in re.findall(r"\$S/([A-Za-z0-9_.-]+)", call)})
    if not readers:
        return ["no launch line reading VERI_STEP through a script inside a fenced block"]
    number, rule = rules[0]
    faults = []
    if not re.search(r"(^|[^a-z])data([^a-z]|$)", rule.lower()):
        faults.append("does not say the title reaches a command line as data")
    faults += [f"does not name {r}, which a launch line reads the title through" for r in readers if r not in rule]
    return [f"{number}: states the step-title rule but {', and '.join(faults)}"] if faults else []


def pin_431_problems(path, exempt=None):
    exempt = table(exempt)
    text = path.read_text()
    title_linenos = [n for n, _ in fenced_in(text, STEP_PH)]
    problems = []
    if not title_linenos:
        problems.append("no fenced line carrying <STEP>, where the #431 guard would meet a single-quoted title")
    else:
        planted_line = title_linenos[0]
        lines = text.splitlines()
        lines[planted_line - 1] = lines[planted_line - 1].replace(DOUBLE_QUOTED_STEP, SINGLE_QUOTED_STEP, 1)
        planted = "\n".join(lines) + "\n"
        refused = "\n".join(title_guard(planted, {k: v for k, v in exempt.items() if k != planted_line}))
        if f"{planted_line}: single-quotes the step title" not in refused:
            problems.append(f"the guard did not refuse {SINGLE_QUOTED_STEP} planted at line {planted_line}"
                            f" — it reported: {refused or 'nothing'}")
        answered = title_guard(planted, {**exempt, planted_line: "planted by the #431 pin"})
        if any(p.startswith(f"{planted_line}:") for p in answered):
            problems.append(f"an EXEMPT entry for line {planted_line} did not answer the report: {answered}")
    problems += [f"EXEMPT[{key}] names a line that no fenced command carrying {STEP_PH} is on in the rewritten document"
                 for key in exempt if key not in title_linenos]
    return problems


def revise_fast_cmd_problems(path, exempt=None):
    revise_builds = fenced_in(path.read_text(), r"build-develop-prompt\.sh revise <phase>")
    if not revise_builds:
        return ["no line building the revise prompt with build-develop-prompt.sh revise inside a fenced block"]
    return [f"{n}: builds the revise prompt without the run's fast command '<fast-cmd>': {t}"
            for n, t in revise_builds if "'<fast-cmd>'" not in t]


CHECKS = (detach_problems, nohup_reason_problems, clear_problems, wait_leaf_problems, supervisor_problems,
          blind_problems, verdict_launcher_problems, step_title_problems, fragment_problems,
          rule_data_problems, pin_431_problems, revise_fast_cmd_problems)


def leaf_guard(path, exempt=None):
    unrun = sorted(name for name, f in globals().items()
                   if name.endswith("_problems") and callable(f) and f not in CHECKS and name != "step_title_rule_problems")
    assert unrun == [], f"leaf_guard does not run {unrun}, so its output is not the whole guard's"
    return [problem for check in CHECKS for problem in check(path, exempt)]


def test_skill_md_launches_every_developer_and_verifier_leaf_through_detach_leaf_sh_and_no_launch_line_uses_nohup():
    assert detach_problems(SKILL) == []


def test_skill_md_s_launching_a_leaf_says_why_nohup_alone_is_not_enough():
    assert nohup_reason_problems(SKILL) == []


def test_skill_md_clears_tdd_name_pid_together_with_tdd_name_exit_on_every_launch():
    assert clear_problems(SKILL) == []


def test_skill_md_s_wait_leaf_sh_entry_says_a_2_also_means_the_supervisor_died_without_recording_a_status_and_takes_the_killed_stuck_branch():
    assert wait_leaf_problems(SKILL) == []


def test_skill_md_passes_verify_sh_only_the_blind_parameters_on_every_supervised_verifier_launch():
    assert blind_problems(SKILL) == []


def test_skill_md_invokes_run_verdict_sh_on_every_verifier_launch_with_no_inlined_bash_c_command_string():
    assert verdict_launcher_problems(SKILL) == []


def test_skill_md_double_quotes_every_documented_command_line_that_passes_a_fragment_of_the_step_s_title():
    assert fragment_problems(SKILL) == []


def test_skill_md_s_step_title_rule_says_the_title_reaches_a_command_line_as_data_not_hand_typed_in_double_quotes_and_names_what_the_launch_lines_read_it_through():
    assert rule_data_problems(SKILL) == []


def test_skill_md_states_the_step_title_rule_in_one_place_and_every_fenced_command_carrying_the_title_follows_it():
    assert step_title_rule_problems(SKILL.read_text()) == []


def test_the_431_guard_still_refuses_a_single_quoted_step_title_and_its_exemption_table_still_holds_over_the_rewritten_skill_md():
    assert pin_431_problems(SKILL) == []


def test_skill_md_s_revise_launch_hands_build_develop_prompt_sh_revise_the_run_s_fast_command_fast_cmd():
    assert revise_fast_cmd_problems(SKILL) == []


def test_skill_md_launches_every_verifier_through_supervise_sh_the_way_it_launches_a_developer_leaf():
    assert supervisor_problems(SKILL) == []


SUPERVISED_VERDICT_FRAGMENT = "$S/supervise.sh verdict-red "
STEP_ANCHOR = "$S/refactor-owed.sh append "
EXEMPT_REASON = "planted by test_skill_leaf_launch.py to ask what an exemption with a reason does"


def plant_in_line(text, line_number, old, new):
    lines = text.splitlines()
    assert old in lines[line_number - 1], f"line {line_number} does not carry {old!r}"
    lines[line_number - 1] = lines[line_number - 1].replace(old, new, 1)
    return "\n".join(lines) + "\n"


def carrier_of(text, fragment):
    carriers = [n for n, line in enumerate(text.splitlines(), 1) if fragment in line]
    assert len(carriers) == 1, f"{fragment!r} is carried by lines {carriers}, want exactly 1"
    return carriers[0]


def planted_skill(tmp_path, text):
    path = tmp_path / "SKILL.md"
    path.write_text(text)
    return path


def step_line_planted_single_quoted(tmp_path):
    text = SKILL.read_text()
    step_line = carrier_of(text, STEP_ANCHOR)
    return step_line, planted_skill(tmp_path, plant_in_line(text, step_line, DOUBLE_QUOTED_STEP, SINGLE_QUOTED_STEP))


def assert_names_only(problems, line):
    assert problems, f"the guard passed over a document planted at line {line}"
    others = [p for p in problems if not p.startswith(f"{line}:")]
    assert others == [], f"want only line {line} named, the guard also said: {others}"


def test_skill_leaf_launch_sh_fails_over_a_skill_md_whose_verifier_launch_has_lost_supervise_sh_naming_that_line_and_nothing_else_and_passes_over_the_document_as_committed(tmp_path):
    assert leaf_guard(SKILL) == []
    text = SKILL.read_text()
    planted_line = carrier_of(text, SUPERVISED_VERDICT_FRAGMENT)
    planted = planted_skill(tmp_path, plant_in_line(text, planted_line, SUPERVISED_VERDICT_FRAGMENT, ""))
    refused = leaf_guard(planted)
    assert_names_only(refused, planted_line)
    assert any(p.startswith(f"{planted_line}: reaches {VERIFIER} without {LAUNCHER}") for p in refused), refused


def test_skill_leaf_launch_sh_fails_over_a_skill_md_whose_launch_line_carries_single_quoted_step_unless_its_exemption_table_names_it_with_a_reason(tmp_path):
    step_line, planted = step_line_planted_single_quoted(tmp_path)
    refused = leaf_guard(planted)
    assert_names_only(refused, step_line)
    assert any(p.startswith(f"{step_line}: single-quotes the step title") for p in refused), refused
    assert leaf_guard(planted, {step_line: EXEMPT_REASON}) == []
    reasonless = leaf_guard(planted, {step_line: ""})
    assert_names_only(reasonless, step_line)
    assert any(p.startswith(f"{step_line}: single-quotes the step title") for p in reasonless), \
        f"line {step_line} is named in the table with no reason — an entry that says nothing excuses nothing: {reasonless}"


def test_skill_leaf_launch_sh_s_431_guard_pin_still_answers_over_a_skill_md_whose_one_double_quoted_step_line_is_planted_single_quoted_and_exempted_with_a_reason(tmp_path):
    step_line, planted = step_line_planted_single_quoted(tmp_path)
    assert pin_431_problems(planted, {step_line: EXEMPT_REASON}) == []
