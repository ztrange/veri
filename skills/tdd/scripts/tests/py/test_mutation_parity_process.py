"""Medium cases for veri/mutation_parity.py: the bash suites and python3 it starts for real."""
import difflib
import importlib
import os
import subprocess
import sys
import time

import pytest

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


@pytest.mark.process("a bash suite and python3 started by failed_cases(), importing a veri module under a same-size mutation reverted within the second")
def test_1501_same_size_mutation_reverted_within_a_second_leaves_no_mutated_bytecode(tmp_path, monkeypatch, run_cli):
    for name in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX"):
        monkeypatch.delenv(name, raising=False)
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
    after = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, 'skills/tdd/scripts/veri'); import gate; print(gate.code())"],
                           cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert (code, out.strip().endswith("proven"), leftover, after.stdout.strip()) == (0, True, [], "2"), (
        "exit=%s stdout=%r stderr=%r; bytecode left %r; module imported after the tool exits answers %r, want '2'"
        % (code, out, err, leftover, after.stdout.strip()))


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
    leg_python = mutation_parity.venv_python()
    interpreter = tmp_path / "interp"
    interpreter.write_text('#!/bin/sh\nexec "%s" "$@"\n' % leg_python)
    interpreter.chmod(0o755)
    monkeypatch.setattr(mutation_parity, "venv_python", lambda: str(interpreter))

    code, out, err = run_cli(mutation_parity, [str(table)], cwd=tmp_path)

    leftover = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("gate.*.pyc"))
    after = subprocess.run([leg_python, "-c", "import sys; sys.path.insert(0, 'skills/tdd/scripts/veri'); import gate; print(gate.code())"],
                           cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert (code, out.strip().endswith("proven"), leftover, after.stdout.strip()) == (0, True, [], "2"), (
        "exit=%s stdout=%r stderr=%r; bytecode left %r; module imported after the tool exits answers %r, want '2'"
        % (code, out, err, leftover, after.stdout.strip()))


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
    interpreter = tmp_path / "interp"
    interpreter.write_text('#!/bin/sh\nexec "%s" "$@"\n' % mutation_parity.venv_python())
    interpreter.chmod(0o755)
    monkeypatch.setattr(mutation_parity, "venv_python", lambda: str(interpreter))

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
    interpreter = tmp_path / "interp"
    interpreter.write_text('#!/bin/sh\nexec "%s" "$@"\n' % mutation_parity.venv_python())
    interpreter.chmod(0o755)
    monkeypatch.setattr(mutation_parity, "venv_python", lambda: str(interpreter))

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
    interpreter = tmp_path / "interp"
    interpreter.write_text('#!/bin/sh\nexec "%s" "$@"\n' % mutation_parity.venv_python())
    interpreter.chmod(0o755)
    monkeypatch.setattr(mutation_parity, "venv_python", lambda: str(interpreter))
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
