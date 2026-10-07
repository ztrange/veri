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

check_failed() {
  local label="$1" target="$2"
  [[ "$code" != 0 ]] || problems+=("$label: want a non-zero exit, got 0: $(flat "$out")")
  [[ "$err" =~ \[(Makefile:[0-9]+:\ )?$target\]\ Error\ 1 ]] ||
    problems+=("$label: want make's [$target] Error 1 on stderr, got: $(flat "$err")")
  [[ "$(tail -n 1 <<< "$out")" == 'SUITES FAILED' ]] ||
    problems+=("$label: want stdout's last line SUITES FAILED, got: $(tail -n 1 <<< "$out")")
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
  mkdir -p "$1/$PY_DIR" "$1/skills/tdd/scripts/lib"
  cp "$ROOT/Makefile" "$1/Makefile"
  cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$1/skills/tdd/scripts/lib/"
  cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$1/skills/tdd/scripts/"
  cp -R "$ROOT/skills/tdd/scripts/veri" "$1/skills/tdd/scripts/"
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
  check_failed "make $target" "$target"
  [[ "$out$err" == *test_veri_probe_fails* ]] ||
    problems+=("make $target: want the output to name test_veri_probe_fails: $(flat "$out")")
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
printf '#!/bin/sh\ncase "$1" in */veri/*.py) exec "%s" "$@" ;; esac\necho "No module named pytest" >&2\nexit 1\n' "$(command -v python3)" > "$work/no-pytest-bin/python3"
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
mkdir -p "$install/bin" "$install/skills/tdd/scripts/lib"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$install/skills/tdd/scripts/lib/"
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

real_python3="$(command -v python3)"
stub_python() {
  local path="$1" version="$2"
  cat > "$path" <<SH
#!/bin/sh
echo "\$0 \$*" >> "$floor/calls"
case "\$1" in
  --version|-V) echo "Python $version" ;;
  -c) shift; exec "$real_python3" -c '
import platform, sys
v = tuple(int(n) for n in "$version".split("."))
class VersionInfo(tuple):
    major = property(lambda s: s[0])
    minor = property(lambda s: s[1])
    micro = property(lambda s: s[2])
sys.version_info = VersionInfo(v + ("final", 0))
sys.version = "$version"
platform.python_version = lambda: "$version"
platform.python_version_tuple = lambda: tuple("$version".split("."))
code = sys.argv[1]
sys.argv = ["-c"] + sys.argv[2:]
exec(code)
' "\$@" ;;
  -m)
    if [ "\$2" = venv ]; then
      for d in "\$@"; do :; done
      mkdir -p "\$d/bin"
      cp "\$0" "\$d/bin/python3"
      cp "\$0" "\$d/bin/pip"
    fi ;;
esac
SH
  chmod +x "$path"
}

