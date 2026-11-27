"""Medium case for the Makefile's test and unit targets: make started for real over a planted tests tree."""
import os
import shutil
import subprocess
import sys

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
BUDGET_CASE = '''import os


def test_small():
    legs = os.environ["VERI_PYTEST_LEGS"]
    entries = sorted(open(os.path.join(legs, name)).read().split("\\n")[0] for name in os.listdir(legs)
                     if name.isdigit() and name != os.environ["PLANTED_HOLDER"])
    lock = legs.rstrip("/") + "-full.lock"
    held = os.path.exists(lock) and open(lock).read() != ""
    with open(os.environ["PLANTED_RAN_LOG"], "a") as log:
        log.write("workers %s registered %s lock held %s\\n" % (os.environ.get("PYTEST_XDIST_WORKER_COUNT", "1"), entries, held))
'''
BASH_TRIPWIRE = '#!/bin/sh\nprintf "bash suite\\n" >> "$PLANTED_RAN_LOG"\necho "1 passed, 0 failed"\n'


def planted_tree(tmp_path, small=None):
    if small is None:
        small = PLANTED_CASES.split("@pytest.mark.process")[0]
    tree = tmp_path / "tree"
    scripts = tree / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(ROOT / "Makefile", tree / "Makefile")
    for name in ("veri", "lib", "prose-owed.sh"):
        (scripts / name).symlink_to(SCRIPTS / name)
    py = scripts / "tests" / "py"
    (py / "unit").mkdir(parents=True)
    (scripts / "tests" / "leg").symlink_to(SCRIPTS / "tests" / "leg")
    (py / "conftest.py").write_text(PLANTED_CONFTEST)
    (py / "unit" / "test_planted_small.py").write_text(small)
    (py / "test_planted_medium.py").write_text(PLANTED_CASES.replace("def test_small", "def test_other_small"))
    for suite in (scripts / "tests" / "planted.test.sh", scripts / "tests" / "unit" / "planted-unit.test.sh"):
        suite.parent.mkdir(exist_ok=True)
        suite.write_text(BASH_TRIPWIRE)
        suite.chmod(0o755)
    return tree


def make(tree, log, target, timeout=None, **veri):
    """(exit code, sorted cases the planted tree noted, output) of one nested make; <timeout> bounds the wait."""
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env.update({"VERI_PYTEST_WORKERS": "1", **veri})
    env["PLANTED_RAN_LOG"] = str(log)
    ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=timeout)
    return ran.returncode, sorted(log.read_text().splitlines()), ran.stdout + ran.stderr


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


# two nested make runs per case, each bounded at NESTED_MAKE_BOUND, so a hung one fails the case before its mark does
NESTED_MAKE_BOUND = 100


def _two_workers_match_serial(tmp_path, target, ran_cases, counts):
    failing = PLANTED_CASES.split("@pytest.mark.process")[0].replace('note("pytest small")', 'note("pytest small")\n    assert False')
    tree, log = planted_tree(tmp_path, small=failing), tmp_path / "ran.log"
    node = "skills/tdd/scripts/tests/py/unit/test_planted_small.py::test_small"
    serial = make(tree, log, target, timeout=NESTED_MAKE_BOUND, VERI_PYTEST_WORKERS="1")
    parallel = make(tree, log, target, timeout=NESTED_MAKE_BOUND, VERI_PYTEST_WORKERS="2")
    output = parallel[2]
    assert (parallel[0], parallel[1]) == (serial[0], serial[1]) == (2, ran_cases), output
    assert [line.startswith("FAILED " + node) for line in output.splitlines() if line.startswith("FAILED ")] == [True], output
    assert counts in output, output
    assert ("SUITES FAILED" in output, "all suites green" in output) == ("SUITES FAILED" in serial[2], False), output


