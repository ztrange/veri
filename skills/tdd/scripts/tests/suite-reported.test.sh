#!/usr/bin/env bash
# Tests for scripts/suite-reported.sh — the conductor's check that a developer leaf which exited 0
# left its `SUITE:` report in `.tdd/<leaf-name>.out`.
#
# Contract under test:
#   suite-reported.sh <leaf-name>   run from a worktree, after the leaf ran through supervise.sh
#                                   → exit 2 when the leaf's captured stdout carries no `SUITE:` line.
#
# Run: scripts/tests/suite-reported.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SUPERVISE="$HERE/../supervise.sh"
RUN_LEAF="$HERE/../run-leaf.sh"
CHECK="$HERE/../suite-reported.sh"
source "$HERE/lib/harness.sh"

stubdir="$(scratch_dir)"
work="$(scratch_dir)"
claude_stub "$stubdir" "$(cat <<'STUB'
printf '{"type":"result","subtype":"success","is_error":false,"result":"%s","usage":{"input_tokens":1,"output_tokens":1}}\n' "$FAKE_RESULT"
STUB
)"
mkdir -p "$work/.tdd"
printf 'Do the step.' > "$work/prompt.txt"

name="a developer leaf that exited 0 with a final result carrying no SUITE: line makes suite-reported.sh exit 2 (#1300)"
problems=()
( cd "$work" && env CLAUDE_BIN="$stubdir/claude" FAKE_RESULT='Waiting on the make test run to exit.' \
    VERI_ISSUE=1 "$SUPERVISE" develop-diff "$RUN_LEAF" prompt.txt \
    > .tdd/develop-diff.out 2> .tdd/develop-diff.err )
leaf_code=$?
[[ "$leaf_code" == 0 ]] || problems+=("the stub leaf: want exit 0 from supervise.sh, got $leaf_code")
( cd "$work" && "$CHECK" develop-diff >/dev/null 2>&1 )
check_code=$?
[[ "$check_code" == 2 ]] ||
  problems+=("suite-reported.sh develop-diff: want exit 2, got $check_code")
report "$name"

name="a developer leaf that exited 0 with a final result carrying a SUITE: GREEN line makes suite-reported.sh exit 0 (#1300)"
problems=()
( cd "$work" && env CLAUDE_BIN="$stubdir/claude" FAKE_RESULT='SUITE: GREEN — 3 suites passed' \
    VERI_ISSUE=1 "$SUPERVISE" develop-green "$RUN_LEAF" prompt.txt \
    > .tdd/develop-green.out 2> .tdd/develop-green.err )
leaf_code=$?
[[ "$leaf_code" == 0 ]] || problems+=("the stub leaf: want exit 0 from supervise.sh, got $leaf_code")
( cd "$work" && "$CHECK" develop-green >/dev/null 2>&1 )
check_code=$?
[[ "$check_code" == 0 ]] ||
  problems+=("suite-reported.sh develop-green: want exit 0, got $check_code")
report "$name"

name="suite-reported.sh appends a report-missing event naming the leaf and SUITE on exit 2, distinct from killed-stuck, and none on exit 0 (#1300)"
problems=()
ev_work="$(scratch_dir)"
mkdir -p "$ev_work/.tdd"
printf 'Waiting on the make test run to exit.\n' > "$ev_work/.tdd/develop-diff.out"
printf 'SUITE: GREEN - 3 suites passed\n' > "$ev_work/.tdd/develop-green.out"
( cd "$ev_work" && VERI_ISSUE=1 "$CHECK" develop-green >/dev/null 2>&1 )
if [[ -s "$ev_work/.tdd/events.jsonl" ]]; then
  problems+=("exit 0 (SUITE: present) wrote events: $(cat "$ev_work/.tdd/events.jsonl")")
fi
( cd "$ev_work" && VERI_ISSUE=1 "$CHECK" develop-diff >/dev/null 2>&1 )
events="$(cat "$ev_work/.tdd/events.jsonl" 2>/dev/null)"
[[ "$events" == *'"event": "report-missing"'* ]] ||
  problems+=("exit 2: want a report-missing event, got: ${events:-<no events>}")
[[ "$events" == *'"name": "develop-diff"'* && "$events" == *'"missing": "SUITE"'* ]] ||
  problems+=("exit 2: want the event to carry name=develop-diff and missing=SUITE, got: ${events:-<no events>}")
[[ "$events" != *killed-stuck* ]] ||
  problems+=("exit 2: the event must not be killed-stuck, got: $events")
report "$name"

finish
