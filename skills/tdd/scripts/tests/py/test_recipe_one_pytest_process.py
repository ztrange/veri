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
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env.update({"VERI_PYTEST_WORKERS": "1", **veri})
    env["PLANTED_RAN_LOG"] = str(log)
    ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    return ran.returncode, sorted(log.read_text().splitlines()), ran.stdout + ran.stderr


@pytest.mark.timeout(120)
@pytest.mark.process("make test and make unit started for real over a planted tree holding a small case, a medium case and a bash suite each")
def test_make_test_and_make_unit_each_run_one_pytest_and_no_bash_suite_unit_the_small_cases_and_test_the_small_and_medium_cases(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    unit = make(tree, log, "unit")
    full = make(tree, log, "test")
    assert (unit[0], unit[1]) == (0, ["pytest small"]), unit[2]
    assert (full[0], full[1]) == (0, ["pytest medium", "pytest small", "pytest small"]), full[2]


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree whose small case fails")
def test_a_failing_case_fails_make_unit_and_make_test_with_no_bash_suite_run(tmp_path):
    failing = PLANTED_CASES.split("@pytest.mark.process")[0].replace('note("pytest small")', 'note("pytest small")\n    assert False')
    tree, log = planted_tree(tmp_path, small=failing), tmp_path / "ran.log"
    unit = make(tree, log, "unit")
    full = make(tree, log, "test")
    assert (unit[0], unit[1]) == (2, ["pytest small"]), unit[2]
    assert (full[0], full[1]) == (2, ["pytest medium", "pytest small", "pytest small"]), full[2]


@pytest.mark.timeout(60)
@pytest.mark.process("make unit started for real over a planted tree whose only unit case is medium, so its selection collects nothing")
def test_a_selection_that_collects_nothing_fails_make_unit_with_no_bash_suite_run(tmp_path):
    medium_only = PLANTED_CASES.replace("def test_small", "def _not_a_case")
    tree, log = planted_tree(tmp_path, small=medium_only), tmp_path / "ran.log"
    code, ran, output = make(tree, log, "unit")
    assert (code, ran) == (2, []), output


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real under a bash older than 5")
def test_the_bash_version_refusal_precedes_pytest_in_make_unit_and_make_test(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    for target in ("unit", "test"):
        code, ran, output = make(tree, log, target, VERI_BASH_MAJOR="4")
        assert (code, ran, "veri needs bash 5 or newer" in output) == (2, [], True), output


@pytest.mark.timeout(60)
@pytest.mark.process("make test started for real over a planted tree, naming a file and a node id together")
def test_make_test_with_tests_naming_a_file_and_a_node_id_runs_only_those_in_one_invocation(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    py = "skills/tdd/scripts/tests/py"
    targets = "%s/unit/test_planted_small.py %s/test_planted_medium.py::test_medium" % (py, py)
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env["VERI_PYTEST_WORKERS"] = "1"
    env["PLANTED_RAN_LOG"] = str(log)
    ran = subprocess.run(["make", "-C", str(tree), "test", "TESTS=" + targets], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)
    assert (ran.returncode, sorted(log.read_text().splitlines()), ran.stdout.count("== pytest")) == \
        (0, ["pytest medium", "pytest small"], 1), ran.stdout + ran.stderr


# four nested make runs, 60 s each
@pytest.mark.timeout(240)
@pytest.mark.process("make unit and make test started for real, with two pytest workers, over a planted tree whose small case fails")
@pytest.mark.serial("starts a nested pytest run that times out when every core is busy")
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
    env["VERI_PYTEST_LEGS"] = str(tmp_path / "legs")
    for target, workers in (("unit", 4), ("test", cores)):
        log.write_text("")
        ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                             capture_output=True, text=True)
        noted = [line for line in log.read_text().splitlines() if line.startswith("workers ")]
        assert (target, ran.returncode, noted) == (target, 0, ["workers %d" % workers]), ran.stdout + ran.stderr


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree holding no serial-marked case")
def test_make_unit_and_make_test_over_a_tree_with_no_serial_marked_case_start_one_pytest_session_each_2092(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    for target in ("unit", "test"):
        code, ran, output = make(tree, log, target, VERI_PYTEST_WORKERS="2")
        assert (target, code, output.count("test session starts")) == (target, 0, 1), output


@pytest.mark.timeout(60)
@pytest.mark.process("make test started for real over a planted tree, naming one real pytest file among several suites")
def test_make_test_with_tests_naming_only_real_suites_runs_exactly_those_and_exits_0_2016(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env["VERI_PYTEST_WORKERS"] = "1"
    env["PLANTED_RAN_LOG"] = str(log)
    named = "TESTS=skills/tdd/scripts/tests/py/unit/test_planted_small.py"
    ran = subprocess.run(["make", "-C", str(tree), "test", named], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)
    assert (ran.returncode, sorted(log.read_text().splitlines())) == (0, ["pytest small"]), ran.stdout + ran.stderr


@pytest.mark.timeout(60)
@pytest.mark.process("make test started for real over a planted tree, naming a missing file beside a real pytest file")
def test_make_test_with_tests_naming_a_missing_file_exits_2_names_it_and_runs_no_suite_2016(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env["VERI_PYTEST_WORKERS"] = "1"
    env["PLANTED_RAN_LOG"] = str(log)
    missing = "skills/tdd/scripts/tests/py/unit/test_typo.py"
    named = "TESTS=skills/tdd/scripts/tests/py/unit/test_planted_small.py " + missing
    ran = subprocess.run(["make", "-C", str(tree), "test", named], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)
    assert (ran.returncode, log.read_text().splitlines(), "all suites green" in ran.stdout + ran.stderr,
            missing in ran.stderr) == (2, [], False, True), ran.stdout + ran.stderr


@pytest.mark.timeout(60)
@pytest.mark.process("make test started for real over a planted tree, naming an existing directory")
def test_make_test_with_tests_naming_a_directory_exits_2_names_it_and_runs_no_suite_2016(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env["VERI_PYTEST_WORKERS"] = "1"
    env["PLANTED_RAN_LOG"] = str(log)
    directory = "skills/tdd/scripts/tests/py"
    ran = subprocess.run(["make", "-C", str(tree), "test", "TESTS=" + directory], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)
    assert (ran.returncode, log.read_text().splitlines(), "all suites green" in ran.stdout + ran.stderr,
            directory in ran.stderr) == (2, [], False, True), ran.stdout + ran.stderr


CACHE_CASE = '''import os

import planted_helper


def test_small():
    with open(os.environ["PLANTED_RAN_LOG"], "a") as log:
        log.write("pyc %s\\n" % planted_helper.__cached__)
'''


@pytest.mark.timeout(120)
@pytest.mark.process("make unit started for real twice over a planted tree whose unit case imports a plain helper module")
def test_a_second_make_unit_over_unchanged_sources_leaves_the_plain_module_pyc_the_first_run_wrote_untouched(tmp_path):
    tree, log = planted_tree(tmp_path, small=CACHE_CASE), tmp_path / "ran.log"
    (tree / "skills" / "tdd" / "scripts" / "tests" / "py" / "unit" / "planted_helper.py").write_text("VALUE = 1\n")

    def cached():
        code, ran, output = make(tree, log, "unit")
        pyc = [line.split(" ", 1)[1] for line in ran if line.startswith("pyc ")]
        stat = os.stat(pyc[0]) if pyc and os.path.exists(pyc[0]) else None
        return code, stat and (stat.st_ino, stat.st_mtime_ns, stat.st_size), output
    first, second = cached(), cached()
    assert (first[0], second[0]) == (0, 0), first[2] + second[2]
    assert first[1] is not None and second[1] == first[1], "first run's .pyc: %s; after the second run: %s\n%s" % (first[1], second[1], second[2])


MUTATION_CASE = '''import os

import planted_helper
import planted_steady


def test_small():
    with open(os.environ["PLANTED_RAN_LOG"], "a") as log:
        log.write("value %s\\n" % planted_helper.VALUE)
        log.write("steady %s\\n" % planted_steady.__cached__)
'''


@pytest.mark.timeout(120)
@pytest.mark.process("make unit started for real twice over a planted tree whose helper module is rewritten to the same size and the same mtime between the runs")
def test_a_helper_module_rewritten_within_the_second_of_the_first_runs_compile_is_seen_by_the_second_make_unit_while_an_unchanged_one_keeps_its_pyc(tmp_path):
    tree, log = planted_tree(tmp_path, small=MUTATION_CASE), tmp_path / "ran.log"
    unit = tree / "skills" / "tdd" / "scripts" / "tests" / "py" / "unit"
    helper = unit / "planted_helper.py"
    helper.write_text("VALUE = 1\n")
    (unit / "planted_steady.py").write_text("VALUE = 1\n")
    pycache = tmp_path / "pycache"
    stamp = os.stat(helper).st_mtime_ns

    def run():
        code, ran, output = make(tree, log, "unit", VERI_PYCACHE=str(pycache))
        noted = dict(line.split(" ", 1) for line in ran)
        steady = noted.get("steady")
        stat = os.stat(steady) if steady and os.path.exists(steady) else None
        return code, noted.get("value"), stat and (stat.st_ino, stat.st_mtime_ns), output
    first = run()
    helper.write_text("VALUE = 2\n")
    os.utime(helper, ns=(stamp, stamp))
    second = run()
    assert (first[0], first[1], second[0], second[1]) == (0, "1", 0, "2"), first[3] + second[3]
    assert first[2] is not None and second[2] == first[2], "unchanged helper's .pyc: %s then %s" % (first[2], second[2])
