"""Medium case for the Makefile's test and unit targets: make started for real over a planted tests tree."""
import os
import shutil
import subprocess

import pytest

from conftest import ROOT, SCRIPTS

PLANTED_CONFTEST = '''import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "process(boundary): a medium case")
    config.addinivalue_line("markers", "tree_audit(sweeps): a tree-audit case")
'''
PLANTED_CASES = '''import os

import pytest


def note(what):
    with open(os.environ["PLANTED_RAN_LOG"], "a") as log:
        log.write(what + "\\n")


def test_small():
    note("pytest small")


@pytest.mark.process("planted")
def test_medium():
    note("pytest medium")
'''
BASH_TRIPWIRE = '#!/bin/sh\nprintf "bash suite\\n" >> "$PLANTED_RAN_LOG"\necho "1 passed, 0 failed"\n'


def planted_tree(tmp_path, small=PLANTED_CASES.split("@pytest.mark.process")[0]):
    tree = tmp_path / "tree"
    scripts = tree / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(ROOT / "Makefile", tree / "Makefile")
    for name in ("veri", "lib", "run-suite.sh"):
        (scripts / name).symlink_to(SCRIPTS / name)
    py = scripts / "tests" / "py"
    (py / "unit").mkdir(parents=True)
    (py / "conftest.py").write_text(PLANTED_CONFTEST)
    (py / "unit" / "test_planted_small.py").write_text(small)
    (py / "test_planted_medium.py").write_text(PLANTED_CASES.replace("def test_small", "def test_other_small"))
    for suite in (scripts / "tests" / "planted.test.sh", scripts / "tests" / "unit" / "planted-unit.test.sh"):
        suite.parent.mkdir(exist_ok=True)
        suite.write_text(BASH_TRIPWIRE)
        suite.chmod(0o755)
    return tree


def make(tree, log, target, **veri):
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env.update(veri)
    env["PLANTED_RAN_LOG"] = str(log)
    ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    return ran.returncode, sorted(log.read_text().splitlines()), ran.stdout + ran.stderr


@pytest.mark.process("make test and make unit started for real over a planted tree holding a small case, a medium case and a bash suite each")
def test_make_test_and_make_unit_each_run_one_pytest_and_no_bash_suite_unit_the_small_cases_and_test_the_small_and_medium_cases(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    unit = make(tree, log, "unit")
    full = make(tree, log, "test")
    assert (unit[0], unit[1]) == (0, ["pytest small"]), unit[2]
    assert (full[0], full[1]) == (0, ["pytest medium", "pytest small", "pytest small"]), full[2]


@pytest.mark.process("make unit and make test started for real over a planted tree whose small case fails")
def test_a_failing_case_fails_make_unit_and_make_test_with_no_bash_suite_run(tmp_path):
    failing = PLANTED_CASES.split("@pytest.mark.process")[0].replace('note("pytest small")', 'note("pytest small")\n    assert False')
    tree, log = planted_tree(tmp_path, small=failing), tmp_path / "ran.log"
    unit = make(tree, log, "unit")
    full = make(tree, log, "test")
    assert (unit[0], unit[1]) == (2, ["pytest small"]), unit[2]
    assert (full[0], full[1]) == (2, ["pytest medium", "pytest small", "pytest small"]), full[2]


@pytest.mark.process("make unit started for real over a planted tree whose only unit case is medium, so its selection collects nothing")
def test_a_selection_that_collects_nothing_fails_make_unit_with_no_bash_suite_run(tmp_path):
    medium_only = PLANTED_CASES.replace("def test_small", "def _not_a_case")
    tree, log = planted_tree(tmp_path, small=medium_only), tmp_path / "ran.log"
    code, ran, output = make(tree, log, "unit")
    assert (code, ran) == (2, []), output


@pytest.mark.process("make unit and make test started for real under a bash older than 5")
def test_the_bash_version_refusal_precedes_pytest_in_make_unit_and_make_test(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    for target in ("unit", "test"):
        code, ran, output = make(tree, log, target, VERI_BASH_MAJOR="4")
        assert (code, ran, "veri needs bash 5 or newer" in output) == (2, [], True), output
