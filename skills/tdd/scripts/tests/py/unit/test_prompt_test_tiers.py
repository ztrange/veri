"""Which test command each phase's prompt tells its leaf to run, as the two prompt builders assemble them."""
import importlib
import os
import re

import pytest

from skill_sections import plain


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


@pytest.fixture(scope="session")
def spec(tmp_path_factory):
    path = tmp_path_factory.mktemp("prompt-tiers") / "spec.md"
    path.write_text("zorblat must return frob\n")
    return str(path)


@pytest.fixture(autouse=True)
def runs_issue_number(monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "3123")


@pytest.fixture(autouse=True)
def branch_base_is_veris_own_tree(monkeypatch):
    """git refuses in this tier: a verify-pin's or verify-diff's --branch-base reads as a commit holding the working
    tree's own CLAUDE.md and layout (#4263, #4376)."""
    run_line = importlib.import_module("veri.build_verify_prompt").run_line

    def at_base(branch_base, root):
        claude = os.path.join(root, "CLAUDE.md")
        held = open(claude, "rb").read() if os.path.isfile(claude) else b""
        return (held, run_line.own_tree(root)) if branch_base else None

    monkeypatch.setattr(run_line, "_at_base", at_base)


@pytest.fixture
def build_develop_prompt():
    return importlib.import_module("veri.build_develop_prompt")


@pytest.fixture
def build_verify_prompt():
    return importlib.import_module("veri.build_verify_prompt")


@pytest.fixture(scope="session")
def reason(tmp_path_factory):
    path = tmp_path_factory.mktemp("prompt-tiers") / "reason.md"
    path.write_text("the verifier objected to the fixture path\n")
    return str(path)


REBASED_TIP = ("develop-rebase", "develop-reconcile", "verify-rebase")
NAMED = ("develop-red", "develop-green", "develop-refactor", "develop-cover", "develop-diff", "develop-transform",
         "develop-structural", "develop-expand", "develop-migrate", "develop-contract-a", "develop-contract-b",
         "develop-revise red", "develop-revise green", "develop-revise refactor", "develop-revise diff",
         "develop-revise expand", "develop-revise migrate", "develop-revise contract-a", "develop-revise contract-b",
         "verify-red", "verify-green", "verify-refactor", "verify-transform", "verify-diff",
         "verify-expand", "verify-migrate", "verify-contract-a", "verify-contract-b")


