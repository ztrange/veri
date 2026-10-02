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
#   4. When the python3 they would use is older than 3.12, both refuse before any suite runs.
#   5. requirements-dev.txt pins pytest to one exact version the Makefile never restates.
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

check_refused() {
  local target="$1"; shift
  env -u PYTHONPATH "$@" PATH="$work/no-pytest-bin:$PATH" \
    make --no-print-directory -C "$refuse" "$target" > "$work/out" 2> "$work/err" < /dev/null
  out="$(cat "$work/out")"
  err="$(cat "$work/err")"
  [[ "$err" =~ \[(Makefile:[0-9]+:\ )?$target\]\ Error\ 2 ]] ||
    problems+=("make $target: want make's [$target] Error 2 on stderr, got: $(flat "$err")")
  [[ "$out" != *'== '* ]] || problems+=("make $target: a suite ran before the refusal: $(flat "$out")")
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
  check_refused "$target" VERI_PYTEST_IMPORTABLE=0 VERI_VENV="$work/no-venv"
  [[ "$err" == *pytest* ]] || problems+=("make $target: want stderr to name pytest, got: $(flat "$err")")
  [[ "$err" == *'make install-dev'* ]] ||
    problems+=("make $target: want stderr to name make install-dev, got: $(flat "$err")")
done
report "$name"

name="when the python3 the pytest leg would use is older than 3.12 (VERI_PYTHON_VERSION=3.11.9 standing in for its answer), make unit and make test exit 2 before any suite runs, stderr naming the 3.12 floor and the version found"
problems=()
for target in unit test; do
  check_refused "$target" VERI_PYTHON_VERSION=3.11.9 VERI_VENV="$work/venv"
  [[ "$err" == *3.12* ]] || problems+=("make $target: want stderr to name the 3.12 floor, got: $(flat "$err")")
  [[ "$err" == *3.11.9* ]] || problems+=("make $target: want stderr to name the version found 3.11.9, got: $(flat "$err")")
done
report "$name"

name="requirements-dev.txt at the repository root pins pytest to one exact version, and that version appears nowhere in the Makefile"
problems=()
if [[ ! -f "$ROOT/requirements-dev.txt" ]]; then
  problems+=("want $ROOT/requirements-dev.txt to exist")
else
  pins="$(grep -E '^[[:space:]]*pytest' "$ROOT/requirements-dev.txt" || true)"
  if [[ "$pins" =~ ^pytest==([0-9]+\.[0-9]+\.[0-9]+)$ ]]; then
    version="${BASH_REMATCH[1]}"
    ! grep -nF "$version" "$ROOT/Makefile" > "$work/restated" ||
      problems+=("want the Makefile not to restate $version, got: $(flat "$(cat "$work/restated")")")
  else
    problems+=("want one line pytest==X.Y.Z, got: $(flat "$pins")")
  fi
fi
report "$name"

install="$work/install"
mkdir -p "$install/bin"
cp "$ROOT/Makefile" "$ROOT/requirements-dev.txt" "$install/"
cat > "$install/bin/python3" <<SH
#!/bin/sh
echo "\$0 \$*" >> "$install/calls"
if [ "\$1" = -m ] && [ "\$2" = venv ]; then
  for d in "\$@"; do :; done
  mkdir -p "\$d/bin"
  for exe in python3 pip; do
    printf '#!/bin/sh\necho "\$0 \$*" >> "%s"\n' "$install/calls" > "\$d/bin/\$exe"
    chmod +x "\$d/bin/\$exe"
  done
fi
SH
chmod +x "$install/bin/python3"
install_venv="$install/venv"

name="make install-dev, with VERI_VENV at a scratch path and a stub python3 recording its calls, creates the environment there when missing and installs -r requirements-dev.txt through that environment's own pip, never the PATH interpreter's; run again over the existing environment it exits 0 without recreating it"
problems=()
for run in first second; do
  : > "$install/calls"
  env -u PYTHONPATH VERI_VENV="$install_venv" PATH="$install/bin:$PATH" \
    make --no-print-directory -C "$install" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  calls="$(cat "$install/calls")"
  [[ "$code" == 0 ]] ||
    problems+=("$run run: want exit 0, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
  path_calls="$(grep -F "$install/bin/python3 " "$install/calls" || true)"
  [[ "$path_calls" != *pip* ]] ||
    problems+=("$run run: want the PATH python3 never to run pip, got: $(flat "$path_calls")")
  case "$run" in
    first)
      [[ -x "$install_venv/bin/python3" ]] ||
        problems+=("first run: want the environment created at $install_venv, got calls: $(flat "$calls")")
      venv_installs="$(grep -E "^$install_venv/bin/(python3 -m pip|pip) install( .*)? -r [^ ]*requirements-dev\.txt" "$install/calls" || true)"
      [[ -n "$venv_installs" ]] ||
        problems+=("first run: want an install -r requirements-dev.txt through $install_venv/bin's pip, got calls: $(flat "$calls")")
      ;;
    second)
      [[ "$path_calls" != *'-m venv'* ]] ||
        problems+=("second run: want the existing environment not recreated, got: $(flat "$path_calls")")
      ;;
  esac
