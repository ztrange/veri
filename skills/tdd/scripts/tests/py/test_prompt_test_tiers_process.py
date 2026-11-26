"""Which test command each phase's prompt tells its leaf to run, as the two prompt builders assemble them."""
import os
import re
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, new_repo
from skill_sections import plain

DEVELOP = SCRIPTS / "build-develop-prompt.sh"
VERIFY = SCRIPTS / "build-verify-prompt.sh"
BOUNDARY = "build-develop-prompt.sh and build-verify-prompt.sh run as real bash processes"

def lines_matching(pattern, text):
    return [line for line in text.split("\n") if re.search(pattern, line)]


def has_line(pattern, text):
    return bool(lines_matching(pattern, text))


def numbered_item(regex, text):
    item, collected = "", ""
    for line in text.split("\n"):
        numbered = re.match(r"[0-9]+\. ", line)
        if numbered and re.search(regex, item):
            return collected
        if numbered:
            item, collected = "", ""
        if numbered or item != "":
            item += " " + line
            collected += line + "\n"
    return collected if re.search(regex, item) else ""


_BUILDS = {}


def build(problems, builder, *argv):
    key = (builder, argv, os.getcwd(), tuple(sorted(i for i in os.environ.items() if i[0].startswith("VERI_"))))
    if key not in _BUILDS:
        done = subprocess.run([str(builder), *argv], capture_output=True, text=True)
        _BUILDS[key] = (done.returncode, done.stdout)
    returncode, stdout = _BUILDS[key]
    if returncode != 0:
        problems.append("%s %s exited %d" % (builder.name, argv[2] if argv[0] == "--fast-cmd" else argv[0], returncode))
    return stdout


def runs_affected(problems, label, prompt):
    named = "\n".join(lines_matching(r"affected-suites\.sh|timed-test-run\.sh changed", plain(prompt)))
    if not has_line(r"\brun", named):
        problems.append("%s's prompt never tells its leaf to run the suites affected-suites.sh prints" % label)


def runs_fast_plus_affected(problems, label, prompt):
    folded = plain(prompt)
    if "--tier fast" not in folded:
        problems.append("%s's prompt never names the fast command (detect-test-command.sh --tier fast)" % label)
    runs_affected(problems, label, prompt)
    if has_line(r"run (the )?(project's )?full (test )?suite|full suite (is )?green", folded):
        problems.append("%s's prompt still tells its leaf to run, or keep green, the full suite" % label)


def timed_through(problems, label, prompt, *tiers):
    runnable = ""
    for line in prompt.split("\n"):
        for cand in re.findall(r"[^ `]*timed-test-run\.sh", line):
            if os.access(cand, os.X_OK) and os.path.isfile(cand):
                runnable = cand
    if not runnable:
        problems.append("%s's prompt never names timed-test-run.sh at a path the leaf can run" % label)
    folded = plain(prompt)
    for tier in tiers:
        if not has_line(r"timed-test-run\.sh %s\b" % tier, folded):
            problems.append("%s's prompt never tells its leaf to run through timed-test-run.sh under tier %s" % (label, tier))


def never_timed_under(problems, label, prompt, tier):
    if has_line(r"timed-test-run\.sh %s\b" % tier, plain(prompt)):
        problems.append("%s's prompt still tells its leaf to run through timed-test-run.sh under tier %s" % (label, tier))


def names_prediction_file(problems, label, prompt):
    if not has_line(r"\.tdd/[A-Za-z0-9_<>.{}-]*prediction", plain(prompt)):
        problems.append("%s's prompt names no prediction file under .tdd/, so nothing records when the prediction was written" % label)


def names_run_output_file(problems, label, prompt):
    if not has_line(r"\.tdd/[A-Za-z0-9_<>.{}-]*(output|run)", plain(prompt)):
        problems.append("%s's prompt names no run-output file under .tdd/, so red-divergence.sh has no run to date the prediction file against" % label)


def probe_prompts(problems, probe, roster):
    for label, prompt in roster:
        probe(problems, label, prompt)


@pytest.fixture(scope="session")
def spec(tmp_path_factory):
    path = tmp_path_factory.mktemp("prompt-tiers") / "spec.md"
    path.write_text("zorblat must return frob\n")
    return str(path)


@pytest.fixture(autouse=True)
def runs_issue_number(monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "3123")


@pytest.fixture(scope="session")
def reason(tmp_path_factory):
    path = tmp_path_factory.mktemp("prompt-tiers") / "reason.md"
    path.write_text("the verifier objected to the fixture path\n")
    return str(path)


