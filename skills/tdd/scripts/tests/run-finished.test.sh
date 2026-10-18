#!/usr/bin/env bash
# Tests for scripts/run-finished.sh — whether a run is safe to merge.
#
# Run: scripts/tests/run-finished.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
FINISHED="$HERE/../run-finished.sh"
source "$HERE/lib/harness.sh"

name="an issue with no run under .tdd/wt/ exits 2 and says on stderr there is no run for it"
repo="$(scratch_dir)"
git -C "$repo" init -q
mkdir -p "$repo/.tdd/wt"
err="$(cd "$repo" && "$FINISHED" 4242 2>&1 >/dev/null)" && code=0 || code=$?
if [[ "$code" != 2 ]]; then
  no "$name (want exit 2, got $code)"
elif [[ "$err" != *"no run for issue 4242"* ]]; then
  no "$name (stderr: $err)"
else
  ok
fi

finish