done
report "$name"

reach="$work/reach"
make_tree "$reach"

name="under make unit, a pytest case that starts git, gh or curl fails: the recipe exits 1, stdout ends SUITES FAILED and the output names the command it tried"
problems=()
for cmd in git gh curl; do
  cat > "$reach/$PY_DIR/test_leg_probe.py" <<PY
import subprocess

def test_veri_probe_reaches():
    subprocess.run(["$cmd", "--version"], capture_output=True)
PY
  env -u VERI_VENV HOME="$work/home-empty" PYTHONPATH="$fake_pytest" \
    make --no-print-directory -C "$reach" unit > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  out="$(cat "$work/out")"
  err="$(cat "$work/err")"
  [[ "$code" != 0 ]] || problems+=("make unit, $cmd: want a non-zero exit, got 0: $(flat "$out")")
  [[ "$err" =~ \[(Makefile:[0-9]+:\ )?unit\]\ Error\ 1 ]] ||
    problems+=("make unit, $cmd: want make's [unit] Error 1 on stderr, got: $(flat "$err")")
  [[ "$(tail -n 1 <<< "$out")" == 'SUITES FAILED' ]] ||
    problems+=("make unit, $cmd: want stdout's last line SUITES FAILED, got: $(tail -n 1 <<< "$out")")
  [[ "$out$err" =~ (^|[^[:alnum:]_.-])$cmd([^[:alnum:]_.-]|$) ]] ||
    problems+=("make unit, $cmd: want the output to name $cmd, got: $(flat "$out") $(flat "$err")")
done
report "$name"

leak="$work/leak"
make_tree "$leak"
cp "$green/$PY_DIR/test_leg_probe.py" "$leak/$PY_DIR/test_leg_probe.py"
mkdir -p "$leak/skills/tdd/scripts/tests/unit"
printf '#!/usr/bin/env bash\ncurl --version > /dev/null 2>&1\necho "1 passed, 0 failed"\n' \
  > "$leak/skills/tdd/scripts/tests/unit/reach.test.sh"
chmod +x "$leak/skills/tdd/scripts/tests/unit/reach.test.sh"

name="under make unit, a command a bash suite tried is named against that suite only, never against a pytest leg that started nothing"
problems=()
env -u VERI_VENV HOME="$work/home-empty" PYTHONPATH="$fake_pytest" \
  make --no-print-directory -C "$leak" unit > "$work/out" 2> "$work/err" < /dev/null
out="$(cat "$work/out")"
[[ "$out" == *'reach.test.sh: tried the network: curl'* ]] ||
  problems+=("want the bash suite's curl named against reach.test.sh, got: $(flat "$out")")
[[ "$out" != *'pytest: tried to start'* ]] ||
  problems+=("want no command named against the pytest leg, got: $(flat "$out")")
report "$name"

finish
