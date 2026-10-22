"""Cases for the tests-frozen record and check in skills/tdd/SKILL.md, read as text.

Contract under test:
  *Revising on a REJECT* (REVISE.md) runs `tests-frozen.sh check` between the revise-green wait
  and its re-verify; on check exit 1 it rejects the attempt, on exit 0 it launches the verifier
  as before, and on exit 2 it bails as a system failure, never a REJECT (that sentence pinned
  verbatim). It runs `tests-frozen.sh record` once a revised red's re-verify passes. Every
  record and check SKILL.md runs outside Green's own check names the step's record by
  `tests-frozen.sh path` over the step text, and no `tests-frozen-<step>` key survives. A
  ⟦replaces-case⟧ step records at its verify-pin PASS (PIN.md, pinned verbatim), before the
  deletion green. REVISE.md routes a revise-green `WRONG_TEST:` report through
  `wrong-test-route.sh` and a `MISSING_TEST:` answer to red-missing.

Every case's subject is source text: it reads SKILL.md, REVISE.md and PIN.md and starts no process.
"""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
REVISE_MD = SKILL.parent / "REVISE.md"
PIN_MD = SKILL.parent / "PIN.md"

GREEN = "#### Green"
REVISE = "## Revising on a REJECT"
PIN = "## Already satisfied — the pin"

RECORD_ARG = '--step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"'
EXIT2_SENTENCE = ('On tests-frozen exit 2 the check could not answer, so **bail** as a system failure, '
                  'never a REJECT, and launch no verifier.')
WRONG_TEST_SENTENCE = ('A revise of green whose leaf reports `WRONG_TEST: <why>` is exempt from the `SUITE:` line '
                       "and is routed as a develop-green `WRONG_TEST:` report is: "
                       "`$S/wrong-test-route.sh .tdd/revise-green-<k>.out '<target-test-id>'` runs before the "
                       "attempt is counted; its exit 0 writes no `revise` mark, spends no `REVISE_BUDGET` attempt "
                       "and launches the `red-contradicted` red, its exit 3 keeps the attempt's main outcome, a "
                       "verify-green REJECT, and its exit 2 is a bail; never a `report-missing` bail.")
PIN_RECORD_SENTENCE = ('A `⟦replaces-case⟧` step skips verify-red, so on that verify-pin PASS first run '
                       f"`$S/tests-frozen.sh record {RECORD_ARG} <test-path>` to record its replacement cases "
                       'before the deletion green checks them; tests-frozen exit 2 is a bail.')


def doc_of(heading):
    return {"## Revising on a REJECT": REVISE_MD, "## Already satisfied — the pin": PIN_MD}.get(heading, SKILL)


def numbered_section(heading):
    out, inside = [], False
    for n, line in enumerate(doc_of(heading).read_text().split("\n"), 1):
        if not inside:
            inside = line.startswith(heading)
        elif line.startswith("#"):
            break
        else:
            out.append((n, line))
    return out


def joined_section(heading):
    return " ".join(line.lstrip() for _, line in numbered_section(heading))


def lines_matching(heading, pattern):
    return [n for n, line in numbered_section(heading) if re.search(pattern, line)]


def any_between(numbers, lo, hi):
    return any(lo < n < hi for n in numbers)


def plain(text):
    return text.replace("*", "").replace("`", "").lower()


def sentences(text):
    return plain(text).replace(". ", ".\n").split("\n")


def frozen_sentences(heading):
    kept, fence = [], False
    for _, line in numbered_section(heading):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence:
            kept.append(line)
    return [s for s in sentences(" ".join(kept)) if "tests-frozen" in s]


def first(numbers):
    return numbers[0] if numbers else 0


