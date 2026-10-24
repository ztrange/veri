"""Which test command each phase's prompt tells its leaf to run, as the two prompt builders assemble them."""
import os
import re
import subprocess

import pytest

from conftest import SCRIPTS
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
    key = (builder, argv)
    if key not in _BUILDS:
        done = subprocess.run([str(builder), *argv], capture_output=True, text=True)
        _BUILDS[key] = (done.returncode, done.stdout)
    returncode, stdout = _BUILDS[key]
    if returncode != 0:
        problems.append("%s %s exited %d" % (builder.name, argv[2] if argv[0] == "--fast-cmd" else argv[0], returncode))
    return stdout


def runs_affected(problems, label, prompt):
    named = "\n".join(lines_matching(r"affected-suites\.sh|timed-test-run\.sh affected", plain(prompt)))
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


def names_suite_runner(problems, label, prompt):
    if 'make test tests="<pytest file or node id>"' not in plain(prompt):
        problems.append("%s's prompt never names make test TESTS=\"<pytest file or node id>\", the invocation for running one suite" % label)
    if "convention like any other" in plain(prompt):
        problems.append("%s's prompt still leaves how to run one suite for the leaf to establish" % label)


def names_runner_fallback(problems, label, prompt):
    item = numbered_item(r'make test tests="<pytest file or node id>"', plain(prompt))
    if not item:
        problems.append("%s's prompt has no numbered item naming make test TESTS=\"<pytest file or node id>\"" % label)
        return
    if not has_line(r"fall back", item):
        problems.append("%s's prompt never tells its leaf what to run when make test TESTS=\"<pytest file or node id>\" cannot run a suite" % label)


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


@pytest.fixture(scope="session")
def reason(tmp_path_factory):
    path = tmp_path_factory.mktemp("prompt-tiers") / "reason.md"
    path.write_text("the verifier objected to the fixture path\n")
    return str(path)


