"""Medium cases for veri/mutation_parity.py: the bash suites it starts for real, its pytest runs in-process."""
import contextlib
import difflib
import importlib
import importlib.util
import io
import os
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest
from _pytest.pytester import Pytester

pytest_plugins = ["pytester"]

MODULE = "skills/tdd/scripts/veri/gate.py"
SUITE = """#!/bin/sh
cd "$(dirname "$0")/../skills/tdd/scripts/veri" || exit 2
pass=0; fail=0
if python3 -c 'import sys; sys.path.insert(0, "."); import gate; sys.exit(gate.code() != 2)'; then
  pass=2
else
  fail=2
  echo "FAIL - old case"
  echo "FAIL - kept case"
fi
pass=$((pass + 1))
echo "----"
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
"""


class ShortNamed:
    function = SimpleNamespace(__name__="mutation_parity")

    def __init__(self, request):
        self.request = request

    def __getattr__(self, name):
        return getattr(self.request, name)


@pytest.fixture(autouse=True)
def pytest_runs_in_process(request, tmp_path_factory, monkeypatch):
    pytester = Pytester(ShortNamed(request), tmp_path_factory, monkeypatch, _ispytest=True)
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    def run(*args):
        environ = dict(os.environ)
        os.environ.clear()
        os.environ.update(mutation_parity.no_bytecode_env())
        monkeypatch.setattr(sys, "dont_write_bytecode", True)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                result = pytester.runpytest_inprocess("-q", "-p", "no:cacheprovider", *args)
        finally:
            os.environ.clear()
            os.environ.update(environ)
        if result.ret not in (0, 1):
            raise RuntimeError(f"pytest could not run {' '.join(args)}: exit {result.ret}")
        return SimpleNamespace(returncode=result.ret, stdout="\n".join(result.outlines) + "\n")

    monkeypatch.setattr(mutation_parity, "pytest", run)


def imported_now(root):
    spec = importlib.util.spec_from_file_location("gate_after", root / MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module.code())


@pytest.mark.process("a bash suite and python3 started by failed_cases(), importing a veri module under a same-size mutation reverted within the second")
def test_1501_same_size_mutation_reverted_within_a_second_leaves_no_mutated_bytecode(tmp_path, monkeypatch, run_cli):
    for name in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    aged = time.time() - 30
    os.utime(source, (aged, aged))
    suite = tmp_path / "checks" / "gate.sh"
    suite.parent.mkdir()
    suite.write_text(SUITE)
    suite.chmod(0o755)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(["checks/gate.sh", "old case", "redundant", "kept case", str(patch)]) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    leftover = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("gate.*.pyc"))
    after = imported_now(tmp_path)
    assert (code, out.strip().endswith("proven"), leftover, after) == (0, True, [], "2"), (
        "exit=%s stdout=%r stderr=%r; bytecode left %r; module imported after the tool exits answers %r, want '2'"
        % (code, out, err, leftover, after))


PYTEST_SUITE = """import sys
sys.path.insert(0, "skills/tdd/scripts/veri")
import gate


def test_old():
    assert gate.code() == 2


def test_kept():
    assert gate.code() == 2


def test_unrelated():
    assert True
"""


@pytest.mark.process("pytest and python3 started by pytest() and node_fails(), importing a veri module under a same-size mutation reverted within the second")
def test_1501_pytest_suite_row_leaves_no_mutated_bytecode_and_unmutated_runs_read_current_source(tmp_path, monkeypatch, run_cli):
    for name in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    aged = time.time() - 30
    os.utime(source, (aged, aged))
    suite = tmp_path / "checks" / "test_gate.py"
    suite.parent.mkdir()
    suite.write_text(PYTEST_SUITE)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(["checks/test_gate.py", "checks/test_gate.py::test_old", "redundant",
                                "checks/test_gate.py::test_kept", str(patch)]) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    leftover = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("gate.*.pyc"))
    after = imported_now(tmp_path)
    assert (code, out.strip().endswith("proven"), leftover, after) == (0, True, [], "2"), (
        "exit=%s stdout=%r stderr=%r; bytecode left %r; module imported after the tool exits answers %r, want '2'"
        % (code, out, err, leftover, after))


UNCAUGHT_SUITE = PYTEST_SUITE.replace("def test_kept():\n    assert gate.code() == 2", "def test_kept():\n    assert True")


@pytest.mark.process("pytest and python3 started by pytest() and node_fails(), applying a mutation only the old case notices")
def test_1808_unproven_row_names_the_old_case_on_stderr_as_a_missing_test_and_leaves_stdout_unchanged(tmp_path, monkeypatch, run_cli):
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    suite = tmp_path / "checks" / "test_gate.py"
    suite.parent.mkdir()
    suite.write_text(UNCAUGHT_SUITE)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    row = ["checks/test_gate.py", "checks/test_gate.py::test_old", "redundant",
           "checks/test_gate.py::test_kept", str(patch)]
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(row) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    want = "MISSING_TEST: checks/test_gate.py::test_old: no kept case fails when its mutation is applied\n"
    assert (code, out, err) == (
        1, "\t".join([row[1], row[3], row[4], "unproven"]) + "\n", want)


