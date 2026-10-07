#!/usr/bin/env bash
# Unit tests for the fast tier's python3 guard — skills/tdd/scripts/tests/unit-guard/python3,
# first on a suite's PATH under `make unit`.
#
# Contract under test:
#   1. A /bin/sh shim that execs python3 on a module file under skills/tdd/scripts/veri/ runs
#      that module through the real interpreter, and answers with the module's own stdout,
#      stderr and exit code.
#   2. It does so when directories with no python3 sit between the guard and the real one on PATH.
#   3. A direct python3 call — -c, a file outside veri/, no arguments — exits 1, names python3 on
#      stderr and is written to $UNIT_GUARD_LOG.
#   4. So does python3 -c or python3 with no arguments run with veri/ as the working directory.
#   5. Under make test, a suite under tests/unit/ gets the same guard — the shim's hand-off goes
#      through, a direct python3 -c is refused, named and logged — and a suite outside it gets none.
#   6. Any git call — one whose first argument is a file under veri/ included — exits 1, names git on
#      stderr and is written to $UNIT_GUARD_LOG.
#
# Run: skills/tdd/scripts/tests/unit-guard-python3.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

tree="$(scratch_dir)"
mkdir -p "$tree/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/tests"
cp -R "$ROOT/skills/tdd/scripts/tests/unit-guard" "$tree/skills/tdd/scripts/tests/"

cat > "$tree/skills/tdd/scripts/veri/probe_handoff.py" <<'PY'
import sys
print("probe-out " + " ".join(sys.argv[1:]))
print("probe-err", file=sys.stderr)
sys.exit(7)
PY
cat > "$tree/skills/tdd/scripts/probe-handoff.sh" <<'SH'
#!/bin/sh
exec python3 "$(dirname "$0")/veri/probe_handoff.py" "$@"
SH
chmod +x "$tree/skills/tdd/scripts/probe-handoff.sh"

name="under make unit's guard PATH, a shim's hand-off to a veri/ module answers with the module's stdout, stderr and exit code"
problems=()

out_file="$tree/out"
err_file="$tree/err"
PATH="$tree/skills/tdd/scripts/tests/unit-guard:$PATH" UNIT_GUARD_LOG="$tree/guard.log" \
  "$tree/skills/tdd/scripts/probe-handoff.sh" one two > "$out_file" 2> "$err_file"
code=$?
out="$(cat "$out_file")"
err="$(cat "$err_file")"

[[ "$out" == "probe-out one two" ]] ||
  problems+=("want stdout 'probe-out one two'; got: $(flat "$out")")
[[ "$err" == "probe-err" ]] ||
  problems+=("want stderr 'probe-err'; got: $(flat "$err")")
[[ "$code" == 7 ]] ||
  problems+=("want exit 7, the module's own; got: $code")

report "$name"

name="under make unit's guard PATH, a shim's hand-off reaches the real interpreter past PATH directories that hold no python3"
problems=()

mkdir -p "$tree/empty-a" "$tree/empty-b"
PATH="$tree/skills/tdd/scripts/tests/unit-guard:$tree/empty-a:$tree/empty-b:$PATH" \
  UNIT_GUARD_LOG="$tree/guard.log" \
  "$tree/skills/tdd/scripts/probe-handoff.sh" three > "$out_file" 2> "$err_file"
code=$?
out="$(cat "$out_file")"
err="$(cat "$err_file")"

[[ "$out" == "probe-out three" ]] ||
  problems+=("want stdout 'probe-out three'; got: $(flat "$out")")
[[ "$err" == "probe-err" ]] ||
  problems+=("want stderr 'probe-err'; got: $(flat "$err")")
[[ "$code" == 7 ]] ||
  problems+=("want exit 7, the module's own; got: $code")

report "$name"

name="under make unit's guard PATH, a direct python3 call — -c, a file outside veri/, no arguments — exits 1 naming python3 and is logged"
problems=()

printf 'print("outside")\n' > "$tree/outside.py"
log="$tree/direct.log"
refusal="make unit: python3 called for real; a unit suite mocks it as a shell function"
for call in "-c|print(1)" "file|$tree/outside.py" "none|"; do
  kind="${call%%|*}" arg="${call#*|}"
  case "$kind" in
    -c) argv=(-c "$arg") ;;
    file) argv=("$arg") ;;
    none) argv=() ;;
  esac
  : > "$log"
  out="$(cd "$tree" && PATH="$tree/skills/tdd/scripts/tests/unit-guard:$PATH" UNIT_GUARD_LOG="$log" \
    python3 ${argv[@]+"${argv[@]}"} 2> "$err_file" < /dev/null)"
  code=$?
  err="$(cat "$err_file")"
  logged="$(cat "$log")"
  [[ "$code" == 1 ]] ||
    problems+=("$kind: want exit 1; got: $code (stdout: $(flat "$out"))")
  [[ "$err" == "$refusal" ]] ||
    problems+=("$kind: want stderr '$refusal'; got: $(flat "$err")")
  [[ "$logged" == "python3 ${argv[*]+"${argv[*]}"} (cwd "* ]] ||
    problems+=("$kind: want a log line 'python3 ${argv[*]+"${argv[*]}"} (cwd …)'; got: $(flat "$logged")")
