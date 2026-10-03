#!/usr/bin/env bash
# Unit tests for the fast tier's python3 guard — skills/tdd/scripts/tests/unit-guard/python3,
# first on a suite's PATH under `make unit`.
#
# Contract under test:
#   1. A /bin/sh shim that execs python3 on a module file under skills/tdd/scripts/veri/ runs
#      that module through the real interpreter, and answers with the module's own stdout,
#      stderr and exit code.
#   2. It does so when directories with no python3 sit between the guard and the real one on PATH.
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

finish