@pytest.mark.process("a bash suite and python3 started by failed_cases(), whose old case name contains '::'")
def test_1843_bash_suite_row_whose_old_case_name_contains_double_colon_gets_a_verdict(tmp_path, monkeypatch, run_cli):
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    suite = tmp_path / "checks" / "gate.sh"
    suite.parent.mkdir()
    suite.write_text(SUITE.replace("old case", "gate::old case"))
    suite.chmod(0o755)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(["checks/gate.sh", "gate::old case", "redundant", "kept case", str(patch)]) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    assert (code, out.strip().endswith("proven")) == (0, True), (
        "exit=%s stdout=%r stderr=%r; want exit 0 and a proven verdict for a bash suite row" % (code, out, err))


@pytest.mark.process("pytest and python3 started by pytest() and node_fails(), for a .py suite row")
def test_1843_pytest_suite_row_is_still_judged_by_the_pytest_runner_and_gets_a_verdict(tmp_path, monkeypatch, run_cli):
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    suite = tmp_path / "checks" / "test_gate.py"
    suite.parent.mkdir()
    suite.write_text(PYTEST_SUITE)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(["checks/test_gate.py", "checks/test_gate.py::test_old", "redundant",
                                "checks/test_gate.py::test_kept", str(patch)]) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    assert (code, out.strip().endswith("proven")) == (0, True), (
        "exit=%s stdout=%r stderr=%r; want exit 0 and a proven verdict for a pytest suite row" % (code, out, err))


CALC_SH = 'add() { echo $(( $1 + $2 )); }\ngreet() { echo "hello $1"; }\n'
CALC_HEAD = '#!/bin/sh\n. "$(dirname "$0")/../calc.sh"\npass=0; fail=0\n'
CALC_TAIL = '''echo "----"
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
'''
PLAIN_CHECK = 'check() { if [ "$2" = "$3" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL - $1"; fi; }\n'
DIAG_CHECK = 'check() { if [ "$2" = "$3" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL - $1$4"; fi; }\n'
CALC_SUITE = CALC_HEAD + PLAIN_CHECK + '''check "adds two numbers" 5 "$(add 2 3)"
check "adds a negative" -1 "$(add 2 -3)"
check "greets by name" "hello ann" "$(greet ann)"
''' + CALC_TAIL
DIAG_SUITE = CALC_HEAD + DIAG_CHECK + '''check "adds two numbers" 5 "$(add 2 3)" " (got $(add 2 3) want 5)"
check "adds a negative" -1 "$(add 2 -3)"
check "greets by name" "hello ann" "$(greet ann)"
''' + CALC_TAIL
EXTENDS_SUITE = CALC_HEAD + PLAIN_CHECK + '''check "adds two numbers" 5 "$(add 2 3)"
check "adds two numbers, one negative" -1 "$(add 2 -3)"
check "adds a negative" -1 "$(add 2 -3)"
check "greets by name" "hello ann" "$(greet ann)"
''' + CALC_TAIL
CALC_PYTEST = '''import os
import subprocess

CALC = os.path.join(os.path.dirname(__file__), "..", "calc.sh")


def test_adds_a_negative():
    run = subprocess.run(["sh", "-c", '. "$0"; add 2 -3', CALC], capture_output=True, text=True)
    assert run.stdout.strip() == "-1"
'''
MUTATIONS = {
    "add-subtracts": [("$1 + $2", "$1 - $2")],
    "old-stays-green": [("$1 + $2", "$1 + ${2#-}")],
    "none-stays-green": [("$1 + $2", "$1 - $2"), ("hello", "bye")],
    "kept-stays-green": [("$1 + $2", "$1 + $2 + ($2 > 0)")],
}


def calc_scratch(tmp_path, monkeypatch, suites=(), pytest_files=()):
    (tmp_path / "checks").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "calc.sh").write_text(CALC_SH)
    for name, text in (("calc-suite.sh", CALC_SUITE), *suites):
        (tmp_path / "checks" / name).write_text(text)
        (tmp_path / "checks" / name).chmod(0o755)
    for name, text in pytest_files:
        (tmp_path / "tests" / name).write_text(text)
    for name, edits in MUTATIONS.items():
        mutated = CALC_SH
        for old, new in edits:
            mutated = mutated.replace(old, new)
        (tmp_path / (name + ".patch")).write_text("".join(difflib.unified_diff(
            CALC_SH.splitlines(True), mutated.splitlines(True), "a/calc.sh", "b/calc.sh")))
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")
    return mutation_parity


