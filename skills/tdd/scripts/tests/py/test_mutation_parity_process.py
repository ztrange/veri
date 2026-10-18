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