@pytest.mark.process(BOUNDARY)
def test_develop_red_and_verify_red_name_affected_suites_not_one_hand_named_suite_as_what_they_run(spec):
    problems = []
    red = build(problems, DEVELOP, "red", spec, "QWIXTLE step", "make test")
    verify_red = build(problems, VERIFY, "red", spec, "tests/zorblat.test.sh", "zorblat case")
    runs_affected(problems, "develop-red", red)
    runs_affected(problems, "verify-red", verify_red)
    if has_line(r"run the suite that holds the new case", plain(red)):
        problems.append("develop-red still tells its leaf to run the one suite that holds the new case")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_verify_refactor_checklist_item_1_names_affected_suites_not_the_projects_full_test_suite(spec):
    problems = []
    verify_refactor = build(problems, VERIFY, "--fast-cmd", "make unit", "refactor", spec, "tests/zorblat.test.sh", "abc1234")
    item1 = numbered_item(r"^ 1\. still green", plain(verify_refactor))
    if not item1:
        problems.append("verify-refactor's prompt has no checklist item 1 ('1. still green')")
    if "the project's full test suite" in item1:
        problems.append("verify-refactor's checklist item 1 still says \"the project's full test suite\"")
    runs_affected(problems, "verify-refactor's checklist item 1", item1)
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_refactor_runs_affected_suites_fed_refactor_touched_output_after_each_transform(spec):
    problems = []
    refactor = build(problems, DEVELOP, "refactor", spec, "QWIXTLE step", "make test", "src/zorblat.sh")
    after_each = numbered_item(r"after each transform", plain(refactor))
    if not after_each:
        problems.append("develop-refactor's prompt has no numbered item saying what runs after each transform")
    runs_affected(problems, "develop-refactor's after-each-transform item", after_each)
    if "refactor-touched.sh" not in after_each:
        problems.append("develop-refactor's after-each-transform item never feeds affected-suites.sh refactor-touched.sh's output")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_green_and_verify_green_name_the_fast_command_plus_the_affected_suites_not_the_full_suite(spec):
    problems = []
    green = build(problems, DEVELOP, "green", spec, "QWIXTLE step", "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")
    verify_green = build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")
    runs_fast_plus_affected(problems, "develop-green", green)
    runs_fast_plus_affected(problems, "verify-green", verify_green)
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_green_runs_the_fast_command_and_the_affected_suites_through_timed_test_run_under_tiers_fast_and_affected(spec):
    problems = []
    green = build(problems, DEVELOP, "green", spec, "QWIXTLE step", "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")
    timed_through(problems, "develop-green", green, "fast", "affected")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_red_refactor_and_reconcile_run_their_test_commands_through_timed_test_run_each_naming_its_tier(spec):
    problems = []
    red = build(problems, DEVELOP, "red", spec, "QWIXTLE step", "make test")
    refactor = build(problems, DEVELOP, "refactor", spec, "QWIXTLE step", "make test", "src/zorblat.sh")
    reconcile = build(problems, DEVELOP, "reconcile", spec, "QWIXTLE step", "make test", "tdd/1-zorblat", "abc1234")
    timed_through(problems, "develop-red", red, "affected")
    timed_through(problems, "develop-refactor", refactor, "affected")
    timed_through(problems, "develop-reconcile", reconcile, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_redoing_red_runs_affected_suites_through_timed_test_run_under_tier_affected_and_names_no_all_run(spec, reason):
    problems = []
    revise = build(problems, DEVELOP, "revise", "red", spec, "QWIXTLE step", "make test", reason)
    runs_affected(problems, "develop-revise red", revise)
    timed_through(problems, "develop-revise red", revise, "affected")
    never_timed_under(problems, "develop-revise red", revise, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_redoing_refactor_runs_affected_suites_through_timed_test_run_under_tier_affected_and_names_no_all_run(spec, reason):
    problems = []
    revise_refactor = build(problems, DEVELOP, "revise", "refactor", spec, "QWIXTLE step", "make test", reason)
    runs_affected(problems, "develop-revise refactor", revise_refactor)
    timed_through(problems, "develop-revise refactor", revise_refactor, "affected")
    never_timed_under(problems, "develop-revise refactor", revise_refactor, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_redoing_green_runs_the_fast_command_and_affected_suites_through_timed_test_run_under_tiers_fast_then_affected_and_names_no_all_run(spec, reason):
    problems = []
    revise_green = build(problems, DEVELOP, "revise", "green", spec, "QWIXTLE step", "make test", reason)
    timed_through(problems, "develop-revise green", revise_green, "fast", "affected")
    folded = plain(revise_green).split("\n")
    fast_at = next((i for i, line in enumerate(folded, 1) if re.search(r"timed-test-run\.sh fast( |$)", line)), None)
    affected_at = next((i for i, line in enumerate(folded, 1) if re.search(r"timed-test-run\.sh affected( |$)", line)), None)
    if fast_at and affected_at and fast_at > affected_at:
        problems.append("develop-revise green's prompt names the affected run before the fast one")
    never_timed_under(problems, "develop-revise green", revise_green, "all")
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_develop_revise_runs_the_tiers_of_the_phase_it_redoes_and_no_all_run_for_each_of_the_three(spec, reason):
    problems = []
    for phase, tiers in (("red", ["affected"]), ("green", ["fast", "affected"]), ("refactor", ["affected"])):
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
def test_verify_red_green_refactor_and_pin_run_their_test_commands_through_timed_test_run_each_naming_its_tier(spec):
    problems = []
    verify_red = build(problems, VERIFY, "red", spec, "tests/zorblat.test.sh", "zorblat case")
    verify_green = build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")
    verify_refactor = build(problems, VERIFY, "--fast-cmd", "make unit", "refactor", spec, "tests/zorblat.test.sh", "abc1234")
    verify_pin = build(problems, VERIFY, "pin", spec, "tests/zorblat.test.sh", "zorblat case")
    timed_through(problems, "verify-red", verify_red, "affected")
    timed_through(problems, "verify-green", verify_green, "fast", "affected")
    timed_through(problems, "verify-refactor", verify_refactor, "fast", "affected")
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


def developer_roster(problems, spec):
    return [
        ("develop-red", build(problems, DEVELOP, "red", spec, "QWIXTLE step", "make test")),
        ("develop-green", build(problems, DEVELOP, "green", spec, "QWIXTLE step", "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")),
        ("develop-refactor", build(problems, DEVELOP, "refactor", spec, "QWIXTLE step", "make test", "src/zorblat.sh")),
    ]


def verifier_roster(problems, spec):
    return [
        ("verify-red", build(problems, VERIFY, "red", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-green", build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-refactor", build(problems, VERIFY, "--fast-cmd", "make unit", "refactor", spec, "tests/zorblat.test.sh", "abc1234")),
        ("verify-pin", build(problems, VERIFY, "pin", spec, "tests/zorblat.test.sh", "zorblat case")),
    ]


@pytest.mark.process(BOUNDARY)
def test_every_developer_prompt_that_runs_a_suite_names_make_test_tests_as_the_single_suite_invocation(spec):
    problems = []
    probe_prompts(problems, names_suite_runner, developer_roster(problems, spec))
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_every_developer_prompt_that_names_make_test_tests_tells_its_leaf_what_to_run_when_the_repository_has_none(spec):
    problems = []
    probe_prompts(problems, names_runner_fallback, developer_roster(problems, spec))
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_every_develop_revise_prompt_names_make_test_tests_so_a_redos_affected_suite_runs_apply_make_tests_environment(spec, reason):
    problems = []
    roster = [
        ("develop-revise " + phase, build(problems, DEVELOP, "revise", phase, spec, "QWIXTLE step", "make test", reason))
        for phase in ("red", "green", "refactor")
    ]
    probe_prompts(problems, names_suite_runner, roster)
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
def test_every_blind_verifier_prompt_names_make_test_tests_as_the_single_suite_invocation(spec):
    problems = []
    probe_prompts(problems, names_suite_runner, verifier_roster(problems, spec))
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_every_blind_verifier_prompt_that_names_make_test_tests_tells_its_leaf_what_to_run_when_the_repository_has_none(spec):
    problems = []
    probe_prompts(problems, names_runner_fallback, verifier_roster(problems, spec))
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_1702_every_affected_tier_prompt_gives_make_test_with_tests_naming_the_suites_not_a_placeholder_for_the_command(spec):
    problems = []
    step = "the zorblat is frobbed ⟦diff-checked⟧ ⟦criterion 1⟧"
    roster = [
        ("develop-green", build(problems, DEVELOP, "green", spec, "QWIXTLE step", "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")),
        ("develop-diff", build(problems, DEVELOP, "diff", spec, step, "make test", "make unit")),
        ("verify-green", build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-refactor", build(problems, VERIFY, "--fast-cmd", "make unit", "refactor", spec, "tests/zorblat.test.sh", "abc1234")),
        ("verify-diff", build(problems, VERIFY, "--step", step, "--fast-cmd", "make unit", "diff", spec, "0123abc", "4567def")),
    ]
    for label, prompt in roster:
        folded = plain(prompt)
        if "<the command that runs them>" in folded:
            problems.append("%s's prompt still leaves the affected run's command as a placeholder" % label)
        if not has_line(r"timed-test-run\.sh affected .*make test tests=\"", folded):
            problems.append("%s's prompt never gives make test TESTS=\"<the suites>\" as the affected run's command" % label)
    assert problems == []


@pytest.mark.process(BOUNDARY)
def test_1702_no_prompt_asking_for_an_affected_run_leaves_the_command_a_placeholder_or_drops_tests(spec, reason):
    problems = []
    step = "the zorblat is frobbed ⟦diff-checked⟧ ⟦criterion 1⟧"
    sha = "abc1234"
    roster = []
    for phase in ("red", "cover", "transform"):
        roster.append(("develop-" + phase, build(problems, DEVELOP, phase, spec, step, "make test")))
    roster += [
        ("develop-green", build(problems, DEVELOP, "green", spec, step, "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")),
        ("develop-refactor", build(problems, DEVELOP, "refactor", spec, step, "make test", "src/zorblat.sh")),
        ("develop-diff", build(problems, DEVELOP, "diff", spec, step, "make test", "make unit")),
        ("develop-structural", build(problems, DEVELOP, "structural", spec, step, "make test", "src/zorblat.sh")),
        ("develop-predicate", build(problems, DEVELOP, "predicate", spec, step, "make test", "src/zorblat.sh")),
        ("develop-exhausted", build(problems, DEVELOP, "exhausted", spec, step, "make test", reason)),
        ("develop-reconcile", build(problems, DEVELOP, "reconcile", spec, step, "make test", "tdd/x", sha)),
        ("develop-over-budget", build(problems, DEVELOP, "over-budget", spec, step, "make test", "9", "5")),
        ("develop-rebase", build(problems, DEVELOP, "rebase", spec, step, "make test", sha, sha, "a.sh")),
        ("develop-revise diff", build(problems, DEVELOP, "revise", "diff", spec, step, "make test", reason, "make unit")),
    ]
    for phase in ("red", "green", "refactor", "expand", "migrate", "contract-a", "contract-b"):
        roster.append(("develop-revise " + phase, build(problems, DEVELOP, "revise", phase, spec, step, "make test", reason)))
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        roster.append(("develop-" + phase, build(problems, DEVELOP, phase, spec, step, "make test")))
    roster += [
        ("verify-red", build(problems, VERIFY, "red", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-green", build(problems, VERIFY, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-refactor", build(problems, VERIFY, "--fast-cmd", "make unit", "refactor", spec, "tests/zorblat.test.sh", sha)),
        ("verify-pin", build(problems, VERIFY, "pin", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-transform", build(problems, VERIFY, "transform", spec, "tests/zorblat.test.sh", sha)),
        ("verify-diff", build(problems, VERIFY, "--step", step, "--fast-cmd", "make unit", "diff", spec, sha, "4567def")),
    ]
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        roster.append(("verify-" + phase, build(problems, VERIFY, "--fast-cmd", "make unit", phase, spec, "tests/zorblat.test.sh", sha)))
    asking = []
    for label, prompt in roster:
        folded = plain(prompt)
        if not has_line(r"timed-test-run\.sh affected", folded):
            continue
        asking.append(label)
        if "<the command that runs them>" in folded:
            problems.append("%s's prompt still leaves the affected run's command as a placeholder" % label)
        if not has_line(r"timed-test-run\.sh affected .*make test tests=\"", folded):
            problems.append("%s's prompt never gives make test TESTS=\"<the suites>\" as the affected run's command" % label)
    for named in ("develop-red", "develop-green", "develop-refactor", "develop-cover", "develop-diff", "develop-transform",
                  "develop-structural", "develop-expand", "develop-migrate", "develop-contract-a", "develop-contract-b",
                  "develop-revise red", "develop-revise green", "develop-revise refactor", "develop-revise diff",
                  "develop-revise expand", "develop-revise migrate", "develop-revise contract-a", "develop-revise contract-b",
                  "verify-red", "verify-green", "verify-refactor", "verify-transform", "verify-diff",
                  "verify-expand", "verify-migrate", "verify-contract-a", "verify-contract-b"):
        if named not in asking:
            problems.append("%s's prompt renders no affected run, so the roster covers nothing there" % named)
    assert problems == []


def test_the_prompt_probes_accept_a_matching_prompt_and_object_to_a_non_matching_one(tmp_path):
    runner = tmp_path / "timed-test-run.sh"
    runner.write_text("#!/bin/sh\n")
    runner.chmod(0o755)
    matching = "\n".join([
        "Run `%s fast '' make unit` first, with --tier fast." % runner,
        "Then run `%s affected 'x' sh -c y` over what affected-suites.sh prints." % runner,
    ])

    def tally(prompt):
        problems = []
        runs_fast_plus_affected(problems, "develop-green", prompt)
        timed_through(problems, "develop-green", prompt, "fast", "affected")
        return problems

    assert tally(matching) == []
    assert tally("a prompt that names none of it") != []


def test_numbered_item_given_runner_dot_literal_selects_the_runner_item_not_the_runnerxsh_one():
    assert numbered_item(r"runner\.sh", "1. runnerXsh\n2. runner.sh").rstrip("\n") == "2. runner.sh"