def run_rows(tmp_path, run_cli, mutation_parity, rows):
    table = tmp_path / "pairs.tsv"
    table.write_text("".join("\t".join(row) + "\n" for row in rows))
    return run_cli(mutation_parity, [str(table)], cwd=tmp_path)


def verdict_line(tmp_path, suite_old_kept, mutation, verdict):
    old, kept = suite_old_kept
    return "\t".join([old, kept, str(tmp_path / (mutation + ".patch")), verdict]) + "\n"


def row_of(tmp_path, suite, old, fate, kept, mutation):
    return [suite, old, fate, kept, str(tmp_path / (mutation + ".patch"))]


@pytest.mark.process("a bash suite started by failed_cases(), under a mutation the kept case catches")
def test_a_valid_mutation_the_kept_case_catches_is_reported_proven_and_exits_0(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch)

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "add-subtracts")])

    assert (code, out) == (0, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "add-subtracts", "proven")), err


@pytest.mark.process("a bash suite started by failed_cases(), whose old case's FAIL line carries a diagnostic")
def test_1436_a_row_whose_old_bash_case_fails_with_a_diagnostic_reads_proven_not_owed(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch, suites=[("diag-suite.sh", DIAG_SUITE)])

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/diag-suite.sh", "adds two numbers", "redundant", "adds a negative", "add-subtracts")])

    assert (code, out) == (0, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "add-subtracts", "proven")), err


@pytest.mark.process("a bash suite started by failed_cases(), whose kept case's FAIL line carries a diagnostic")
def test_1436_a_row_whose_kept_bash_case_fails_with_a_diagnostic_counts_as_catching_and_reads_proven(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch, suites=[("diag-suite.sh", DIAG_SUITE)])

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/diag-suite.sh", "adds a negative", "redundant", "adds two numbers", "add-subtracts")])

    assert (code, out) == (0, verdict_line(tmp_path, ("adds a negative", "adds two numbers"), "add-subtracts", "proven")), err


@pytest.mark.process("a bash suite started by failed_cases(), under a mutation the old case survives")
def test_a_mutation_that_leaves_the_old_case_green_is_not_reported_proven_though_the_kept_case_goes_red(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch)

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "old-stays-green")])

    assert not any(line.endswith("\tproven") for line in out.splitlines()), (code, out, err)


@pytest.mark.process("a bash suite started by failed_cases(), under a mutation that turns every case red")
def test_a_mutation_that_leaves_no_other_case_green_is_not_reported_proven_though_the_old_and_kept_cases_go_red(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch)

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "none-stays-green")])

    assert not any(line.endswith("\tproven") for line in out.splitlines()), (code, out, err)


@pytest.mark.process("a bash suite started by failed_cases(), under a mutation the kept case survives")
def test_a_valid_mutation_that_leaves_the_kept_case_green_is_reported_unproven_naming_the_kept_case_and_exits_1(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch)

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "kept-stays-green")])

    assert (code, out) == (1, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "kept-stays-green", "unproven")), err


@pytest.mark.process("a bash suite started by failed_cases(), under a mutation the old case survives")
def test_a_mutation_that_leaves_the_old_case_green_is_reported_owed_and_exits_1(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch)

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "old-stays-green")])

    assert (code, out) == (1, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "old-stays-green", "owed")), err


@pytest.mark.process("a bash suite started by failed_cases(), one of whose failing cases has a name extending the old case's")
def test_1436_a_fail_line_extending_the_old_cases_name_does_not_count_as_the_old_case_failing_so_the_row_reads_owed(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch, suites=[("extends-suite.sh", EXTENDS_SUITE)])

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/extends-suite.sh", "adds two numbers", "redundant", "adds a negative", "old-stays-green")])

    assert (code, out) == (1, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "old-stays-green", "owed")), err


@pytest.mark.process("a bash suite started by failed_cases(), under a mutation that turns every case red")
def test_a_mutation_that_leaves_no_other_case_of_the_suite_green_is_reported_owed_and_exits_1(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch)

    code, out, err = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "none-stays-green")])

    assert (code, out) == (1, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "none-stays-green", "owed")), err


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a row replaced by a node id")
def test_a_row_replaced_by_a_pytest_node_id_is_proven_when_the_node_goes_red_and_unproven_naming_it_when_it_stays_green(tmp_path, monkeypatch, run_cli):
    mp = calc_scratch(tmp_path, monkeypatch, pytest_files=[("test_calc.py", CALC_PYTEST)])
    node = "tests/test_calc.py::test_adds_a_negative"

    caught = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "replaced", node, "add-subtracts")])
    missed = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "replaced", node, "kept-stays-green")])

    assert (caught[:2], missed[:2]) == (
        (0, verdict_line(tmp_path, ("adds two numbers", node), "add-subtracts", "proven")),
        (1, verdict_line(tmp_path, ("adds two numbers", node), "kept-stays-green", "unproven"))), (caught, missed)