done

report "$name"

name="under make unit's guard PATH, a direct python3 call — -c, no arguments — run from inside veri/ exits 1 naming python3 and is logged"
problems=()

for call in "-c|print(1)" "none|"; do
  kind="${call%%|*}" arg="${call#*|}"
  case "$kind" in
    -c) argv=(-c "$arg") ;;
    none) argv=() ;;
  esac
  : > "$log"
  out="$(cd "$tree/skills/tdd/scripts/veri" &&
    PATH="$tree/skills/tdd/scripts/tests/unit-guard:$PATH" UNIT_GUARD_LOG="$log" \
    python3 ${argv[@]+"${argv[@]}"} 2> "$err_file" < /dev/null)"
  code=$?
  err="$(cat "$err_file")"
  logged="$(cat "$log")"
  [[ "$code" == 1 ]] ||
    problems+=("$kind: want exit 1; got: $code (stdout: $(flat "$out"))")
  [[ "$err" == "$refusal" ]] ||
    problems+=("$kind: want stderr '$refusal'; got: $(flat "$err")")
  [[ "$logged" == "python3 ${argv[*]+"${argv[*]}"} (cwd "* ]] ||
    problems+=("$kind: want a log line 'python3 ${argv[*]+"${argv[*]}"} (cwd …)'; got: $(flat "$logged")")
done

report "$name"

name="when the guard has no veri/ directory beside it, every python3 call — a file included — exits 1 naming python3, is logged, and never reaches the interpreter"
problems=()

bare="$(scratch_dir)"
mkdir -p "$bare/skills/tdd/scripts/tests"
cp -R "$ROOT/skills/tdd/scripts/tests/unit-guard" "$bare/skills/tdd/scripts/tests/"
printf 'print("reached-interpreter")\n' > "$bare/module.py"
for call in "file|$bare/module.py" "-c|print(\"reached-interpreter\")" "none|"; do
  kind="${call%%|*}" arg="${call#*|}"
  case "$kind" in
    -c) argv=(-c "$arg") ;;
    file) argv=("$arg") ;;
    none) argv=() ;;
  esac
  : > "$log"
  out="$(cd "$bare" && PATH="$bare/skills/tdd/scripts/tests/unit-guard:$PATH" UNIT_GUARD_LOG="$log" \
    python3 ${argv[@]+"${argv[@]}"} 2> "$err_file" < /dev/null)"
  code=$?
  err="$(cat "$err_file")"
  logged="$(cat "$log")"
  [[ "$code" == 1 ]] ||
    problems+=("$kind: want exit 1; got: $code (stdout: $(flat "$out"))")
  [[ "$err" == "$refusal" ]] ||
    problems+=("$kind: want stderr '$refusal'; got: $(flat "$err")")
  [[ "$logged" == "python3 ${argv[*]+"${argv[*]}"} (cwd "* ]] ||
    problems+=("$kind: want a log line 'python3 ${argv[*]+"${argv[*]}"} (cwd …)'; got: $(flat "$logged")")
done

report "$name"

name="under make unit's guard PATH, any git call — a file under veri/ as its first argument included — exits 1 naming git and is logged"
problems=()

git_refusal="make unit: git called for real; a unit suite mocks it as a shell function"
for call in "veri-file|$tree/skills/tdd/scripts/veri/probe_handoff.py" "status|status" "none|"; do
  kind="${call%%|*}" arg="${call#*|}"
  case "$kind" in
    none) argv=() ;;
    *) argv=("$arg") ;;
  esac
  : > "$log"
  out="$(cd "$tree" && PATH="$tree/skills/tdd/scripts/tests/unit-guard:$PATH" UNIT_GUARD_LOG="$log" \
    git ${argv[@]+"${argv[@]}"} 2> "$err_file" < /dev/null)"
  code=$?
  err="$(cat "$err_file")"
  logged="$(cat "$log")"
  [[ "$code" == 1 ]] ||
    problems+=("$kind: want exit 1; got: $code (stdout: $(flat "$out"))")
  [[ "$err" == "$git_refusal" ]] ||
    problems+=("$kind: want stderr '$git_refusal'; got: $(flat "$err")")
  [[ "$logged" == "git ${argv[*]+"${argv[*]}"} (cwd "* ]] ||
    problems+=("$kind: want a log line 'git ${argv[*]+"${argv[*]}"} (cwd …)'; got: $(flat "$logged")")