floor="$work/floor"
mkdir -p "$floor/bin" "$floor/sys" "$floor/skills/tdd/scripts/lib"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$floor/skills/tdd/scripts/lib/"
cp "$ROOT/Makefile" "$ROOT/requirements-dev.txt" "$floor/"
ln -s /bin/* /usr/bin/* "$floor/sys/" 2> /dev/null
rm -f "$floor"/sys/python*
ln -sf "$(command -v bash)" "$floor/sys/bash"
stub_python "$floor/bin/python3" 3.11.15
stub_python "$floor/bin/python3.12" 3.12.4
floor_venv="$floor/venv"

name="#863: make install-dev, with the python3 on PATH at 3.11 (below veri's 3.12 floor) and python3.12 also on PATH, builds the environment at VERI_VENV with python3.12, so the environment's interpreter reports a version at or above the floor"
problems=()
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$floor_venv" PATH="$floor/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
venv_version="$("$floor_venv/bin/python3" --version 2> /dev/null || true)"
[[ "$venv_version" =~ ^Python\ 3\.(1[2-9]|[2-9][0-9])(\.|$) ]] ||
  problems+=("want $floor_venv/bin/python3 to report Python 3.12 or newer, got: '$venv_version' (calls: $(flat "$(cat "$floor/calls")"))")
report "$name"

path_venv="$floor/venv-path-line"

name="#936: make install-dev that builds a fresh environment at VERI_VENV ends its output with a line naming \$VERI_VENV/bin and telling the reader to put it first on PATH"
problems=()
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$path_venv" PATH="$floor/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
last="$(tail -n 1 "$work/out")"
[[ "$last" == *"$path_venv/bin"* && "$last" == *PATH* && "$last" == *first* ]] ||
  problems+=("want stdout's last line to name $path_venv/bin and say to put it first on PATH, got: '$last'")
report "$name"

reuse_venv="$floor/venv-reused-path-line"
mkdir -p "$reuse_venv/bin"
stub_python "$reuse_venv/bin/python3" 3.13.1

name="#936: make install-dev that reuses an existing environment at VERI_VENV meeting the floor ends its output with a line naming \$VERI_VENV/bin and telling the reader to put it first on PATH"
problems=()
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$reuse_venv" PATH="$floor/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
[[ "$(cat "$floor/calls")" != *'-m venv'* ]] ||
  problems+=("want the existing environment reused, not rebuilt, got calls: $(flat "$(cat "$floor/calls")")")
last="$(tail -n 1 "$work/out")"
[[ "$last" == *"$reuse_venv/bin"* && "$last" == *PATH* && "$last" == *first* ]] ||
  problems+=("want stdout's last line to name $reuse_venv/bin and say to put it first on PATH, got: '$last'")
report "$name"

stub_python "$floor/bin/python3.12" 3.11.9
stub_python "$floor/bin/python3.13" 3.13.1
newest_venv="$floor/venv-newest"

name="#863: make install-dev, with python3 and python3.12 on PATH both below veri's 3.12 floor and python3.13 also on PATH, builds the environment at VERI_VENV with python3.13, trying python3.13 before python3.12"
problems=()
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$newest_venv" PATH="$floor/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
venv_version="$("$newest_venv/bin/python3" --version 2> /dev/null || true)"
[[ "$venv_version" =~ ^Python\ 3\.13(\.|$) ]] ||
  problems+=("want $newest_venv/bin/python3 to report Python 3.13, got: '$venv_version'")
at_313="$(grep -n -m1 -F "/bin/python3.13 " "$floor/calls" || true)"
at_312="$(grep -n -m1 -F "/bin/python3.12 " "$floor/calls" || true)"
if [[ -z "$at_313" ]] || { [[ -n "$at_312" ]] && ((${at_312%%:*} < ${at_313%%:*})); }; then
  problems+=("want python3.13 tried before python3.12, calls: $(flat "$(cat "$floor/calls")")")
fi
report "$name"

stub_python "$floor/bin/python3" 3.12.7
current_venv="$floor/venv-current"

name="#863: make install-dev, with the python3 on PATH at 3.12 (at veri's floor) and python3.13 and python3.12 also on PATH, builds the environment at VERI_VENV with python3, as it did before the floor"
problems=()
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$current_venv" PATH="$floor/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
venv_version="$("$current_venv/bin/python3" --version 2> /dev/null || true)"
[[ "$venv_version" == "Python 3.12.7" ]] ||
  problems+=("want $current_venv/bin/python3 to report python3's Python 3.12.7, got: '$venv_version' (calls: $(flat "$(cat "$floor/calls")"))")
report "$name"

stub_python "$floor/bin/python3" 3.11.15
stub_python "$floor/bin/python3.13" 3.11.2
stub_python "$floor/bin/python3.12" 3.11.9
none_venv="$floor/venv-none"

name="#863: make install-dev, with python3, python3.13 and python3.12 on PATH all below veri's 3.12 floor, exits 2, its stderr names the floor 3.12, and no environment is created at VERI_VENV nor anything run from it"
problems=()
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$none_venv" PATH="$floor/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 2 ]] ||
  problems+=("want exit 2, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
[[ "$(cat "$work/err")" == *3.12* ]] ||
  problems+=("want stderr to name the floor 3.12, got: $(flat "$(cat "$work/err")")")
[[ ! -e "$none_venv" ]] ||
  problems+=("want nothing created at $none_venv, found: $(flat "$(ls -A "$none_venv")")")
[[ "$(cat "$work/err")" != *"$none_venv"* ]] ||
  problems+=("want the recipe to stop at the refusal, running nothing from $none_venv, got: $(flat "$(cat "$work/err")")")
report "$name"

stub_python "$floor/bin/python3" 3.12.7
old_venv="$floor/venv-old"
mkdir -p "$old_venv/bin"
stub_python "$old_venv/bin/python3" 3.11.15
stub_python "$old_venv/bin/pip" 3.11.15

name="#863: make install-dev, with an existing environment at VERI_VENV whose interpreter is 3.11 (below veri's 3.12 floor), exits 2, its stderr names the environment's path, its version and the floor, and the environment is left in place, neither used for pip install nor deleted"
problems=()
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$old_venv" PATH="$floor/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 2 ]] ||
  problems+=("want exit 2, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
err="$(cat "$work/err")"
[[ "$err" == *"$old_venv"* && "$err" == *3.11* && "$err" == *3.12* ]] ||
  problems+=("want stderr to name $old_venv, its version 3.11 and the floor 3.12, got: $(flat "$err")")
[[ -x "$old_venv/bin/python3" && -x "$old_venv/bin/pip" ]] ||
  problems+=("want the environment left in place at $old_venv, found: $(flat "$(ls -A "$old_venv/bin" 2> /dev/null)")")
old_installs="$(grep -E "^$old_venv/bin/(python3 -m pip|pip) install" "$floor/calls" || true)"
[[ -z "$old_installs" ]] ||
  problems+=("want no pip install through $old_venv, got: $(flat "$old_installs")")
report "$name"

name="#936: make install-dev refusing — no interpreter on PATH meets the floor, or the existing environment at VERI_VENV is below it — exits 2 with its current message and prints no PATH line"
problems=()
stub_python "$floor/bin/python3" 3.11.15
refused_venv="$floor/venv-refused"
for scenario in "no interpreter:$refused_venv:veri needs Python 3.12 or newer to build its environment; none of python3, python3.13, python3.12 on PATH is." \
  "old environment:$old_venv:veri needs Python 3.12 or newer; the environment at $old_venv runs Python 3.11.15. Remove it and run make install-dev again."; do
  label="${scenario%%:*}" rest="${scenario#*:}"
  venv="${rest%%:*}" message="${rest#*:}"
  env -u PYTHONPATH VERI_VENV="$venv" PATH="$floor/bin:$floor/sys" \
    "$(command -v make)" --no-print-directory -C "$floor" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
  [[ "$(cat "$work/err")" == *"$message"* ]] ||
    problems+=("$label: want stderr to carry '$message', got: $(flat "$(cat "$work/err")")")
  both="$(cat "$work/out" "$work/err")"
  [[ "$both" != *"first on PATH"* && "$both" != *"$venv/bin:"* ]] ||
    problems+=("$label: want no PATH line, got: $(flat "$both")")
done
stub_python "$floor/bin/python3" 3.12.7
report "$name"

raised="$work/raised"
mkdir -p "$raised/bin" "$raised/skills/tdd/scripts/lib"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$raised/skills/tdd/scripts/lib/"
cp "$ROOT/Makefile" "$ROOT/requirements-dev.txt" "$raised/"
stub_python "$raised/bin/python3" 3.11.15
stub_python "$raised/bin/python3.12" 3.12.4
raised_lib="$raised/skills/tdd/scripts/lib/venv-python.sh"
raised_venv="$raised/venv"

name="#863: with lib/venv-python.sh's one floor definition, VENV_FLOOR=3.12, raised to 3.13 and nothing else edited, make install-dev never tries python3.12: with python3 at 3.11 and python3.12 at 3.12 on PATH it exits 2, its stderr names the floor 3.13, and no environment is created at VERI_VENV"
problems=()
floor_lines="$(grep -c -x 'VENV_FLOOR=3\.12' "$raised_lib" || true)"
[[ "$floor_lines" == 1 ]] ||
  problems+=("want exactly one line VENV_FLOOR=3.12 in lib/venv-python.sh, found $floor_lines")
sed 's/^VENV_FLOOR=3\.12$/VENV_FLOOR=3.13/' "$raised_lib" > "$raised_lib.new" && mv "$raised_lib.new" "$raised_lib"
: > "$floor/calls"
env -u PYTHONPATH VERI_VENV="$raised_venv" PATH="$raised/bin:$floor/sys" \
  "$(command -v make)" --no-print-directory -C "$raised" install-dev > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
[[ "$code" == 2 ]] ||
  problems+=("want exit 2, got $code: $(flat "$(cat "$work/out")") $(flat "$(cat "$work/err")")")
tried_312="$(grep -F "/bin/python3.12 " "$floor/calls" || true)"
[[ -z "$tried_312" ]] ||
  problems+=("want python3.12 never tried once the floor is 3.13, got: $(flat "$tried_312")")
[[ "$(cat "$work/err")" == *3.13* ]] ||
  problems+=("want stderr to name the floor 3.13, got: $(flat "$(cat "$work/err")")")
[[ ! -e "$raised_venv" ]] ||
  problems+=("want nothing created at $raised_venv, found: $(flat "$(ls -A "$raised_venv")")")
report "$name"

leg_raised="$work/leg-raised"
make_tree "$leg_raised"
cp "$green/$PY_DIR/test_leg_probe.py" "$leg_raised/$PY_DIR/test_leg_probe.py"
leg_lib="$leg_raised/skills/tdd/scripts/lib/venv-python.sh"

name="#863: with lib/venv-python.sh's one floor definition, VENV_FLOOR=3.12, raised to 3.13 and nothing else edited, the pytest leg of make unit and make test refuses the 3.12.4 interpreter it accepted at 3.12: exit 2 before any suite runs, stderr naming the floor 3.13"
problems=()
env -u PYTHONPATH VERI_PYTHON_VERSION=3.12.4 VERI_VENV="$work/venv" \
  make --no-print-directory -C "$leg_raised" unit > "$work/out" 2> "$work/err" < /dev/null &&
  code=0 || code=$?
check_green "floor 3.12, make unit"
sed 's/^VENV_FLOOR=3\.12$/VENV_FLOOR=3.13/' "$leg_lib" > "$leg_lib.new" && mv "$leg_lib.new" "$leg_lib"
for target in unit test; do
  env -u PYTHONPATH VERI_PYTHON_VERSION=3.12.4 VERI_VENV="$work/venv" \
    make --no-print-directory -C "$leg_raised" "$target" > "$work/out" 2> "$work/err" < /dev/null &&
    code=0 || code=$?
  out="$(cat "$work/out")"
  err="$(cat "$work/err")"
  [[ "$code" != 0 && "$err" =~ \[(Makefile:[0-9]+:\ )?$target\]\ Error\ 2 ]] ||
    problems+=("floor 3.13, make $target: want make's [$target] Error 2 on stderr, got exit $code: $(flat "$err")")
  [[ "$out" != *'== '* ]] || problems+=("floor 3.13, make $target: a suite ran before the refusal: $(flat "$out")")
  [[ "$err" == *3.13* ]] || problems+=("floor 3.13, make $target: want stderr to name the floor 3.13, got: $(flat "$err")")
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
  check_failed "make unit, $cmd" unit
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

shadow="$work/shadow"
make_tree "$shadow"
cp "$green/$PY_DIR/test_leg_probe.py" "$shadow/$PY_DIR/test_leg_probe.py"
mkdir -p "$shadow/skills/tdd/scripts/tests/unit"
printf '#!/usr/bin/env bash\necho "python3 is $(command -v python3)"\necho "1 passed, 0 failed"\n' \
  > "$shadow/skills/tdd/scripts/tests/unit/which-python.test.sh"
chmod +x "$shadow/skills/tdd/scripts/tests/unit/which-python.test.sh"

name="under make unit, with \$VERI_VENV/bin holding a python3, a bash suite under tests/unit/ still finds the refusing unit-guard/python3 shim first, not the environment's interpreter"
problems=()
env -u PYTHONPATH VERI_VENV="$work/venv" \
  make --no-print-directory -C "$shadow" unit > "$work/out" 2> "$work/err" < /dev/null
out="$(cat "$work/out")"
found="$(sed -n 's/^python3 is //p' <<< "$out")"
[[ "$found" == */skills/tdd/scripts/tests/unit-guard/python3 ]] ||
  problems+=("want the bash suite to find .../unit-guard/python3 first, got: $found ($(flat "$out"))")