SUMS_PYTEST = '''import os
import subprocess

CALC = os.path.join(os.path.dirname(__file__), "..", "calc.sh")


def run(call):
    return subprocess.run(["sh", "-c", '. "$0"; ' + call, CALC], capture_output=True,
                          text=True).stdout.strip()


def test_adds_two_numbers():
    assert run("add 2 3") == "5"


def test_greets_by_name():
    assert run("greet ann") == "hello ann"
'''
CALC_RED_PYTEST = CALC_PYTEST.replace('"-1"', '"-2"')
SINGLE_SUITE = CALC_HEAD + PLAIN_CHECK + 'check "adds two numbers" 5 "$(add 2 3)"\n' + CALC_TAIL
NODE = "tests/test_calc.py::test_adds_a_negative"


def patch_of(tmp_path, name, mutated):
    (tmp_path / (name + ".patch")).write_text("".join(difflib.unified_diff(
        CALC_SH.splitlines(True), mutated.splitlines(True), "a/calc.sh", "b/calc.sh")))


def scratch_with(tmp_path, monkeypatch, suites=(), pytest_files=()):
    mp = calc_scratch(tmp_path, monkeypatch, suites=suites,
                      pytest_files=[("test_calc.py", CALC_PYTEST), *pytest_files])
    patch_of(tmp_path, "greet-byes", CALC_SH.replace("hello", "bye"))
    patch_of(tmp_path, "dies", CALC_SH + "exit 9\n")
    return mp


def one_row(tmp_path, run_cli, mp, suite, old, fate, kept, mutation):
    return run_rows(tmp_path, run_cli, mp, [row_of(tmp_path, suite, old, fate, kept, mutation)])


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a row whose old case is a pytest node id")
def test_a_row_whose_old_case_is_a_pytest_node_id_is_valid_when_the_node_goes_red_and_another_case_of_its_file_stays_green_and_owed_when_none_stays_green(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch, pytest_files=[("test_sums.py", SUMS_PYTEST)])
    old = "tests/test_sums.py::test_adds_two_numbers"

    valid = one_row(tmp_path, run_cli, mp, "tests/test_sums.py", old, "replaced", NODE, "add-subtracts")
    owed = one_row(tmp_path, run_cli, mp, "tests/test_sums.py", old, "replaced", NODE, "none-stays-green")

    assert (valid[:2], owed[:2]) == (
        (0, verdict_line(tmp_path, (old, NODE), "add-subtracts", "proven")),
        (1, verdict_line(tmp_path, (old, NODE), "none-stays-green", "owed"))), (valid, owed)


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a table of several rows")
def test_a_table_of_several_rows_reports_every_row_each_rows_case_run_with_only_its_own_mutation_in_place_and_exits_0_only_when_every_row_is_proven_1_when_any_is_unproven_or_owed(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch, pytest_files=[("test_sums.py", SUMS_PYTEST)])
    greets = "tests/test_sums.py::test_greets_by_name"
    suite = "checks/calc-suite.sh"

    all_proven = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, suite, "adds two numbers", "redundant", "adds a negative", "add-subtracts"),
        row_of(tmp_path, suite, "greets by name", "replaced", greets, "greet-byes")])
    mixed = run_rows(tmp_path, run_cli, mp, [
        row_of(tmp_path, suite, "greets by name", "replaced", greets, "greet-byes"),
        row_of(tmp_path, suite, "adds two numbers", "redundant", "adds a negative", "old-stays-green"),
        row_of(tmp_path, suite, "adds two numbers", "redundant", "adds a negative", "kept-stays-green")])

    assert (all_proven[:2], mixed[:2]) == (
        (0, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "add-subtracts", "proven")
         + verdict_line(tmp_path, ("greets by name", greets), "greet-byes", "proven")),
        (1, verdict_line(tmp_path, ("greets by name", greets), "greet-byes", "proven")
         + verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "old-stays-green", "owed")
         + verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "kept-stays-green", "unproven"))), (all_proven, mixed)


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a one-case old suite")
def test_1594_a_row_whose_old_suite_holds_exactly_one_case_reads_proven_when_that_suite_runs_to_its_count_line_with_the_named_case_failed_and_the_replacement_is_caught(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch, suites=[("single.sh", SINGLE_SUITE)])

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/single.sh", "adds two numbers", "replaced", NODE, "add-subtracts")

    assert (code, out) == (0, verdict_line(tmp_path, ("adds two numbers", NODE), "add-subtracts", "proven")), err


