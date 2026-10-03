#!/usr/bin/env bash
# Unit tests for scripts/push-branch.sh — the script sourced, never executed, with every
# command it shells out to mocked as a same-named shell function.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/push-branch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PUSH="$HERE/../../push-branch.sh"
source "$HERE/../lib/harness.sh"
scratch="$(scratch_dir)"

show_run() {  # show_run <exit> <stdout-file> <stderr-file> — print what a failing case got
  echo "    exit $1"; echo "    stdout: $(printf '%q' "$(cat "$2")")"
  echo "    stderr: $(printf '%q' "$(cat "$3")")"
}

name="executed directly, push-branch.sh keeps its CLI contract: VERI_PUSH_RETRIES=x prints nothing on stdout, one exact stderr line, and exits 2"
out="$scratch/out" err="$scratch/err"
VERI_PUSH_RETRIES=x VERI_PUSH_BACKOFF=0 "$PUSH" > "$out" 2> "$err"
rc=$?
want_err="push-branch.sh: VERI_PUSH_RETRIES must be a non-negative integer, got 'x'"
if [[ "$rc" -ne 2 || -s "$out" || "$(cat "$err")" != "$want_err" ]]; then
  no "$name (want exit 2, empty stdout, stderr '$want_err'):"
  show_run "$rc" "$out" "$err"
else
  ok
fi

finish