def check_handling(where, found):
    text = "\n".join(found)
    problems = []
    for ok, what in (
        (re.search(r"exit 1|exits 1", text), "branches on check exit 1"),
        ("verify-green.reason" in text, "writes the changed file to .tdd/verify-green.reason"),
        (re.search(r"nam(e|es|ing) the (changed |test )?file", text), "says the reason names the file"),
        ("revise_budget" in text, "says a changed test spends REVISE_BUDGET"),
        (re.search(r"no verifier|not launch|without launching", text), "says no verifier is launched for that attempt"),
        (re.search(r"exit 0|exits 0", text), "says check exit 0 launches the verifier as before"),
    ):
        if not ok:
            problems.append(f"{where}: no sentence naming tests-frozen {what}")
    return problems


def test_revising_runs_tests_frozen_check_between_revise_green_and_its_reverify_rejecting_on_exit_1():
    wait = first(lines_matching(REVISE, r"wait-leaf\.sh revise-<phase>-<k>"))
    verify = first(lines_matching(REVISE, r"supervise\.sh verdict-<phase>"))
    check = lines_matching(REVISE, r"tests-frozen\.sh check")
    found = frozen_sentences(REVISE)
    assert check, "Revising on a REJECT never runs tests-frozen.sh check"
    assert any_between(check, wait, verify), (
        f"Revising runs tests-frozen.sh check, but not between the revise wait (line {wait}) and its re-verify (line {verify})")
    assert any("green" in s for s in found), "no sentence naming tests-frozen scopes the check to a revise of green"
    assert check_handling("Revising on a REJECT", found) == []


def test_every_tests_frozen_record_and_check_names_the_record_by_path_over_the_step_text_and_red_defines_the_key():
    text = SKILL.read_text()
    in_green = {n for n, _ in numbered_section(GREEN)}
    commands = [(n, line) for n, line in enumerate(text.split("\n"), 1)
                if re.search(r"tests-frozen\.sh (record|check)", line)
                and not (n in in_green and "tests-frozen.sh check" in line)]
    assert commands, "no tests-frozen.sh record or check command to read"
    for n, line in commands:
        assert f"tests-frozen.sh record {RECORD_ARG}" in line or f"tests-frozen.sh check {RECORD_ARG}" in line, (
            f"SKILL.md:{n} runs record or check without {RECORD_ARG}")
    assert "tests-frozen-<step>" not in text


def test_revising_runs_tests_frozen_record_once_a_revised_reds_reverify_passes():
    wait = first(lines_matching(REVISE, r"wait-leaf\.sh verdict-<phase>"))
    record = lines_matching(REVISE, r"tests-frozen\.sh record")
    assert record, "Revising on a REJECT never runs tests-frozen.sh record"
    assert any_between(record, wait, 999999), f"record does not follow the re-verify's wait (line {wait})"
    body = "\n".join(line for _, line in numbered_section(REVISE))
    assert f"tests-frozen.sh record {RECORD_ARG}" in body
    records = [s for s in frozen_sentences(REVISE) if "record" in s]
    assert re.search("red", "\n".join(records), re.I), "no sentence naming tests-frozen record scopes it to a revise of red"


def test_green_and_revising_handle_check_exit_2_as_a_system_failure_bail_never_a_reject():
    assert EXIT2_SENTENCE in joined_section(REVISE), "REVISE lacks the check exit 2 handling verbatim"


def test_revising_routes_a_revise_green_wrong_test_report_through_wrong_test_route_never_a_report_missing_bail():
    assert WRONG_TEST_SENTENCE in joined_section(REVISE)


def test_the_pin_records_a_replaces_case_steps_tests_at_its_verify_pin_pass_before_the_deletion_green():
    pin = joined_section(PIN)
    assert PIN_RECORD_SENTENCE in pin
    assert PIN_RECORD_SENTENCE in pin.partition("launch a green leaf exactly as")[0]


def test_green_and_revising_send_a_missing_behaviour_answer_to_red_missing_with_no_revise_attempt_and_verify_the_added_case_before_green_runs_again():
    revise = plain(joined_section(REVISE))
    assert re.search(r"impossible.*missing_test:.*red-missing", revise), (
        "REVISE.md's loop does not route a revise answering IMPOSSIBLE with a MISSING_TEST: line to red-missing")