@pytest.mark.process("a bash suite started by failed_cases(), whose one-case suite dies before its count line under the mutation")
def test_1594_a_row_whose_old_suite_holds_exactly_one_case_reads_owed_when_under_the_mutation_that_suite_dies_before_its_count_line(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch, suites=[("single.sh", SINGLE_SUITE)])

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/single.sh", "adds two numbers", "replaced", NODE, "dies")

    assert (code, out) == (1, verdict_line(tmp_path, ("adds two numbers", NODE), "dies", "owed")), err


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a one-case old suite whose replacement the mutation misses")
def test_1594_a_row_whose_old_suite_holds_exactly_one_case_reads_unproven_when_that_suite_runs_to_its_count_line_with_the_named_case_failed_but_the_replacement_is_not_caught(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch, suites=[("single.sh", SINGLE_SUITE)])

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/single.sh", "adds two numbers", "replaced", NODE, "kept-stays-green")

    assert (code, out) == (1, verdict_line(tmp_path, ("adds two numbers", NODE), "kept-stays-green", "unproven")), err


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a one-case old suite already red")
def test_1596_a_row_whose_old_suite_holds_exactly_one_case_reads_unproven_and_names_the_old_case_when_that_case_already_fails_with_the_mutation_not_applied_though_the_replacement_is_caught(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch,
                      suites=[("single-red.sh", SINGLE_SUITE.replace('5 "$(add 2 3)"', '6 "$(add 2 3)"'))])

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/single-red.sh", "adds two numbers", "replaced", NODE, "add-subtracts")

    assert (code, out.strip().endswith("unproven"), "old case adds two numbers" in err) == (1, True, True), (out, err)


@pytest.mark.process("a bash suite started by failed_cases(), for a several-case old suite whose old case is already red")
def test_1596_a_row_whose_old_suite_holds_several_cases_reads_unproven_and_names_the_old_case_when_that_case_already_fails_with_the_mutation_not_applied(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch,
                      suites=[("calc-red.sh", CALC_SUITE.replace('5 "$(add 2 3)"', '6 "$(add 2 3)"'))])

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-red.sh", "adds two numbers", "redundant", "adds a negative", "add-subtracts")

    assert (code, out.strip().endswith("unproven"), "old case adds two numbers" in err) == (1, True, True), (out, err)


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a pytest replacement already red")
def test_1596_a_row_whose_pytest_replacement_already_fails_with_the_mutation_not_applied_reads_unproven_and_names_the_replacement_not_the_old_case(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch, pytest_files=[("test_calc_red.py", CALC_RED_PYTEST)])
    red = "tests/test_calc_red.py::test_adds_a_negative"

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "replaced", red, "add-subtracts")

    assert (code, out.strip().endswith("unproven"), "replacement " + red in err, "old case" in err) == (1, True, True, False), (out, err)


@pytest.mark.process("a bash suite started by failed_cases(), for a kept bash case already red")
def test_1596_a_row_whose_kept_bash_case_already_fails_with_the_mutation_not_applied_reads_unproven_and_names_the_replacement_not_the_old_case(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch,
                      suites=[("neg-red.sh", CALC_SUITE.replace('-1 "$(add 2 -3)"', '-2 "$(add 2 -3)"'))])

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/neg-red.sh", "adds two numbers", "redundant", "adds a negative", "add-subtracts")

    assert (code, out.strip().endswith("unproven"), "replacement adds a negative" in err, "old case" in err) == (1, True, True, False), (out, err)


@pytest.mark.process("a bash suite started by failed_cases(), for a several-case old suite that dies before its count line under the mutation")
def test_1596_a_row_whose_old_suite_holds_several_cases_ends_in_an_error_not_owed_when_under_the_mutation_that_suite_dies_before_its_count_line(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch)

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "dies")

    assert (code, "owed" in out.split()) == (2, False), (out, err)


NO_COUNT_SUITE = CALC_SUITE.replace('echo "$pass passed, $fail failed"\n', "")
BREAKS_COLLECTION = CALC_PYTEST + "def (:\n"


def git_in(tmp_path, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=tmp_path, check=True,
                   capture_output=True, stdin=subprocess.DEVNULL)


def committed_scratch(tmp_path, monkeypatch, suites=()):
    mp = scratch_with(tmp_path, monkeypatch, suites=suites)
    git_in(tmp_path, "init", "-q", "-b", "main")
    git_in(tmp_path, "add", "-A")
    git_in(tmp_path, "commit", "-qm", "init")
    return mp


def dirty_tree(tmp_path):
    (tmp_path / "staged.txt").write_text("staged\n")
    git_in(tmp_path, "add", "staged.txt")
    (tmp_path / "calc.sh").write_text(CALC_SH + "sub() { echo $(( $1 - $2 )); }\n")
    (tmp_path / "untracked.txt").write_text("untracked\n")


