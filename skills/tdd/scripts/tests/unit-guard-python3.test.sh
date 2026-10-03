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

finish