@pytest.mark.timeout(240)
@pytest.mark.process("make unit started for real, with one and with two pytest workers, over a planted tree whose small case fails")
def test_make_unit_with_two_workers_passes_and_fails_the_same_cases_as_serial_and_names_a_failing_case_by_its_node_id(tmp_path):
    _two_workers_match_serial(tmp_path, "unit", ["pytest small"], "1 failed in")


@pytest.mark.timeout(240)
@pytest.mark.process("make test started for real, with one and with two pytest workers, over a planted tree whose small case fails")
def test_make_test_with_two_workers_passes_and_fails_the_same_cases_as_serial_and_names_a_failing_case_by_its_node_id(tmp_path):
    _two_workers_match_serial(tmp_path, "test", ["pytest medium", "pytest small", "pytest small"], "1 failed, 2 passed in")


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real with VERI_PYTEST_WORKERS unset, over a planted tree whose small case notes its worker count")
def test_with_no_worker_count_set_make_unit_runs_min_4_and_the_available_cores_and_make_test_one_per_available_core(tmp_path, monkeypatch):
    tree, log = planted_tree(tmp_path, small=WORKER_COUNT_CASE), tmp_path / "ran.log"
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(tmp_path / "legs"))
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    (tmp_path / "veri-test-ceiling").write_text("6\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("VERI_", "PYTEST_XDIST_"))}
    env["PLANTED_RAN_LOG"] = str(log)
    env["VERI_PYTEST_LEGS"] = str(tmp_path / "legs")
    env["VERI_TEST_CEILING_FILE"] = os.environ["VERI_TEST_CEILING_FILE"]  # the budget the case read, not the machine's record
    env["VERI_TEST_CAP_FILE"] = os.environ["VERI_TEST_CAP_FILE"]  # nor the machine's cap
    env["VERI_TEST_BUDGET_DIR"] = os.environ["VERI_TEST_BUDGET_DIR"]  # nor the machine's lane budgets
    env["VERI_TEST_LOAD_FILE"] = os.environ["VERI_TEST_LOAD_FILE"]  # nor the machine's load record
    for target, workers in (("unit", 4), ("test", 6)):
        log.write_text("")
        ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                             capture_output=True, text=True)
        noted = [line for line in log.read_text().splitlines() if line.startswith("workers ")]
        assert (target, ran.returncode, noted) == (target, 0, ["workers %d" % workers]), ran.stdout + ran.stderr


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree holding a small case, a medium case and a bash suite each, none serial-marked")
def test_make_unit_and_make_test_over_a_tree_with_no_serial_marked_case_start_one_pytest_session_each_and_no_bash_suite_unit_the_small_cases_and_test_the_small_and_medium_cases_2092(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    for target, noted in (("unit", ["pytest small"]), ("test", ["pytest medium", "pytest small", "pytest small"])):
        code, ran, output = make(tree, log, target, VERI_PYTEST_WORKERS="2")
        assert (target, code, ran, output.count("test session starts")) == (target, 0, noted, 1), output


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
    pycache = tmp_path / "pycache"

    def cached():
        code, ran, output = make(tree, log, "unit", VERI_PYCACHE=str(pycache))
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


@pytest.mark.timeout(120)
@pytest.mark.process("make -n test started for real over a planted tree whose cases log when they run")
def test_3340_make_n_test_prints_the_recipe_and_runs_no_case(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env["VERI_PYTEST_WORKERS"] = "1"
    env["PLANTED_RAN_LOG"] = str(log)

    ran = subprocess.run(["make", "-n", "-C", str(tree), "test"], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, log.read_text().splitlines()) == (0, []), ran.stdout + ran.stderr


VERI_GIT_CASE = '''import os
import subprocess


def test_small():
    subprocess.run(["git", "--version"], capture_output=True)
    with open(os.environ["PLANTED_RAN_LOG"], "a") as log:
        log.write("veri git ran\\n")
'''


@pytest.mark.timeout(120)
@pytest.mark.process("make test started for real over a planted tree holding an unmarked veri case that spawns git, named in TESTS")
def test_3340_criterion_4_an_unmarked_veri_case_that_spawns_git_named_in_tests_refuses_and_make_test_exits_non_zero(tmp_path):
    tree, log = planted_tree(tmp_path, small=VERI_GIT_CASE), tmp_path / "ran.log"
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env["VERI_PYTEST_WORKERS"] = "1"
    env["PLANTED_RAN_LOG"] = str(log)
    env["PATH"] = os.path.dirname(sys.executable) + os.pathsep + env["PATH"]
    named = "TESTS=skills/tdd/scripts/tests/py/unit/test_planted_small.py"

    ran = subprocess.run(["make", "-C", str(tree), "test", named], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode != 0, log.read_text().splitlines()) == (True, []), ran.stdout + ran.stderr


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE naming an absent directory")
def test_3966_make_unit_and_make_test_create_an_absent_prefix_with_mode_0700_and_run(tmp_path):
    tree, log, cache = planted_tree(tmp_path), tmp_path / "ran.log", tmp_path / "cache"
    unit = make(tree, log, "unit", VERI_PYCACHE=str(cache))
    mode = cache.is_dir() and oct(os.lstat(cache).st_mode & 0o777)
    full = make(tree, log, "test", VERI_PYCACHE=str(cache))
    assert (unit[0], unit[1], mode) == (0, ["pytest small"], oct(0o700)), unit[2]
    assert full[0] == 0, full[2]


def refusals_of_unit_and_test(tmp_path, cache):
    """Per target, unit then test: (exit code, cases the planted tree noted, whether the leg started, the output lines naming <cache>)."""
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    answers = []
    for target in ("unit", "test"):
        code, ran, output = make(tree, log, target, VERI_PYCACHE=str(cache))
        answers.append((code, ran, "== pytest" in output, [line for line in output.splitlines() if str(cache) in line]))
    return answers


def refusal(cache, why):
    return (2, [], False, ["veri: refusing the bytecode cache %s: %s; remove it, or set VERI_PYCACHE to a directory of your own" % (cache, why)])


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE naming a group-writable directory")
def test_3966_a_group_writable_prefix_makes_make_unit_and_make_test_exit_2_naming_it_and_the_fix_before_any_suite(tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    cache.chmod(0o770)
    assert refusals_of_unit_and_test(tmp_path, cache) == [refusal(cache, "it is group-writable")] * 2


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE naming an other-writable directory")
def test_3966_an_other_writable_prefix_makes_make_unit_and_make_test_exit_2_naming_it_and_the_fix_before_any_suite(tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    cache.chmod(0o707)
    assert refusals_of_unit_and_test(tmp_path, cache) == [refusal(cache, "it is other-writable")] * 2


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE naming a symlink to a closed directory")
def test_3966_a_prefix_that_is_a_symlink_makes_make_unit_and_make_test_exit_2_naming_it_and_the_fix_before_any_suite(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    target.chmod(0o700)
    cache = tmp_path / "cache"
    cache.symlink_to(target)
    assert refusals_of_unit_and_test(tmp_path, cache) == [refusal(cache, "it is a symlink")] * 2


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE naming /dev, a closed directory root owns")
def test_3966_a_prefix_owned_by_another_user_makes_make_unit_and_make_test_exit_2_naming_it_and_the_fix_before_any_suite(tmp_path):
    other = os.lstat("/dev")
    assert (other.st_uid != os.getuid(), other.st_mode & 0o022) == (True, 0), "the case needs /dev closed and not this user's"
    assert refusals_of_unit_and_test(tmp_path, "/dev") == [refusal("/dev", "it is owned by another user")] * 2


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE naming a closed regular file")
def test_3966_a_prefix_that_is_a_regular_file_makes_make_unit_and_make_test_exit_2_naming_it_not_a_directory(tmp_path):
    cache = tmp_path / "cache"
    cache.write_text("")
    cache.chmod(0o600)
    assert refusals_of_unit_and_test(tmp_path, cache) == [refusal(cache, "it is not a directory")] * 2


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE naming a symlink with a trailing slash")
def test_3966_a_symlink_prefix_named_with_a_trailing_slash_makes_make_unit_and_make_test_exit_2_as_a_symlink(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    target.chmod(0o700)
    cache = tmp_path / "cache"
    cache.symlink_to(target)
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    answers = []
    for name in ("unit", "test"):
        code, ran, output = make(tree, log, name, VERI_PYCACHE=str(cache) + "/")
        answers.append((code, ran, "== pytest" in output, [line for line in output.splitlines() if str(cache) in line]))
    assert answers == [refusal(cache, "it is a symlink")] * 2


def closed_cache_under(tmp_path, parent_mode):
    parent = tmp_path / "parent"
    parent.mkdir()
    cache = parent / "cache"
    cache.mkdir()
    cache.chmod(0o700)
    parent.chmod(parent_mode)
    return cache


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, VERI_PYCACHE in a parent others can write, no sticky bit")
def test_3966_a_closed_prefix_whose_parent_others_can_write_without_the_sticky_bit_makes_make_unit_and_make_test_exit_2(tmp_path):
    cache = closed_cache_under(tmp_path, 0o777)
    assert refusals_of_unit_and_test(tmp_path, cache) == [
        refusal(cache, "its parent is group- or other-writable without the sticky bit")] * 2


@pytest.mark.timeout(120)
@pytest.mark.process("make unit started for real over a planted tree, VERI_PYCACHE in a parent writable by all with the sticky bit, as /tmp")
def test_3966_a_closed_prefix_whose_parent_is_writable_by_all_with_the_sticky_bit_as_tmp_is_used(tmp_path):
    tree, log, cache = planted_tree(tmp_path), tmp_path / "ran.log", closed_cache_under(tmp_path, 0o1777)
    code, ran, output = make(tree, log, "unit", VERI_PYCACHE=str(cache))
    assert (code, ran) == (0, ["pytest small"]), output


@pytest.mark.timeout(120)
@pytest.mark.process("make unit started for real twice over a planted tree whose small case notes its worker count, the registry and the full-run lock, beside a live leg holding all workers but two")
def test_4311_make_unit_with_no_worker_count_takes_the_two_free_workers_and_registers_them_without_the_full_run_lock_and_an_exported_count_is_used_as_given_unregistered(tmp_path, monkeypatch):
    import pytest_leg
    tree, log = planted_tree(tmp_path, small=BUDGET_CASE), tmp_path / "ran.log"
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    cores = pytest_leg.worker_count(None)
    (legs / str(os.getpid())).write_text(pytest_leg.registration(max(cores - 2, 0)))
    env = {k: v for k, v in os.environ.items() if not k.startswith(("VERI_", "PYTEST_XDIST_", "PYTEST_LEG_"))}
    env.update(PLANTED_RAN_LOG=str(log), PLANTED_HOLDER=str(os.getpid()), VERI_PYTEST_LEGS=str(legs),
               VERI_TEST_CEILING_FILE=os.environ["VERI_TEST_CEILING_FILE"], VERI_TEST_CAP_FILE=os.environ["VERI_TEST_CAP_FILE"],
               VERI_TEST_BUDGET_DIR=os.environ["VERI_TEST_BUDGET_DIR"], VERI_TEST_LOAD_FILE=os.environ["VERI_TEST_LOAD_FILE"])
    noted = []
    for exported in ({}, {"VERI_PYTEST_WORKERS": "3"}):
        log.write_text("")
        ran = subprocess.run(["make", "-C", str(tree), "unit"], env={**env, **exported}, stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=NESTED_MAKE_BOUND)
        noted.append((ran.returncode, log.read_text().splitlines(), ran.stdout + ran.stderr))

    assert [(code, lines) for code, lines, _ in noted] == [
        (0, ["workers 2 registered ['2'] lock held False"]),
        (0, ["workers 3 registered [] lock held False"]),
    ], [output for _, _, output in noted]
