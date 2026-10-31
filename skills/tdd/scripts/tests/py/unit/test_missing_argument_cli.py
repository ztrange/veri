import importlib
import pathlib
import re

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[3]
SHIM_MODULE = re.compile(r'^exec (?:python3|"\$py") .*/veri/(\w+)\.py"', re.MULTILINE)
FLOOR_KNOBS = {"VERI_BASH_MAJOR": "5", "VERI_PYTHON_VERSION": "3.12.0"}


def requires_argument(script):
    usage = re.search(r"usage: .*", script.read_text())
    return usage is not None and re.search(r"<.*?>", re.sub(r"\[[^\]]*\]", "", usage.group(0))) is not None


def subjects():
    return sorted(script.name for script in SCRIPTS.glob("*.sh") if requires_argument(script))


def module_of(name):
    return importlib.import_module(SHIM_MODULE.search((SCRIPTS / name).read_text()).group(1))


@pytest.mark.tree_audit("every skills/tdd/scripts/*.sh, read for its usage line and its shim")
@pytest.mark.parametrize("name", sorted(set(subjects()) | {"grade-prose.sh"}))
def test_a_script_requiring_a_positional_argument_exits_2_with_a_usage_line_when_called_with_none(name, run_cli):
    script = SCRIPTS / name
    assert script.is_file(), "%s does not exist" % name
    assert script.read_text().startswith("#!/bin/sh"), "%s is not a /bin/sh shim" % name
    assert name in subjects(), "the sweep does not cover %s" % name
    code, out, err = run_cli(module_of(name), [], env=FLOOR_KNOBS)
    assert code == 2, "%s: want exit 2, got %s: %s" % (name, code, err)
    assert "usage" in err, "%s: no usage line on stderr: %r" % (name, err)
    assert name in err, "%s: usage line does not name it: %r" % (name, err)


def roster_ids(roster):
    return ["%s %s" % (name, " ".join(repr(a) if a == "" else a for a in argv)) for name, argv in roster]


LATER_ARGUMENT_ROSTER = [
    ("add-ledger-step.sh", [".tdd/issue-1.md", "after", "anchor"]),
    ("build-develop-prompt.sh", ["green", "spec", "step"]),
    ("build-verify-prompt.sh", ["green"]),
    ("build-verify-prompt.sh", ["green", "spec"]),
    ("build-verify-prompt.sh", ["--step"]),
    ("issue-worktree.sh", ["270"]),
    ("issue-worktree.sh", ["--remove"]),
    ("over-budget.sh", ["unit"]),
    ("over-budget.sh", ["unit", "10"]),
    ("solvable-issues.sh", ["--repo"]),
    ("supervise.sh", ["develop-red"]),
    ("timed-test-run.sh", ["all"]),
    ("timed-test-run.sh", ["all", ""]),
    ("verify.sh", ["green"]),
    ("verify.sh", ["green", "spec"]),
    ("verify.sh", ["--step"]),
]

BAD_VALUE_ROSTER = [
    ("build-verify-prompt.sh", ["bogus", "spec", "test-path"]),
    ("build-develop-prompt.sh", ["bogus", "spec", "step", "cmd"]),
    ("build-develop-prompt.sh", ["revise", "bogus", "spec", "step", "cmd", "reason"]),
    ("build-verify-prompt.sh", ["green", "spec", "test-path"]),
    ("build-verify-prompt.sh", ["--fast-cmd", "x", "refactor", "spec", "test-path", "nothex"]),
    ("build-verify-prompt.sh", ["rebase", "spec", "nothex", "nothex"]),
    ("classify-bail.sh", ["bogus"]),
    ("leaf-timeout.sh", ["ten"]),
    ("push-branch.sh", ["--bogus"]),
    ("refactor-budget.sh", ["ten"]),
    ("step-cost.sh", ["--bogus"]),
    ("stop-requested.sh", ["--bogus"]),
    ("stop-run.sh", ["--mode", "bogus", "1"]),
    ("stop-run.sh", ["ten"]),
    ("workqueue.sh", ["bogus"]),
]

SLICE_6_ROSTER = [
    ("refactor-owed.sh", ["render"]),
    ("refactor-owed.sh", ["list"]),
    ("refactor-owed.sh", ["append"]),
]


def refused(name, argv, run_cli):
    code, out, err = run_cli(module_of(name), argv, env=FLOOR_KNOBS)
    shown = "%s %s" % (name, argv)
    assert code == 2, "%s: want exit 2, got %s: %s" % (shown, code, err)
    assert "usage" in err, "%s: no usage line on stderr: %r" % (shown, err)
    return err, shown


@pytest.mark.parametrize("name, argv", LATER_ARGUMENT_ROSTER, ids=roster_ids(LATER_ARGUMENT_ROSTER))
def test_a_script_exits_2_with_a_usage_line_when_a_later_required_argument_is_missing(name, argv, run_cli):
    refused(name, argv, run_cli)


@pytest.mark.parametrize("name, argv", BAD_VALUE_ROSTER, ids=roster_ids(BAD_VALUE_ROSTER))
def test_a_script_given_a_bad_argument_value_exits_2_with_its_own_usage_text_on_stderr(name, argv, run_cli):
    err, shown = refused(name, argv, run_cli)
    assert name in err, "%s: usage line does not name it: %r" % (shown, err)


@pytest.mark.parametrize("name, argv", SLICE_6_ROSTER, ids=roster_ids(SLICE_6_ROSTER))
def test_migration_slice_6_refuses_an_unresolvable_commit_or_a_missing_file_with_the_scripts_own_usage_text(name, argv, run_cli):
    err, shown = refused(name, argv, run_cli)
    assert name in err, "%s: usage line does not name it: %r" % (shown, err)

