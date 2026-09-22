#!/usr/bin/env bash
# run-suite.sh — run ONE suite and hold it to the same count-line contract the `test` recipe
# holds every suite to (issue #418).
#
# Usage:   run-suite.sh <suite>
#
# Until this script existed, that contract lived in the Makefile and nowhere else, so it
# reached only the suites `make test`'s glob — or a `TESTS=` override — handed it. A leaf
# running one suite by itself (`bash skills/tdd/scripts/tests/<suite>.test.sh`) got no check
# at all: not the exit code, which #157 established lies — under `set -u`, which every suite
# here declares, an unbound name inside a numeric comparison kills the script, and a script
# killed that way exits with the status of the command before it, routinely 0 — and not the
# count line, which nothing read. On #415 the leaf that ran a suite that way was the blind
# verifier, the one component whose whole purpose is to establish ground truth independently.
#
# So: a suite whose last line is not `<n> passed, <m> failed` is refused here, named, however
# it exited. The refusal is exit 1 rather than 2, matching the answer the same shape gets
# through `make test`: the suite ran, and what came back about the tree under it is that it is
# not green. What a caller must never be handed is 0.
set -uo pipefail

# The call this script accepts, spelled once: the check below quotes it back. A caller who
# dropped the argument ran no suite at all, so it is exit 2 — "no answer could be obtained" —
# never the exit 1 a suite that ran and failed earns (#270).
USAGE="usage: run-suite.sh <suite>"
[[ $# -ge 1 && -n "$1" ]] || { echo "$USAGE" >&2; exit 2; }
suite="$1"

# The guard itself, fetched rather than written out here. What a count line looks like and what
# a suite that never printed one is told are the two judgements this script and the `test`
# recipe have to make identically, and a copy of them here would be a second guard: tighten the
# pattern or reword the refusal in one place and the other goes on reporting the suite it was
# handed the old way, so whether a partially-dead suite reads as green would come down to how
# the leaf invoked it — the very split #418 exists to close. So the Makefile declares both once,
# as COUNT_LINE and COUNTLESS, and its `count-line-guard` target prints them as shell
# assignments for the eval below. make is asked rather than the file parsed because the value of
# a make variable is make's to say.
#
# The repository root is this script's own grandparent's parent — skills/tdd/scripts/ is where
# it lives — so the Makefile found is the one next to the suites being run, never whichever
# directory the caller happened to be in. A root with no Makefile, or a make that cannot answer,
# is exit 2 and not exit 1: no suite has been run and no judgement about one can be reached, so
# there is no answer to give (CLAUDE.md, "Exit codes are the API").
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
eval "$(make -s --no-print-directory -C "$ROOT" count-line-guard 2>/dev/null)"
[[ -n "${COUNT_LINE:-}" && -n "${COUNTLESS:-}" ]] || {
  echo "run-suite.sh: could not read the count-line guard from $ROOT/Makefile" >&2
  exit 2
}

out="$(mktemp)"
trap 'rm -f "$out"' EXIT

# `tee` rather than a plain capture, so a slow suite's lines still appear while it runs; the
# file is read only once the suite is done. The status wanted is the suite's, not tee's, so it
# comes off PIPESTATUS. stdin is /dev/null for the reason the recipe gives: a suite that
# inherits a leaf's stdin can block on it for as long as the leaf lives.
"$suite" < /dev/null 2>&1 | tee "$out"
code=${PIPESTATUS[0]}

tail -n 1 "$out" | grep -Eq "$COUNT_LINE" || {
  # shellcheck disable=SC2059 — COUNTLESS is the Makefile's format string, not caller input.
  printf "$COUNTLESS" "$(basename "$suite")"
  exit 1
}

exit "$code"
