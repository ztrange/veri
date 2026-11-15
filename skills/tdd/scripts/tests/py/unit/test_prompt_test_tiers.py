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


@pytest.fixture(scope="session")
def spec(tmp_path_factory):
    path = tmp_path_factory.mktemp("prompt-tiers") / "spec.md"
    path.write_text("zorblat must return frob\n")
    return str(path)


@pytest.fixture(autouse=True)
def runs_issue_number(monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "3123")


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


def test_1702_no_prompt_asking_for_an_affected_run_leaves_the_command_a_placeholder_or_drops_tests(spec, reason, run_cli, build_develop_prompt, build_verify_prompt):
    def render(problems, module, *argv):
        code, out, _ = run_cli(module, list(argv))
        if code != 0:
            problems.append("%s %s exited %d" % (module.__name__.rsplit(".", 1)[-1], argv[2] if argv[0] == "--fast-cmd" else argv[0], code))
        return out

    def develop(problems, *argv):
        return render(problems, build_develop_prompt, *argv)

    def verify(problems, *argv):
        return render(problems, build_verify_prompt, *argv)

    problems = []
    step = "the zorblat is frobbed ⟦diff-checked⟧ ⟦criterion 1⟧"
    sha = "abc1234"
    roster = []
    for phase in ("red", "cover", "transform"):
        roster.append(("develop-" + phase, develop(problems, phase, spec, step, "make test")))
    roster += [
        ("develop-green", develop(problems, "green", spec, step, "make test", "tests/zorblat.test.sh", "zorblat case", "make unit")),
        ("develop-refactor", develop(problems, "refactor", spec, step, "make test", "src/zorblat.sh")),
        ("develop-diff", develop(problems, "diff", spec, step, "make test", "make unit")),
        ("develop-structural", develop(problems, "structural", spec, step, "make test", "src/zorblat.sh")),
        ("develop-predicate", develop(problems, "predicate", spec, step, "make test", "src/zorblat.sh")),
        ("develop-exhausted", develop(problems, "exhausted", spec, step, "make test", reason)),
        ("develop-reconcile", develop(problems, "reconcile", spec, step, "make test", "tdd/x", sha)),
        ("develop-over-budget", develop(problems, "over-budget", spec, step, "make test", "9", "5")),
        ("develop-rebase", develop(problems, "rebase", spec, step, "make test", sha, sha, "a.sh")),
        ("develop-revise diff", develop(problems, "revise", "diff", spec, step, "make test", reason, "make unit")),
    ]
    for phase in ("red", "green", "refactor", "expand", "migrate", "contract-a", "contract-b"):
        roster.append(("develop-revise " + phase, develop(problems, "revise", phase, spec, step, "make test", reason)))
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        roster.append(("develop-" + phase, develop(problems, phase, spec, step, "make test")))
    roster += [
        ("verify-red", verify(problems, "red", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-green", verify(problems, "--fast-cmd", "make unit", "green", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-refactor", verify(problems, "--fast-cmd", "make unit", "refactor", spec, "tests/zorblat.test.sh", sha)),
        ("verify-pin", verify(problems, "--branch-base", "abc1234", "pin", spec, "tests/zorblat.test.sh", "zorblat case")),
        ("verify-transform", verify(problems, "transform", spec, "tests/zorblat.test.sh", sha)),
        ("verify-diff", verify(problems, "--step", step, "--fast-cmd", "make unit", "diff", spec, sha, "4567def")),
    ]
    for phase in ("expand", "migrate", "contract-a", "contract-b"):
        roster.append(("verify-" + phase, verify(problems, "--fast-cmd", "make unit", phase, spec, "tests/zorblat.test.sh", sha)))
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
