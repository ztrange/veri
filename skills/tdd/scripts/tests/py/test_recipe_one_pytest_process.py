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
WORKER_COUNT_CASE = '''import os


def test_small():
    with open(os.environ["PLANTED_RAN_LOG"], "a") as log:
        log.write("workers %s\\n" % os.environ.get("PYTEST_XDIST_WORKER_COUNT", "1"))
'''
BASH_TRIPWIRE = '#!/bin/sh\nprintf "bash suite\\n" >> "$PLANTED_RAN_LOG"\necho "1 passed, 0 failed"\n'


def planted_tree(tmp_path, small=PLANTED_CASES.split("@pytest.mark.process")[0]):
    tree = tmp_path / "tree"
    scripts = tree / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(ROOT / "Makefile", tree / "Makefile")
    for name in ("veri", "lib", "prose-owed.sh"):
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
    env.update({"VERI_PYTEST_WORKERS": "1", **veri})
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


@pytest.mark.process("make test started for real over a planted tree, naming a file and a node id together")
def test_make_test_with_tests_naming_a_file_and_a_node_id_runs_only_those_in_one_invocation(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    py = "skills/tdd/scripts/tests/py"
    targets = "%s/unit/test_planted_small.py %s/test_planted_medium.py::test_medium" % (py, py)
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_WORKERS"] = "1"
    env["PLANTED_RAN_LOG"] = str(log)
    ran = subprocess.run(["make", "-C", str(tree), "test", "TESTS=" + targets], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)
    assert (ran.returncode, sorted(log.read_text().splitlines()), ran.stdout.count("== pytest")) == \
        (0, ["pytest medium", "pytest small"], 1), ran.stdout + ran.stderr


@pytest.mark.process("make unit and make test started for real, with two pytest workers, over a planted tree whose small case fails")
def test_two_workers_pass_and_fail_the_same_cases_as_serial_and_name_a_failing_case_by_its_node_id(tmp_path):
    failing = PLANTED_CASES.split("@pytest.mark.process")[0].replace('note("pytest small")', 'note("pytest small")\n    assert False')
    tree, log = planted_tree(tmp_path, small=failing), tmp_path / "ran.log"
    node = "skills/tdd/scripts/tests/py/unit/test_planted_small.py::test_small"
    for target, ran_cases, counts in (("unit", ["pytest small"], "1 failed in"),
                                      ("test", ["pytest medium", "pytest small", "pytest small"], "1 failed, 2 passed in")):
        serial = make(tree, log, target, VERI_PYTEST_WORKERS="1")
        parallel = make(tree, log, target, VERI_PYTEST_WORKERS="2")
        output = parallel[2]
        assert (parallel[0], parallel[1]) == (serial[0], serial[1]) == (2, ran_cases), output
        assert [line.startswith("FAILED " + node) for line in output.splitlines() if line.startswith("FAILED ")] == [True], output
        assert counts in output, output
        assert ("SUITES FAILED" in output, "all suites green" in output) == ("SUITES FAILED" in serial[2], False), output


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real with VERI_PYTEST_WORKERS unset, over a planted tree whose small case notes its worker count")
def test_with_no_worker_count_set_make_unit_runs_four_workers_and_make_test_one_per_available_core(tmp_path):
    tree, log = planted_tree(tmp_path, small=WORKER_COUNT_CASE), tmp_path / "ran.log"
    cores = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
    env = {k: v for k, v in os.environ.items() if not k.startswith(("VERI_", "PYTEST_XDIST_"))}
    env["PLANTED_RAN_LOG"] = str(log)
    for target, workers in (("unit", 4), ("test", cores)):
        log.write_text("")
        ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                             capture_output=True, text=True)
        noted = [line for line in log.read_text().splitlines() if line.startswith("workers ")]
        assert (target, ran.returncode, noted) == (target, 0, ["workers %d" % workers]), ran.stdout + ran.stderr


@pytest.mark.process("make unit started for real twice over a planted tree whose sources do not change between the runs")
def test_a_second_make_unit_over_an_unchanged_tree_leaves_the_bytecode_the_first_run_wrote_for_a_test_module_untouched(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    venv = os.environ.get("VERI_VENV") or os.path.join(os.path.expanduser("~"), ".veri-tools", "venv")
    home, scratch = tmp_path / "home", tmp_path / "scratch"
    home.mkdir()
    scratch.mkdir()
    env = {"VERI_VENV": venv, "HOME": str(home), "TMPDIR": str(scratch)}

    def cached():
        return {str(p): (p.stat().st_ino, p.stat().st_mtime_ns) for p in tmp_path.rglob("test_planted_small*.pyc")}

    first = make(tree, log, "unit", **env)
    after_first = cached()
    second = make(tree, log, "unit", **env)
    assert (first[0], second[0]) == (0, 0), first[2] + second[2]
    assert after_first, "the first run left no bytecode for the planted test module"
    assert cached() == after_first


@pytest.mark.process("make unit started for real twice over a planted tree, a test module edited to same-size contents with its mtime set back between the runs")
def test_a_test_module_edited_to_same_size_contents_within_the_same_second_is_recompiled_while_an_unchanged_one_keeps_its_bytecode(tmp_path):
    original = PLANTED_CASES.split("@pytest.mark.process")[0].replace("pytest small", "alpha")
    tree, log = planted_tree(tmp_path, small=original), tmp_path / "ran.log"
    venv = os.environ.get("VERI_VENV") or os.path.join(os.path.expanduser("~"), ".veri-tools", "venv")
    home, scratch = tmp_path / "home", tmp_path / "scratch"
    home.mkdir()
    scratch.mkdir()
    env = {"VERI_VENV": venv, "HOME": str(home), "TMPDIR": str(scratch)}
    edited = tree / "skills" / "tdd" / "scripts" / "tests" / "py" / "unit" / "test_planted_small.py"

    def cached(stem):
        return {str(p): (p.stat().st_ino, p.stat().st_mtime_ns) for p in scratch.rglob(stem + "*.pyc")}

    first = make(tree, log, "unit", **env)
    mtime = edited.stat().st_mtime_ns
    unchanged = cached("conftest")
    edited.write_text(original.replace("alpha", "bravo"))
    os.utime(edited, ns=(mtime, mtime))
    second = make(tree, log, "unit", **env)
    assert (first[0], first[1], second[0], second[1]) == (0, ["alpha"], 0, ["bravo"]), first[2] + second[2]
    assert unchanged, "the first run left no bytecode for the planted conftest"
    assert cached("conftest") == unchanged