def roster_of(problems, spec, reason, run_cli, build_develop_prompt, build_verify_prompt):
    def render(module, *argv):
        code, out, _ = run_cli(module, list(argv))
        if code != 0:
            problems.append("%s %s exited %d" % (module.__name__.rsplit(".", 1)[-1], argv[2] if argv[0] == "--fast-cmd" else argv[0], code))
        return out

    def develop(*argv):
        return render(build_develop_prompt, *argv)

    def verify(*argv):
        return render(build_verify_prompt, *argv)

    step = "the zorblat is frobbed ⟦diff-checked⟧ ⟦criterion 1⟧"
    sha = "abc1234"
    roster = []
    for phase in ("red", "cover", "transform"):
        roster.append(("develop-" + phase, develop(phase, spec, step, "make test")))
    roster += [
        ("develop-green", develop("green", spec, step, "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")),
        ("develop-refactor", develop("refactor", spec, step, "make test", "src/zorblat.sh")),
        ("develop-diff", develop("diff", spec, step, "make test", "make unit")),
        ("develop-structural", develop("structural", spec, step, "make test", "src/zorblat.sh")),
        ("develop-predicate", develop("predicate", spec, step, "make test", "src/zorblat.sh")),
        ("develop-exhausted", develop("exhausted", spec, step, "make test", reason)),
        ("develop-reconcile", develop("reconcile", spec, step, "make test", "tdd/x", sha)),
        ("develop-over-budget", develop("over-budget", spec, step, "make test", "9", "5")),
        ("develop-rebase", develop("rebase", spec, step, "make test", sha, sha, "a.sh")),
        ("develop-revise diff", develop("revise", "diff", spec, step, "make test", reason, "make unit")),
    ]
    for phase in ("red", "green", "refactor", "expand", "migrate", "contract-a", "contract-b"):
        roster.append(("develop-revise " + phase, develop("revise", phase, spec, step, "make test", reason)))
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        roster.append(("develop-" + phase, develop(phase, spec, step, "make test")))
    roster += [
        ("verify-red", verify("red", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-green", verify("--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-refactor", verify("--fast-cmd", "make unit", "--step-green", sha, "refactor", spec, "tests/zorblat.test.sh", sha)),
        ("verify-pin", verify("--branch-base", "abc1234", "pin", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-transform", verify("--fast-cmd", "make unit", "transform", spec, "tests/zorblat.test.sh", sha)),
        ("verify-diff", verify("--step", step, "--fast-cmd", "make unit", "--branch-base", sha, "diff", spec, "4567def")),
    ]
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        roster.append(("verify-" + phase, verify("--fast-cmd", "make unit", phase, spec, "tests/zorblat.test.sh", sha)))
    return roster


def test_1702_no_prompt_asking_for_a_changed_run_leaves_the_command_a_placeholder_or_drops_tests(spec, reason, run_cli, build_develop_prompt, build_verify_prompt):
    problems = []
    roster = roster_of(problems, spec, reason, run_cli, build_develop_prompt, build_verify_prompt)
    asking = []
    for label, prompt in roster:
        folded = plain(prompt)
        if not has_line(r"timed-test-run\.sh changed", folded):
            continue
        asking.append(label)
        if "<the command that runs them>" in folded:
            problems.append("%s's prompt still leaves the changed run's command as a placeholder" % label)
        if not has_line(r"timed-test-run\.sh changed .*make test tests=\"", folded):
            problems.append("%s's prompt never gives make test TESTS=\"<the test files>\" as the changed run's command" % label)
    for named in NAMED:
        if named not in asking:
            problems.append("%s's prompt renders no changed run, so the roster covers nothing there" % named)
    assert problems == []


def test_4333_no_leaf_or_verifier_but_the_rebased_tip_ones_is_told_to_run_more_than_the_fast_command_and_the_changed_files_tests(spec, reason, run_cli, build_develop_prompt, build_verify_prompt):
    problems = []
    roster = roster_of(problems, spec, reason, run_cli, build_develop_prompt, build_verify_prompt)
    for label, prompt in roster:
        if label in REBASED_TIP:
            continue
        folded = plain(prompt)
        for line in lines_matching(r"timed-test-run\.sh (affected|all)\b", folded):
            problems.append("%s's prompt times a run under a tier broader than changed: %s" % (label, line.strip()))
        for line in lines_matching(r"timed-test-run\.sh \S+ '[^']*' make test\b", folded):
            if "tests=" not in line:
                problems.append("%s's prompt times the bare full test command: %s" % (label, line.strip()))
        if has_line(r"--tier all\b", folded):
            problems.append("%s's prompt tells its leaf to run the --tier all command" % label)
    timed = dict(roster)
    for named in NAMED:
        if not has_line(r"timed-test-run\.sh changed '", plain(timed[named])):
            problems.append("%s's prompt never times its covering-tests run under changed" % named)
    assert problems == []


def test_the_prompt_probes_accept_a_matching_prompt_and_object_to_a_non_matching_one(tmp_path):
    runner = tmp_path / "timed-test-run.sh"
    runner.write_text("#!/bin/sh\n")
    runner.chmod(0o755)
    matching = "\n".join([
        "Run `%s fast '' make unit` first, with --tier fast." % runner,
        "Then run `%s changed 'x' sh -c y` over what affected-suites.sh prints." % runner,
    ])

    def tally(prompt):
        problems = []
        runs_fast_plus_affected(problems, "develop-green", prompt)
        timed_through(problems, "develop-green", prompt, "fast", "changed")
        return problems

    assert tally(matching) == []
    assert tally("a prompt that names none of it") != []


def test_numbered_item_given_runner_dot_literal_selects_the_runner_item_not_the_runnerxsh_one():
    assert numbered_item(r"runner\.sh", "1. runnerXsh\n2. runner.sh").rstrip("\n") == "2. runner.sh"


def test_issue_4335_a_foreign_tree_declaring_a_quiet_command_gets_it_run_over_the_changed_files_tests_in_every_timed_changed_run(spec, reason, run_cli, build_develop_prompt, build_verify_prompt, tmp_path, monkeypatch):
    (tmp_path / "CLAUDE.md").write_text(
        "veri: one test file: pytest $1\n"
        "veri: quiet test files: pytest -q --no-header -rf\n")
    monkeypatch.chdir(tmp_path)
    problems = []
    roster = dict(roster_of(problems, spec, reason, run_cli, build_develop_prompt, build_verify_prompt))
    quiet_run = "' sh -c 'pytest -q --no-header -rf \"$@\"' sh <those paths>"
    for named in NAMED:
        changed = lines_matching(r"timed-test-run\.sh changed '", plain(roster[named]))
        if not changed or not all(quiet_run in line for line in changed):
            problems.append("%s's prompt never gives the declared quiet command over the changed paths: %s" % (named, changed))
    assert problems == []