@pytest.mark.process(BOUNDARY)
def test_develop_red_and_verify_red_name_affected_suites_not_one_hand_named_suite_as_what_they_run(spec):
    problems = []
    verify_red = build(problems, VERIFY, "red", spec, "tests/zorblat.test.sh", "zorblat case")
    runs_affected(problems, "verify-red", verify_red)
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_verify_refactor_checklist_item_1_names_affected_suites_not_the_projects_full_test_suite(spec):
    problems = []
    verify_refactor = build(problems, VERIFY, "--fast-cmd", "make unit", "--step-green", "abc1234", "refactor", spec, "tests/zorblat.test.sh", "abc1234")
    item1 = numbered_item(r"^ 1\. still green", plain(verify_refactor))
    if not item1:
        problems.append("verify-refactor's prompt has no checklist item 1 ('1. still green')")
    if "the project's full test suite" in item1:
        problems.append("verify-refactor's checklist item 1 still says \"the project's full test suite\"")
    runs_affected(problems, "verify-refactor's checklist item 1", item1)
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_green_and_verify_green_name_the_fast_command_plus_the_affected_suites_not_the_full_suite(spec):
    problems = []
    verify_green = build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")
    runs_fast_plus_affected(problems, "verify-green", verify_green)
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_green_runs_the_fast_command_and_the_affected_suites_through_timed_test_run_under_tiers_fast_and_changed(spec):
    problems = []
    green = build(problems, DEVELOP, "green", spec, "QWIXTLE step", "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")
    timed_through(problems, "develop-green", green, "fast", "changed")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_red_refactor_and_reconcile_run_their_test_commands_through_timed_test_run_each_naming_its_tier(spec):
    problems = []
    red = build(problems, DEVELOP, "red", spec, "QWIXTLE step", "make test")
    refactor = build(problems, DEVELOP, "refactor", spec, "QWIXTLE step", "make test", "src/zorblat.sh")
    reconcile = build(problems, DEVELOP, "reconcile", spec, "QWIXTLE step", "make test", "tdd/1-zorblat", "abc1234")
    timed_through(problems, "develop-red", red, "changed")
    timed_through(problems, "develop-refactor", refactor, "changed")
    timed_through(problems, "develop-reconcile", reconcile, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_redoing_red_runs_affected_suites_through_timed_test_run_under_tier_changed_and_names_no_all_run(spec, reason):
    problems = []
    revise = build(problems, DEVELOP, "revise", "red", spec, "QWIXTLE step", "make test", reason)
    runs_affected(problems, "develop-revise red", revise)
    timed_through(problems, "develop-revise red", revise, "changed")
    never_timed_under(problems, "develop-revise red", revise, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_redoing_refactor_runs_affected_suites_through_timed_test_run_under_tier_changed_and_names_no_all_run(spec, reason):
    problems = []
    revise_refactor = build(problems, DEVELOP, "revise", "refactor", spec, "QWIXTLE step", "make test", reason)
    runs_affected(problems, "develop-revise refactor", revise_refactor)
    timed_through(problems, "develop-revise refactor", revise_refactor, "changed")
    never_timed_under(problems, "develop-revise refactor", revise_refactor, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_redoing_green_runs_the_fast_command_and_affected_suites_through_timed_test_run_under_tiers_fast_then_changed_and_names_no_all_run(spec, reason):
    problems = []
    revise_green = build(problems, DEVELOP, "revise", "green", spec, "QWIXTLE step", "make test", reason)
    timed_through(problems, "develop-revise green", revise_green, "fast", "changed")
    folded = plain(revise_green).split("\n")
    fast_at = next((i for i, line in enumerate(folded, 1) if re.search(r"timed-test-run\.sh fast( |$)", line)), None)
    affected_at = next((i for i, line in enumerate(folded, 1) if re.search(r"timed-test-run\.sh changed( |$)", line)), None)
    if fast_at and affected_at and fast_at > affected_at:
        problems.append("develop-revise green's prompt names the changed run before the fast one")
    never_timed_under(problems, "develop-revise green", revise_green, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_runs_the_tiers_of_the_phase_it_redoes_and_no_all_run_for_each_of_the_three(spec, reason):
    problems = []
    for phase, tiers in (("red", ["changed"]), ("green", ["fast", "changed"]), ("refactor", ["changed"])):
        redo = build(problems, DEVELOP, "revise", phase, spec, "QWIXTLE step", "make test", reason)
        timed_through(problems, "develop-revise " + phase, redo, *tiers)
        never_timed_under(problems, "develop-revise " + phase, redo, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_the_rebase_leaves_still_run_the_full_test_command_under_tier_all(spec):
    problems = []
    reconcile = build(problems, DEVELOP, "reconcile", spec, "QWIXTLE step", "make test", "tdd/1-zorblat", "abc1234")
    rebase = build(problems, DEVELOP, "rebase", spec, "QWIXTLE step", "make test", "abc1234", "def5678", "src/zorblat.sh")
    verify_rebase = build(problems, VERIFY, "rebase", spec, "abc1234", "def5678")
    timed_through(problems, "develop-rebase", rebase, "all")
    timed_through(problems, "develop-reconcile", reconcile, "all")
    timed_through(problems, "verify-rebase", verify_rebase, "all")
    for leaf, redo in (("develop-rebase", rebase), ("develop-reconcile", reconcile)):
        if "timed-test-run.sh all '' make test" not in plain(redo):
            problems.append("%s's prompt never runs the full test command, make test, under tier all" % leaf)
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_verify_red_green_refactor_and_pin_run_their_test_commands_through_timed_test_run_each_naming_its_tier(
        spec, tmp_path, monkeypatch):
    problems = []
    verify_red = build(problems, VERIFY, "red", spec, "tests/zorblat.test.sh", "zorblat case")
    verify_green = build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")
    verify_refactor = build(problems, VERIFY, "--fast-cmd", "make unit", "--step-green", "abc1234", "refactor", spec, "tests/zorblat.test.sh", "abc1234")
    own = new_repo(tmp_path / "own")  # the pin's --branch-base read needs a real commit of a tree laid out as veri's (#4263)
    base = commit_all(own, "base", **{"skills__tdd__scripts__tests__py__conftest.py": ""})
    monkeypatch.chdir(own)
    verify_pin = build(problems, VERIFY, "--branch-base", base, "pin", spec, "tests/zorblat.test.sh", "zorblat case")
    timed_through(problems, "verify-red", verify_red, "changed")
    timed_through(problems, "verify-green", verify_green, "fast", "changed")
    timed_through(problems, "verify-refactor", verify_refactor, "fast", "changed")
    timed_through(problems, "verify-pin", verify_pin, "target")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_verify_green_check_1_runs_the_target_test_through_timed_test_run_under_tier_target(spec):
    problems = []
    verify_green = build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")
    check1 = numbered_item(r"The target test passes", verify_green)
    if not check1:
        problems.append("verify-green's prompt has no numbered item saying the target test passes")
    timed_through(problems, "verify-green's check 1", check1, "target")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_the_develop_red_and_develop_revise_red_prompts_name_a_prediction_file_to_write_before_the_run(spec, reason):
    problems = []
    red = build(problems, DEVELOP, "red", spec, "QWIXTLE step", "make test")
    revise = build(problems, DEVELOP, "revise", "red", spec, "QWIXTLE step", "make test", reason)
    probe_prompts(problems, names_prediction_file, [("develop-red", red), ("develop-revise red", revise)])
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_the_develop_red_and_develop_revise_red_prompts_name_a_run_output_file_to_save_the_affected_suite_run_to(spec, reason):
    problems = []
    red = build(problems, DEVELOP, "red", spec, "QWIXTLE step", "make test")
    revise = build(problems, DEVELOP, "revise", "red", spec, "QWIXTLE step", "make test", reason)
    probe_prompts(problems, names_run_output_file, [("develop-red", red), ("develop-revise red", revise)])
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_1702_every_changed_tier_prompt_gives_make_test_with_tests_naming_the_suites_not_a_placeholder_for_the_command(
        spec, tmp_path, monkeypatch):
    problems = []
    step = "the zorblat is frobbed ⟦diff-checked⟧ ⟦criterion 1⟧"
    roster = [
        ("develop-green", build(problems, DEVELOP, "green", spec, "QWIXTLE step", "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")),
        ("develop-diff", build(problems, DEVELOP, "diff", spec, step, "make test", "make unit")),
        ("verify-green", build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-refactor", build(problems, VERIFY, "--fast-cmd", "make unit", "--step-green", "abc1234", "refactor", spec, "tests/zorblat.test.sh", "abc1234")),
    ]
    own = new_repo(tmp_path / "own")  # the diff's --branch-base read needs a real commit of a tree laid out as veri's (#4376)
    base = commit_all(own, "base", **{"skills__tdd__scripts__tests__py__conftest.py": ""})
    monkeypatch.chdir(own)
    roster.append(("verify-diff", build(problems, VERIFY, "--step", step, "--fast-cmd", "make unit", "--branch-base", base,
                                        "diff", spec, base)))
    for label, prompt in roster:
        folded = plain(prompt)
        if "<the command that runs them>" in folded:
            problems.append("%s's prompt still leaves the changed run's command as a placeholder" % label)
        if not has_line(r"timed-test-run\.sh changed .*make test tests=\"", folded):
            problems.append("%s's prompt never gives make test TESTS=\"<the suites>\" as the changed run's command" % label)
    assert problems == []
