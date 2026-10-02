#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md's CI step answers a conflicting PR, read as text.
#
# Contract under test:
#   1. In the step that readies the PR and reads its CI, a wait-ci.sh exit 2 whose stderr
#      names a conflict rebases onto origin/<default> through the existing rebase path —
#      the rebase verifier, the full suite, the push under a pinned lease — and waits for
#      CI again, once; a second conflict bails with cause ci-conflict.
#
# Run: scripts/tests/skill-ci-conflict.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

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

name="#688 the CI step sends a wait-ci.sh exit 2 naming a conflict through the rebase path once — rebase verifier, full suite, pinned lease, CI again — and bails ci-conflict on a second"
problems=()
step="$(ci_step)"
if [[ -z "$step" ]]; then
  problems+=("$skill_md has no CI step (2. **Mark the PR ready …) to read — nothing could be checked")
else
  text="$(conflict_paragraphs <<<"$step")"
  if [[ -z "$text" ]]; then
    problems+=("the CI step never mentions a conflict")
  else
    for want in 'wait-ci\.sh' 'exit 2' 'stderr' 'rebase-onto-default\.sh|origin/<default>' \
                'verify-rebase|rebase verifier' 'full (suite|test command)' 'lease' \
                'once' 'second conflict' 'bail' 'ci-conflict'; do
      grep -E -- "$want" > /dev/null <<<"$text" \
        || problems+=("the CI step's conflict instructions never mention /$want/")
    done
  fi
  grep -E 'event\.sh bail cause=ci-conflict' > /dev/null <<<"$step" \
    || problems+=("the CI step's commands carry no event.sh bail cause=ci-conflict")
fi
report "$name"

finish
