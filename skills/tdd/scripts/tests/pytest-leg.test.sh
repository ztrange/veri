#!/usr/bin/env bash
# Unit tests for the pytest leg of `make unit` and `make test`: the `test_*.py` files under
# skills/tdd/scripts/tests/py/, run through a python3 that can import pytest.
#
# Contract under test:
#   1. With a failing `test_*.py` there, both targets run it, name the failing test in their
#      output, their recipe exits 1 (make's own `[<target>] Error 1` line on stderr, make's exit
#      non-zero) and the recipe's stdout ends `SUITES FAILED`.
#   2. With every case there passing, both targets run them, exit 0 and end `all suites green`.
#
# Run: skills/tdd/scripts/tests/pytest-leg.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

PY_DIR='skills/tdd/scripts/tests/py'


source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

work="$(scratch_dir)"

fake_pytest="$work/fake-pytest"
mkdir -p "$fake_pytest/pytest"
: > "$fake_pytest/pytest/__init__.py"
cat > "$fake_pytest/pytest/__main__.py" <<'PY'
import importlib.util
import os
import sys
import traceback

paths = [a for a in sys.argv[1:] if not a.startswith("-")] or ["."]
files = []
for p in paths:
    if os.path.isfile(p):
        files.append(p)
        continue
    for d, _, names in os.walk(p):
        files += [os.path.join(d, n) for n in sorted(names) if n.startswith("test_") and n.endswith(".py")]
failed = passed = 0
for f in sorted(files):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name in sorted(n for n in vars(mod) if n.startswith("test_") and callable(getattr(mod, n))):
        try:
            getattr(mod, name)()
            passed += 1
        except Exception:
            failed += 1
            traceback.print_exc(file=sys.stdout)
            print("FAILED %s::%s" % (f, name))
print("%d failed, %d passed" % (failed, passed))
sys.exit(1 if failed else 0)
PY

tree="$work/tree"
mkdir -p "$tree/$PY_DIR"
cp "$ROOT/Makefile" "$tree/Makefile"
ln -s "$HERE/offline" "$tree/skills/tdd/scripts/tests/offline"
ln -s "$HERE/unit-guard" "$tree/skills/tdd/scripts/tests/unit-guard"
cat > "$tree/$PY_DIR/test_leg_probe.py" <<'PY'
def test_veri_probe_fails():
    assert 1 == 2
PY

name="with a failing test_*.py under $PY_DIR and a python3 that can import pytest, make unit and make test each run it, their recipe exits 1, the output names the failing test and stdout ends SUITES FAILED"
problems=()
for target in unit test; do
  env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
    make --no-print-directory -C "$tree" "$target" > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  out="$(cat "$work/out")"
  err="$(cat "$work/err")"
  [[ "$code" != 0 ]] || problems+=("make $target: want a non-zero exit, got 0: $(flat "$out")")
  [[ "$err" =~ \[(Makefile:[0-9]+:\ )?$target\]\ Error\ 1 ]] ||
    problems+=("make $target: want make's [$target] Error 1 on stderr, got: $(flat "$err")")
  [[ "$out$err" == *test_veri_probe_fails* ]] ||
    problems+=("make $target: want the output to name test_veri_probe_fails: $(flat "$out")")
  [[ "$(tail -n 1 <<< "$out")" == 'SUITES FAILED' ]] ||
    problems+=("make $target: want stdout's last line SUITES FAILED, got: $(tail -n 1 <<< "$out")")
done
report "$name"

green="$work/green"
mkdir -p "$green/$PY_DIR"
cp "$ROOT/Makefile" "$green/Makefile"
ln -s "$HERE/offline" "$green/skills/tdd/scripts/tests/offline"
ln -s "$HERE/unit-guard" "$green/skills/tdd/scripts/tests/unit-guard"
cat > "$green/$PY_DIR/test_leg_probe.py" <<'PY'
def test_veri_probe_passes():
    assert 1 == 1
PY

name="with every pytest case under $PY_DIR passing, make unit and make test each run them, exit 0 and end all suites green"
problems=()
for target in unit test; do
  env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
    make --no-print-directory -C "$green" "$target" > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  out="$(cat "$work/out")"
  [[ "$code" == 0 ]] || problems+=("make $target: want exit 0, got $code: $(flat "$out") $(flat "$(cat "$work/err")")")
  [[ "$out" == *"1 passed"* ]] ||
    problems+=("make $target: want the pytest leg to report 1 passed, got: $(flat "$out")")
  [[ "$(tail -n 1 <<< "$out")" == 'all suites green' ]] ||
    problems+=("make $target: want stdout's last line all suites green, got: $(tail -n 1 <<< "$out")")
done
report "$name"

finish