def snapshot(tmp_path):
    files = sorted(p for p in tmp_path.rglob("*") if p.is_file() and p.name != "pairs.tsv" and ".git" not in p.relative_to(tmp_path).parts[:1])
    index = subprocess.run(["git", "ls-files", "-s"], cwd=tmp_path, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL).stdout
    return index, [(str(p.relative_to(tmp_path)), p.read_bytes()) for p in files]


def breaks_collection_patch(tmp_path):
    (tmp_path / "breaks-collection.patch").write_text("".join(difflib.unified_diff(
        CALC_PYTEST.splitlines(True), BREAKS_COLLECTION.splitlines(True), "a/tests/test_calc.py", "b/tests/test_calc.py")))


def does_not_apply_patch(tmp_path):
    other = "mul() { echo $(( $1 * $2 )); }\n"
    (tmp_path / "does-not-apply.patch").write_text("".join(difflib.unified_diff(
        other.splitlines(True), other.replace("*", "/").splitlines(True), "a/calc.sh", "b/calc.sh")))


def dirty_patch(tmp_path, name, extra=""):
    before = (tmp_path / "calc.sh").read_text()
    after = before.replace("$1 + $2", "$1 - $2") + extra
    (tmp_path / (name + ".patch")).write_text("".join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True), "a/calc.sh", "b/calc.sh")))


@pytest.mark.process("a bash suite started by failed_cases() and pytest by node_fails(), for a several-case old suite whose every case the mutation fails")
def test_1594_a_row_whose_old_suite_holds_more_than_one_case_reads_owed_when_the_mutation_fails_every_case_of_that_suite_though_the_replacement_is_caught(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch)

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "replaced", NODE, "none-stays-green")

    assert (code, out) == (1, verdict_line(tmp_path, ("adds two numbers", NODE), "none-stays-green", "owed")), err


@pytest.mark.process("git apply started by check(), refusing a patch written against other content")
def test_a_row_whose_mutation_does_not_apply_to_the_tree_exits_2(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch)
    does_not_apply_patch(tmp_path)

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "does-not-apply")

    assert code == 2, (out, err)


@pytest.mark.process("a bash suite and pytest started for rows whose case cannot be run")
def test_a_row_whose_case_cannot_be_run_a_suite_path_that_does_not_exist_a_pytest_node_id_that_is_not_collected_exits_2(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch)

    missing = one_row(tmp_path, run_cli, mp, "checks/absent-suite.sh", "adds two numbers", "redundant", "adds a negative", "add-subtracts")
    uncollected = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "replaced",
                          "tests/test_calc.py::test_not_there", "add-subtracts")

    assert (missing[0], uncollected[0]) == (2, 2), (missing, uncollected)


@pytest.mark.process("git, a bash suite and pytest started against a scratch repository with a staged, an unstaged and an untracked change")
def test_after_the_pairs_check_exits_0_or_1_the_working_tree_and_the_index_are_byte_identical_to_before_it_a_staged_change_an_unstaged_change_to_a_file_the_mutation_patches_and_an_untracked_file_included(tmp_path, monkeypatch, run_cli):
    mp = committed_scratch(tmp_path, monkeypatch)
    dirty_tree(tmp_path)
    dirty_patch(tmp_path, "dirty")
    before = snapshot(tmp_path)

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "dirty")

    assert (code in (0, 1), snapshot(tmp_path) == before) == (True, True), (code, out, err)


@pytest.mark.process("a bash suite started by failed_cases(), one that never reaches its count line run unmutated")
def test_1612_a_row_whose_old_suite_dies_before_its_count_line_run_unmutated_reads_unproven_and_exits_1_with_stderr_naming_the_suite_and_saying_it_did_not_run_to_completion(tmp_path, monkeypatch, run_cli):
    mp = scratch_with(tmp_path, monkeypatch, suites=[("no-count.sh", NO_COUNT_SUITE)])

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/no-count.sh", "adds two numbers", "redundant", "adds a negative", "add-subtracts")

    assert (code, out.strip().endswith("unproven"), "checks/no-count.sh" in err, "did not run to completion" in err) == (1, True, True, True), (out, err)


@pytest.mark.process("git, a bash suite and pytest started for a row whose mutation stops its pytest replacement collecting")
def test_1612_an_exception_raised_while_a_rows_mutation_is_applied_a_pytest_replacement_the_mutation_stops_collecting_is_raised_after_the_mutation_is_reverted_so_the_tree_is_byte_identical_to_before_the_row(tmp_path, monkeypatch, run_cli):
    mp = committed_scratch(tmp_path, monkeypatch)
    breaks_collection_patch(tmp_path)
    before = snapshot(tmp_path)

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "replaced", NODE, "breaks-collection")

    assert (code, snapshot(tmp_path) == before) == (2, True), (out, err)


