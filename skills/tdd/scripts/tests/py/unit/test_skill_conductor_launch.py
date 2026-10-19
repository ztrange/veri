"""What README.md tells an operator about launching the conductor, read as text,
one paragraph or bullet at a time."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[6] / "README.md"

NESTED = r"claudecode|nested|inside (another|a) claude|interactive session|own session|already in"
INTERACTIVE = r"interactive|chat session|inside a session|a session you|typed into a session"
PRINT = r"print mode|print-mode|claude -p"
CANNOT_INTERVENE = (r"(cannot|can not|no way to|nobody can|no one can|impossible to|never|not) "
                    r"(be )?(asked|answered|questioned|interrupted|redirected|steered|reached|stopped)")
PREFER_PRINT = (r"(prefer|recommend|should|always|the (supported|right|proper|only) way)"
                r"[^.]*(print mode|print-mode|claude -p|run-conductor|plain shell|"
                r"outside (any|the|that|a) (claude code )?session)")


def records():
    out, rec = [], ""
    for line in SKILL.read_text().splitlines():
        if re.match(r"[-*] ", line):
            if rec:
                out.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                out.append(rec)
            rec = ""
        elif not rec:
            rec = line
        else:
            rec = rec + " " + line
    if rec:
        out.append(rec)
    return [r.replace("*", "").replace("`", "").lower() for r in out]


def matches_all(record, patterns):
    return all(re.search(p, record) for p in patterns)


def says(*patterns):
    return any(matches_all(r, patterns) for r in records())


def still_says(*patterns):
    return [r[:120] for r in records() if matches_all(r, patterns)]


def test_skill_md_says_how_to_launch_the_conductor_when_the_operator_is_already_inside_a_claude_code_session_and_that_veri_never_unsets_claudecode_itself():
    assert says(NESTED, r"claude -p", r"/tdd",
                r"plain shell|ordinary shell|normal shell|separate shell|own shell|a terminal|outside (the|that|this) session|outside claude code")
    assert says(r"claudecode", r"unset", r"never|does not|will not|refus|not veri|leaves it",
                r"crash|risk|danger", r"operator|user|you|human|their|yours")


def test_skill_md_says_which_launch_modes_exist_and_that_a_print_mode_conductor_cannot_be_asked_a_question_mid_run():
    assert says(INTERACTIVE, PRINT, r"run-conductor")
    assert says(f"{PRINT}|run-conductor|unattended", CANNOT_INTERVENE,
                r"mid-run|mid run|while it is running|once it is running|once it has started|once running|during the run|after it start|under way|underway|in flight")


def test_skill_md_no_longer_says_pulling_the_primary_clone_changes_the_scripts_under_a_live_run():
    assert still_says(r"pull", r"primary", r"(chang|swap|replac|mov)[a-z]* (the )?script",
                      r"live|running|in flight|under (it|a run|the run)") == []


def test_skill_md_presents_interactive_and_print_mode_as_a_trade_picked_per_run_steerable_at_25000_tokens_a_request_more_or_that_much_cheaper_with_every_question_a_bail():
    assert says(INTERACTIVE, f"{PRINT}|run-conductor", r"steer|intervene|redirect", r"25,?000|25k",
                r"token", r"request", r"cheaper|less|saves", r"bail", r"trade|per run|each run|every run")


def test_skill_md_no_longer_says_an_interactive_session_is_not_where_a_run_belongs():
    assert still_says(INTERACTIVE,
                      r"not where (a|the|your) (run|conductor) belongs|(run|conductor)s? (does|do) not belong|(is|are) not (a|the) place (for|to) (a )?(run|conductor)") == []


def test_skill_md_gives_the_25000_token_per_request_cost_as_the_reason_for_print_mode_never_the_claudecode_nested_session_refusal():
    assert says(f"{PRINT}|run-conductor", r"25,?000|25k", r"token", r"request", r"cheaper|less|saves")
    assert still_says(r"claudecode|nested|guard", PREFER_PRINT) == []


def test_skill_md_still_says_if_a_nested_launch_guard_fires_to_run_the_conductor_from_a_plain_shell_outside_the_session_with_claude_p_tdd_n():
    assert says(r"guard", r"(when|if|once) (one|it|the guard|a guard)[^.]*(fires|fired|does|trips|refuses)",
                r"plain shell|ordinary shell|normal shell|separate shell|outside (any|the|that|this) (claude code )?session",
                r"claude -p", r"/tdd")
