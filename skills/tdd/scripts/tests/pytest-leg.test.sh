#!/usr/bin/env bash
# Unit tests for the pytest leg of `make unit` and `make test`: the `test_*.py` files under
# skills/tdd/scripts/tests/py/, run through a python3 that can import pytest.
#
# Contract under test:
#   1. With a failing `test_*.py` there, both targets run it, name the failing test in their
#      output, their recipe exits 1 (make's own `[<target>] Error 1` line on stderr, make's exit
#      non-zero) and the recipe's stdout ends `SUITES FAILED`.
#   2. With every case there passing, both targets run them, exit 0 and end `all suites green`.
#   3. When no python3 they would use can import pytest, both refuse before any suite runs.
#
# Run: skills/tdd/scripts/tests/pytest-leg.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

PY_DIR='skills/tdd/scripts/tests/py'


source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

check_green() {
  local out
  out="$(cat "$work/out")"
  [[ "$code" == 0 ]] || problems+=("$1: want exit 0, got $code: $(flat "$out") $(flat "$(cat "$work/err")")")
  [[ "$out" == *"1 passed"* ]] ||
    problems+=("$1: want the pytest leg to report 1 passed, got: $(flat "$out")")
  [[ "$(tail -n 1 <<< "$out")" == 'all suites green' ]] ||
    problems+=("$1: want stdout's last line all suites green, got: $(tail -n 1 <<< "$out")")
}

make_tree() {
  mkdir -p "$1/$PY_DIR"
  cp "$ROOT/Makefile" "$1/Makefile"
  ln -s "$HERE/offline" "$1/skills/tdd/scripts/tests/offline"
  ln -s "$HERE/unit-guard" "$1/skills/tdd/scripts/tests/unit-guard"
}

stub_bash_suites() {
  local suite
  mkdir -p "$1/skills/tdd/scripts/tests/unit"
  for suite in skills/tdd/scripts/tests/unit/fast.test.sh skills/tdd/scripts/tests/slow.test.sh; do
    printf '#!/usr/bin/env bash\necho "1 passed, 0 failed"\n' > "$1/$suite"
    chmod +x "$1/$suite"
  done
}

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
make_tree "$tree"
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
make_tree "$green"
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
  check_green "make $target"
done
report "$name"

bare="$work/bare"
mkdir -p "$work/no-pytest-bin"
make_tree "$bare"
: > "$bare/$PY_DIR/helper.py"
stub_bash_suites "$bare"
printf '#!/bin/sh\necho "No module named pytest" >&2\nexit 1\n' > "$work/no-pytest-bin/python3"
chmod +x "$work/no-pytest-bin/python3"

name="with no test_*.py under $PY_DIR and no python3 that can import pytest, make unit and make test run only their bash suites, exit 0, print nothing on stderr and end all suites green"
problems=()
for target in unit test; do
  case "$target" in
    unit) want_heads='== fast.test.sh' ;;
    test) want_heads='== slow.test.sh/== fast.test.sh' ;;
  esac
  env PATH="$work/no-pytest-bin:$PATH" VERI_VENV="$work/no-venv" \
    make --no-print-directory -C "$bare" "$target" > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  out="$(cat "$work/out")"
  err="$(cat "$work/err")"
  [[ "$code" == 0 ]] || problems+=("make $target: want exit 0, got $code: $(flat "$out") $(flat "$err")")
  [[ -z "$err" ]] || problems+=("make $target: want nothing on stderr, got: $(flat "$err")")
  heads="$(grep '^== ' <<< "$out" | tr '\n' '/')"
  [[ "$heads" == "$want_heads/" ]] ||
    problems+=("make $target: want suites $want_heads/, got: $heads")
  [[ "$(tail -n 1 <<< "$out")" == 'all suites green' ]] ||
    problems+=("make $target: want stdout's last line all suites green, got: $(tail -n 1 <<< "$out")")
done
report "$name"

real_py="$(command -v python3)"
fake_venv_python() {
  mkdir -p "$1/bin"
  printf '#!/bin/sh\nPYTHONPATH="%s" exec "%s" "$@"\n' "$fake_pytest" "$real_py" > "$1/bin/python3"
  chmod +x "$1/bin/python3"
}
fake_venv_python "$work/venv"
fake_venv_python "$work/home/.veri-tools/venv"

name="with \$VERI_VENV/bin/python3 able to import pytest and the PATH python3 unable to, make unit and make test run the pytest leg with the environment's interpreter; with VERI_VENV unset it is \$HOME/.veri-tools/venv"
problems=()
for venv in set unset; do
  for target in unit test; do
    case "$venv" in
      set) venv_env=(HOME="$work/home-empty" VERI_VENV="$work/venv") ;;
      unset) venv_env=(HOME="$work/home") ;;
    esac
    env -u PYTHONPATH -u VERI_VENV "${venv_env[@]}" PATH="$work/no-pytest-bin:$PATH" \
      make --no-print-directory -C "$green" "$target" > "$work/out" 2> "$work/err" < /dev/null &&
      code=0 || code=$?
    check_green "VERI_VENV $venv, make $target"
  done
done
report "$name"

refuse="$work/refuse"
make_tree "$refuse"
cp "$green/$PY_DIR/test_leg_probe.py" "$refuse/$PY_DIR/test_leg_probe.py"
stub_bash_suites "$refuse"

name="when neither the environment's python3 nor the PATH one can import pytest (VERI_PYTEST_IMPORTABLE=0 standing in for the import), make unit and make test exit 2 before any suite runs, stderr naming pytest and make install-dev"
problems=()
for target in unit test; do
  env -u PYTHONPATH VERI_PYTEST_IMPORTABLE=0 PATH="$work/no-pytest-bin:$PATH" VERI_VENV="$work/no-venv" \
    make --no-print-directory -C "$refuse" "$target" > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  out="$(cat "$work/out")"
  err="$(cat "$work/err")"
  [[ "$err" =~ \[(Makefile:[0-9]+:\ )?$target\]\ Error\ 2 ]] ||
    problems+=("make $target: want make's [$target] Error 2 on stderr, got: $(flat "$err")")
  [[ "$err" == *pytest* ]] || problems+=("make $target: want stderr to name pytest, got: $(flat "$err")")
  [[ "$err" == *'make install-dev'* ]] ||
    problems+=("make $target: want stderr to name make install-dev, got: $(flat "$err")")
  [[ "$out" != *'== '* ]] || problems+=("make $target: a suite ran before the refusal: $(flat "$out")")
done
report "$name"

finish