@pytest.mark.process("git, a bash suite and pytest started for a row that raises with its mutation applied")
def test_1612_a_row_that_raises_with_its_mutation_applied_leaves_every_file_of_the_tree_byte_identical_to_before_it_pytest_cache_included(tmp_path, monkeypatch, run_cli):
    mp = committed_scratch(tmp_path, monkeypatch)
    breaks_collection_patch(tmp_path)
    before = snapshot(tmp_path)

    code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", "adds two numbers", "replaced", NODE, "breaks-collection")

    assert (code, snapshot(tmp_path) == before, (tmp_path / ".pytest_cache").exists()) == (2, True, False), (out, err)


@pytest.mark.process("git, a bash suite and pytest started against a dirty scratch repository for rows that end in exit 2")
def test_after_the_pairs_check_exits_2_a_mutation_that_does_not_apply_a_bash_suite_that_never_reaches_its_count_line_under_the_mutation_or_a_pytest_node_id_that_is_not_collected_while_the_mutation_is_in_place_the_working_tree_and_the_index_are_byte_identical_to_before_it_a_staged_change_an_unstaged_change_and_an_untracked_file_included(tmp_path, monkeypatch, run_cli):
    mp = committed_scratch(tmp_path, monkeypatch)
    dirty_tree(tmp_path)
    dirty_patch(tmp_path, "dirty")
    dirty_patch(tmp_path, "dirty-dies", extra="exit 9\n")
    does_not_apply_patch(tmp_path)
    scenarios = {
        "does-not-apply": ("adds two numbers", "redundant", "adds a negative", "does-not-apply"),
        "dies": ("adds two numbers", "redundant", "adds a negative", "dirty-dies"),
        "uncollected": ("adds two numbers", "replaced", "tests/test_calc.py::test_not_there", "dirty"),
    }
    problems = {}

    for name, (old, fate, kept, mutation) in scenarios.items():
        before = snapshot(tmp_path)
        code, out, err = one_row(tmp_path, run_cli, mp, "checks/calc-suite.sh", old, fate, kept, mutation)
        if (code, snapshot(tmp_path) == before) != (2, True):
            problems[name] = (code, snapshot(tmp_path) == before, out, err)

    assert problems == {}


@pytest.mark.process("a bash suite and python3 started by failed_cases(), run with a VERI_* tunable set in the caller")
def test_1667_bash_suite_row_sees_no_veri_or_claude_variable_from_the_caller_except_veri_venv(tmp_path, monkeypatch, run_cli):
    monkeypatch.setenv("VERI_MODEL_REVISE", "opus")
    monkeypatch.setenv("CLAUDE_BIN", "/nonexistent")
    monkeypatch.setenv("VERI_VENV", str(tmp_path / "venv"))
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    suite = tmp_path / "checks" / "gate.sh"
    suite.parent.mkdir()
    guarded = SUITE.replace("if python3 -c", "if ! env | grep -v '^VERI_VENV=' | grep -q -E '^(VERI|CLAUDE)_' && python3 -c")
    assert guarded != SUITE
    suite.write_text(guarded)
    suite.chmod(0o755)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(["checks/gate.sh", "old case", "redundant", "kept case", str(patch)]) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    assert (code, out.strip().endswith("proven")) == (0, True), (
        "exit=%s stdout=%r stderr=%r; want the unmutated run to see no VERI_*/CLAUDE_* variable" % (code, out, err))


@pytest.mark.process("pytest and python3 started by pytest() and node_fails(), run with a VERI_* tunable set in the caller")
def test_1667_pytest_case_row_sees_no_veri_or_claude_variable_from_the_caller_except_veri_venv(tmp_path, monkeypatch, run_cli):
    monkeypatch.setenv("VERI_MODEL_REVISE", "opus")
    monkeypatch.setenv("CLAUDE_BIN", "/nonexistent")
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    suite = tmp_path / "checks" / "test_gate.py"
    suite.parent.mkdir()
    leak = ("import os\n\n\ndef leaked():\n"
            "    return sorted(k for k in os.environ if k.startswith(('VERI_', 'CLAUDE_')) and k != 'VERI_VENV')\n\n\n")
    guarded = PYTEST_SUITE.replace("\n\ndef test_old", "\n\n" + leak.rstrip("\n") + "\n\n\ndef test_old", 1)
    guarded = guarded.replace("    assert gate.code() == 2", "    assert leaked() == []\n    assert gate.code() == 2")
    assert guarded.count("assert leaked() == []") == 2
    suite.write_text(guarded)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(["checks/test_gate.py", "checks/test_gate.py::test_old", "redundant",
                                "checks/test_gate.py::test_kept", str(patch)]) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    assert (code, out.strip().endswith("proven")) == (0, True), (
        "exit=%s stdout=%r stderr=%r; want the unmutated pytest run to see no VERI_*/CLAUDE_* variable" % (code, out, err))


