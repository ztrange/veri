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

finish
