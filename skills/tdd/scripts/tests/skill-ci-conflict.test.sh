#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md's CI step answers a conflicting PR, read as text.
#
# Contract under test:
#   1. In the step that readies the PR and reads its CI, a wait-ci.sh exit 2 whose stderr
#      names a conflict rebases onto origin/<default> through the existing rebase path —
#      the rebase verifier, the full suite, the push under a pinned lease — and waits for
#      CI again, once; a second conflict bails with cause ci-conflict.
#   2. That conflict rebase says rebase-onto-default.sh's exit code decides the next action, so
#      nothing after it — the rebased tip's full run in particular — starts until it has
#      returned, and never in the same message as the rebase.
#
# Run: scripts/tests/skill-ci-conflict.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


ci_step() {
  awk '
    /^2\. \*\*Mark the PR ready/ { inside = 1 }
    inside && /^([0-9]+\. |#)/ && !/^2\. \*\*Mark the PR ready/ { exit }
    inside' "$skill_path"
}

conflict_paragraphs() {
  awk '
    function flush() { if (para ~ /[Cc]onflict/) print para; para = "" }
    /^[[:space:]]*$/ { flush(); next }
    { para = para " " $0 }
    END { flush() }' | plain | tr -s '[:space:]' ' '
}

finish