report "$name"


seen="$work/seen"
make_tree "$seen"
cat > "$seen/$PY_DIR/test_leg_probe.py" <<PY
import os

def test_veri_probe_sees():
    git = {os.environ.get("GIT_CONFIG_KEY_%d" % i): os.environ.get("GIT_CONFIG_VALUE_%d" % i)
           for i in range(int(os.environ.get("GIT_CONFIG_COUNT", "0")))}
    null, fd0 = os.stat("/dev/null"), os.fstat(0)
    with open("$work/seen.txt", "w") as f:
        f.write("LC_ALL=%s\n" % os.environ.get("LC_ALL"))
        f.write("stdin=%s\n" % ("/dev/null" if (fd0.st_dev, fd0.st_ino) == (null.st_dev, null.st_ino) else "other"))
        f.write("HTTP_PROXY=%s\n" % os.environ.get("HTTP_PROXY"))
        f.write("HTTPS_PROXY=%s\n" % os.environ.get("HTTPS_PROXY"))
        f.write("protocol.allow=%s\n" % git.get("protocol.allow"))
PY
printf 'not /dev/null\n' > "$work/stdin.txt"
want_seen='LC_ALL=C/stdin=/dev/null/HTTP_PROXY=http://127.0.0.1:1/HTTPS_PROXY=http://127.0.0.1:1/protocol.allow=never'