done

report "$name"

name="under make test, a suite under tests/unit/ gets the guard — hand-off through, direct python3 refused, named and logged — and a suite outside it gets none"
problems=()

mk="$(scratch_dir)"
mkdir -p "$mk/skills/tdd/scripts/tests/unit" "$mk/skills/tdd/scripts/lib" "$mk/skills/tdd/scripts/veri"
cp "$ROOT/Makefile" "$mk/Makefile"
cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$mk/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/veri" "$mk/skills/tdd/scripts/"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$mk/skills/tdd/scripts/lib/"
cp -R "$ROOT/skills/tdd/scripts/tests/offline" "$ROOT/skills/tdd/scripts/tests/unit-guard" "$mk/skills/tdd/scripts/tests/"
cp "$tree/skills/tdd/scripts/veri/probe_handoff.py" "$mk/skills/tdd/scripts/veri/"
cp "$tree/skills/tdd/scripts/probe-handoff.sh" "$mk/skills/tdd/scripts/"
cat > "$mk/skills/tdd/scripts/tests/unit/handoff.test.sh" <<'SUITE'
#!/usr/bin/env bash
"$(dirname "$0")/../../probe-handoff.sh" four > "$RECORD_DIR/handoff.out" 2> "$RECORD_DIR/handoff.err"
echo $? > "$RECORD_DIR/handoff.code"
echo "1 passed, 0 failed"
SUITE
cat > "$mk/skills/tdd/scripts/tests/unit/direct.test.sh" <<'SUITE'
#!/usr/bin/env bash
python3 -c 'print("reached-interpreter")' > "$RECORD_DIR/direct.out" 2> "$RECORD_DIR/direct.err"
echo $? > "$RECORD_DIR/direct.code"
echo "1 passed, 0 failed"
SUITE
cat > "$mk/skills/tdd/scripts/tests/outside.test.sh" <<'SUITE'
#!/usr/bin/env bash
python3 -c 'print("reached-interpreter")' > "$RECORD_DIR/outside.out" 2> "$RECORD_DIR/outside.err"
echo $? > "$RECORD_DIR/outside.code"
echo "1 passed, 0 failed"
SUITE
chmod +x "$mk/skills/tdd/scripts/tests/unit/handoff.test.sh" "$mk/skills/tdd/scripts/tests/unit/direct.test.sh" \
  "$mk/skills/tdd/scripts/tests/outside.test.sh"
records="$(scratch_dir)"
: > "$records/guard.log"

make_out="$(RECORD_DIR="$records" UNIT_GUARD_LOG="$records/guard.log" make --no-print-directory -C "$mk" test 2>&1 < /dev/null)"
make_code=$?
[[ "$make_code" == 0 ]] ||
  problems+=("want make test over the three fixture suites to exit 0; got $make_code: $(flat "$make_out")")
record() { cat "$records/$1" 2> /dev/null || printf '<no record>'; }

[[ "$(record handoff.out)" == "probe-out four" ]] ||
  problems+=("tests/unit hand-off: want stdout 'probe-out four'; got: $(flat "$(record handoff.out)")")
[[ "$(record handoff.err)" == "probe-err" ]] ||
  problems+=("tests/unit hand-off: want stderr 'probe-err'; got: $(flat "$(record handoff.err)")")
[[ "$(record handoff.code)" == 7 ]] ||
  problems+=("tests/unit hand-off: want exit 7, the module's own; got: $(record handoff.code)")

[[ "$(record direct.code)" == 1 ]] ||
  problems+=("tests/unit direct python3 -c: want exit 1; got: $(record direct.code) (stdout: $(flat "$(record direct.out)"))")
[[ "$(record direct.err)" == "$refusal" ]] ||
  problems+=("tests/unit direct python3 -c: want stderr '$refusal'; got: $(flat "$(record direct.err)")")
logged="$(cat "$records/guard.log")"
[[ "$logged" == "python3 -c print(\"reached-interpreter\") (cwd "* && "$logged" != *$'\n'* ]] ||
  problems+=("want \$UNIT_GUARD_LOG to hold the one line 'python3 -c print(\"reached-interpreter\") (cwd …)'; got: $(flat "$logged")")

[[ "$(record outside.out)" == "reached-interpreter" && "$(record outside.code)" == 0 ]] ||
  problems+=("suite outside tests/unit: want python3 -c to reach the interpreter, stdout 'reached-interpreter', exit 0; got stdout $(flat "$(record outside.out)"), exit $(record outside.code), stderr $(flat "$(record outside.err)")")

report "$name"

finish
