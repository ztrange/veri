#!/usr/bin/env bash
# run-suite.sh — run ONE suite and hold it to the same count-line contract the `test` recipe
# holds every suite to.
#
# Usage:   run-suite.sh <suite>
#
# Until this script existed, that contract lived in the Makefile and nowhere else, so it
# reached only the suites `make test`'s glob — or a `TESTS=` override — handed it. A leaf
# running one suite by itself (`bash skills/tdd/scripts/tests/<suite>.test.sh`) got no check
# at all: not the exit code, which lies — under `set -u`, which every suite
# here declares, an unbound name inside a numeric comparison kills the script, and a script
# killed that way exits with the status of the command before it, routinely 0 — and not the
# count line, which nothing read. The leaf that once ran a suite that way was the blind
# verifier, the one component whose whole purpose is to establish ground truth independently.
#
# So: a suite whose last line is not `<n> passed, <m> failed` is refused here, named, however
# it exited. The refusal is exit 1 rather than 2, matching the answer the same shape gets
# through `make test`: the suite ran, and what came back about the tree under it is that it is
# not green. What a caller must never be handed is 0.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/lib/exit-contract.sh"
USAGE="usage: run-suite.sh <suite>"
require_args 1 "$@"
suite="$1"

ROOT="$(cd "$HERE/../../.." && pwd)"
eval "$(make -s --no-print-directory -C "$ROOT" count-line-guard 2>/dev/null)"
[[ -n "${COUNT_LINE:-}" && -n "${COUNTLESS:-}" ]] || {
  echo "run-suite.sh: could not read the count-line guard from $ROOT/Makefile" >&2
  exit 2
}

out="$(mktemp)"
trap 'rm -f "$out"' EXIT

# hazard: the pipeline's status is tee's; the suite's comes off PIPESTATUS.
"$suite" < /dev/null 2>&1 | tee "$out"
code=${PIPESTATUS[0]}

tail -n 1 "$out" | grep -Eq "$COUNT_LINE" || {
  printf "$COUNTLESS" "$(basename "$suite")"
  exit 1
}

# pass-through: the caller reads the suite's own status once its count line is there.
exit "$code"