name="a pytest case run by make unit or make test sees the recipe's environment a bash suite sees: LC_ALL=C, stdin from /dev/null, HTTP_PROXY and HTTPS_PROXY at the offline proxy and git's protocol.allow=never"
problems=()
for target in unit test; do
  rm -f "$work/seen.txt"
  env -u VERI_VENV -u HTTP_PROXY -u HTTPS_PROXY -u GIT_CONFIG_COUNT HOME="$work/home-empty" \
    PYTHONPATH="$fake_pytest" LC_ALL=en_US.UTF-8 \
    make --no-print-directory -C "$seen" "$target" > "$work/out" 2> "$work/err" < "$work/stdin.txt"
  got="$(flat "$(cat "$work/seen.txt" 2> /dev/null)")"
  [[ "$got" == "$want_seen" ]] ||
    problems+=("make $target: want the pytest case to see $want_seen, got: $got ($(flat "$(cat "$work/out")"))")
done
report "$name"

scoped="$work/scoped"
make_tree "$scoped"
cp "$tree/$PY_DIR/test_leg_probe.py" "$scoped/$PY_DIR/test_leg_probe.py"
stub_bash_suites "$scoped"

name="make test TESTS=<one shell suite>, with a failing test_*.py under $PY_DIR, runs that suite and no pytest case, exits 0 and ends all suites green"
problems=()
env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
  make --no-print-directory -C "$scoped" test TESTS=skills/tdd/scripts/tests/slow.test.sh UNIT_TESTS= \
  > "$work/out" 2> "$work/err" < /dev/null && code=0 || code=$?