@pytest.mark.process("a bash suite and python3 started by failed_cases(), one proven and one owed row, run with a VERI_* tunable set in the caller")
def test_1667_proven_row_still_reports_proven_and_an_owed_row_still_exits_1_with_a_tunable_set(tmp_path, monkeypatch, run_cli):
    monkeypatch.setenv("VERI_MODEL_REVISE", "opus")
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    suite = tmp_path / "checks" / "gate.sh"
    suite.parent.mkdir()
    suite.write_text(SUITE)
    suite.chmod(0o755)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    proven = ["checks/gate.sh", "old case", "redundant", "kept case", str(patch)]
    owed = ["checks/gate.sh", "never failing case", "redundant", "kept case", str(patch)]
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(proven) + "\n" + "\t".join(owed) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    want = "\t".join([proven[1], proven[3], proven[4], "proven"]) + "\n" + "\t".join([owed[1], owed[3], owed[4], "owed"]) + "\n"
    assert (code, out) == (1, want), "exit=%s stdout=%r stderr=%r" % (code, out, err)


FAILING_OLD_SUITE = PYTEST_SUITE.replace("def test_old():\n    assert gate.code() == 2", "def test_old():\n    assert gate.code() == 3")


@pytest.mark.process("pytest and python3 started by pytest() and node_fails(), for a row whose old case already fails unmutated")
def test_1667_row_whose_unmutated_suite_already_fails_is_unproven_with_no_missing_test_line(tmp_path, monkeypatch, run_cli):
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    suite = tmp_path / "checks" / "test_gate.py"
    suite.parent.mkdir()
    suite.write_text(FAILING_OLD_SUITE)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    row = ["checks/test_gate.py", "checks/test_gate.py::test_old", "redundant",
           "checks/test_gate.py::test_kept", str(patch)]
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(row) + "\n")
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    assert (code, out, err) == (
        1, "\t".join([row[1], row[3], row[4], "unproven"]) + "\n",
        "already failing unmutated: old case checks/test_gate.py::test_old\n")


@pytest.mark.process("mutation-parity.sh started for real, forwarding its pairs-table argument and the exit code of mutation_parity.py")
def test_1983_shim_forwards_the_pairs_table_and_the_exit_code(tmp_path, monkeypatch):
    calc_scratch(tmp_path, monkeypatch)
    row = row_of(tmp_path, "checks/calc-suite.sh", "adds two numbers", "redundant", "adds a negative", "add-subtracts")
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(row) + "\n")
    shim = os.path.join(os.path.dirname(__file__), "..", "..", "mutation-parity.sh")

    run = subprocess.run([shim, str(table)], cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    assert (run.returncode, run.stdout) == (
        0, verdict_line(tmp_path, ("adds two numbers", "adds a negative"), "add-subtracts", "proven")), run.stderr


@pytest.mark.process("git apply started by check(), applying a mutation whose pytest run is in-process")
def test_1983_in_process_pytest_row_restores_the_source_and_leaves_no_mutated_module_or_bytecode(tmp_path, monkeypatch, run_cli):
    source = tmp_path / MODULE
    source.parent.mkdir(parents=True)
    source.write_text("def code():\n    return 2\n")
    original = source.read_bytes()
    suite = tmp_path / "checks" / "test_gate.py"
    suite.parent.mkdir()
    suite.write_text(PYTEST_SUITE)
    mutated = source.read_text().replace("return 2", "return 1")
    patch = tmp_path / "gate.patch"
    patch.write_text("".join(difflib.unified_diff(
        source.read_text().splitlines(True), mutated.splitlines(True), "a/" + MODULE, "b/" + MODULE)))
    table = tmp_path / "pairs.tsv"
    table.write_text("\t".join(["checks/test_gate.py", "checks/test_gate.py::test_old", "redundant",
                                "checks/test_gate.py::test_kept", str(patch)]) + "\n")
    monkeypatch.delitem(sys.modules, "gate", raising=False)
    monkeypatch.setattr(sys, "path", list(sys.path))
    importlib.invalidate_caches()
    mutation_parity = importlib.import_module("veri.mutation_parity")

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    sys.path.insert(0, str(source.parent))
    importlib.invalidate_caches()
    later = importlib.import_module("gate")
    leftover = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*.pyc"))
    assert (code, source.read_bytes(), leftover, later.code()) == (0, original, [], 2), (
        "exit=%s stderr=%r; source restored=%s; bytecode left %r; a later in-process import of the module answers %r, want 2"
        % (code, err, source.read_bytes() == original, leftover, later.code()))