out="$(cat "$work/out")"
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code: $(flat "$out") $(flat "$(cat "$work/err")")")
heads="$(grep '^== ' <<< "$out" | tr '\n' '/')"
[[ "$heads" == '== slow.test.sh/' ]] || problems+=("want only == slow.test.sh/, got: $heads")
[[ "$(tail -n 1 <<< "$out")" == 'all suites green' ]] ||
  problems+=("want stdout's last line all suites green, got: $(tail -n 1 <<< "$out")")
report "$name"

cp "$green/$PY_DIR/test_leg_probe.py" "$scoped/$PY_DIR/test_named_probe.py"

name="make test TESTS=<one test_*.py under $PY_DIR>, with another failing test_*.py beside it, runs only that file through the pytest leg, exits 0 and ends all suites green"
problems=()
env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
  make --no-print-directory -C "$scoped" test TESTS="$PY_DIR/test_named_probe.py" UNIT_TESTS= \
  > "$work/out" 2> "$work/err" < /dev/null && code=0 || code=$?
out="$(cat "$work/out")"
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code: $(flat "$out") $(flat "$(cat "$work/err")")")
heads="$(grep '^== ' <<< "$out" | tr '\n' '/')"
[[ "$heads" == '== pytest/' ]] || problems+=("want only == pytest/, got: $heads")
[[ "$out" == *'0 failed, 1 passed'* ]] ||
  problems+=("want the pytest leg to report 0 failed, 1 passed, got: $(flat "$out")")
[[ "$(tail -n 1 <<< "$out")" == 'all suites green' ]] ||
  problems+=("want stdout's last line all suites green, got: $(tail -n 1 <<< "$out")")
report "$name"

name="a plain make test, with no TESTS on the command line, runs every shell suite and the full pytest leg over every test_*.py under $PY_DIR, and with one of them failing its recipe exits 1 and stdout ends SUITES FAILED"
problems=()
env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
  make --no-print-directory -C "$scoped" test > "$work/out" 2> "$work/err" < /dev/null && code=0 || code=$?
out="$(cat "$work/out")"
err="$(cat "$work/err")"
heads="$(grep '^== ' <<< "$out" | tr '\n' '/')"
[[ "$heads" == '== slow.test.sh/== fast.test.sh/== pytest/' ]] ||
  problems+=("want == slow.test.sh/== fast.test.sh/== pytest/, got: $heads")
[[ "$out" == *'1 failed, 1 passed'* ]] ||
  problems+=("want the pytest leg to report 1 failed, 1 passed, got: $(flat "$out")")
check_failed "make test" test
report "$name"

name="#899: make unit UNIT_TESTS=<one shell suite>, with a failing test_*.py under $PY_DIR, runs that suite and no pytest case, exits 0 and ends all suites green"
problems=()
env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
  make --no-print-directory -C "$scoped" unit UNIT_TESTS=skills/tdd/scripts/tests/unit/fast.test.sh \
  > "$work/out" 2> "$work/err" < /dev/null && code=0 || code=$?
out="$(cat "$work/out")"
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code: $(flat "$out") $(flat "$(cat "$work/err")")")
heads="$(grep '^== ' <<< "$out" | tr '\n' '/')"
[[ "$heads" == '== fast.test.sh/' ]] || problems+=("want only == fast.test.sh/, got: $heads")
[[ "$(tail -n 1 <<< "$out")" == 'all suites green' ]] ||
  problems+=("want stdout's last line all suites green, got: $(tail -n 1 <<< "$out")")
report "$name"

name="#899: make unit UNIT_TESTS=<one test_*.py under $PY_DIR>, with another failing test_*.py beside it, runs only that file through the pytest leg, exits 0 and ends all suites green"
problems=()
env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
  make --no-print-directory -C "$scoped" unit UNIT_TESTS="$PY_DIR/test_named_probe.py" \
  > "$work/out" 2> "$work/err" < /dev/null && code=0 || code=$?
out="$(cat "$work/out")"
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code: $(flat "$out") $(flat "$(cat "$work/err")")")
heads="$(grep '^== ' <<< "$out" | tr '\n' '/')"
[[ "$heads" == '== pytest/' ]] || problems+=("want only == pytest/, got: $heads")
[[ "$out" == *'0 failed, 1 passed'* ]] ||
  problems+=("want the pytest leg to report 0 failed, 1 passed, got: $(flat "$out")")
[[ "$(tail -n 1 <<< "$out")" == 'all suites green' ]] ||
  problems+=("want stdout's last line all suites green, got: $(tail -n 1 <<< "$out")")
report "$name"

name="#899: a plain make unit, with no UNIT_TESTS on the command line, runs every suite under tests/unit and the full pytest leg over every test_*.py under $PY_DIR, and with one of them failing its recipe exits 1 and stdout ends SUITES FAILED"
problems=()
env VERI_VENV="$work/no-venv" PYTHONPATH="$fake_pytest" \
  make --no-print-directory -C "$scoped" unit > "$work/out" 2> "$work/err" < /dev/null && code=0 || code=$?
out="$(cat "$work/out")"
err="$(cat "$work/err")"
heads="$(grep '^== ' <<< "$out" | tr '\n' '/')"
[[ "$heads" == '== fast.test.sh/== pytest/' ]] ||
  problems+=("want == fast.test.sh/== pytest/, got: $heads")
[[ "$out" == *'1 failed, 1 passed'* ]] ||
  problems+=("want the pytest leg to report 1 failed, 1 passed, got: $(flat "$out")")
check_failed "make unit" unit
report "$name"

finish
