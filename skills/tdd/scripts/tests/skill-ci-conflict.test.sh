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

name="#1287 the CI step's conflict rebase says rebase-onto-default.sh's exit code decides the next action, so nothing after it, the rebased tip's full run included, starts until it has returned, and never in the same message"
problems=()
if [[ -z "$step" ]]; then
  problems+=("$skill_md has no CI step (2. **Mark the PR ready …) to read — nothing could be checked")
else
  gate="$(conflict_paragraphs <<<"$step" | awk '{ gsub(/\. /, ".\n"); print }' | grep -i 'rebase-onto-default\.sh' | grep -i 'exit code' |
    grep -iE 'decides?[^.]*next action' | grep -i 'full' | grep -iE 'until[^.]*returned' | grep -i 'same message')"
  [[ -n "$gate" ]] ||
    problems+=("no sentence of the CI step's conflict instructions says rebase-onto-default.sh's exit code decides the next action, so nothing after it — the rebased tip's full run in particular — is started until it has returned, and never in the same message as the rebase; a conductor batching tool calls starts the full run beside a rebase that exits 3")
fi
report "$name"

name="#1458 the CI step gives a merge conflict CI reports after the metrics: push the same one-rebase path, bailing ci-conflict on a second, rather than waiting into ci-timeout"
problems=()
if [[ -z "$step" ]]; then
  problems+=("$skill_md has no CI step (2. **Mark the PR ready …) to read — nothing could be checked")
else
  late="$(conflict_paragraphs <<<"$step" | awk '{ gsub(/\. /, ".\n"); print }' | grep -F 'metrics:' | grep -i 'conflict' |
    grep -iE 'rebase' | grep -iE 'same|once' | grep -F 'ci-conflict' | grep -F 'ci-timeout')"
  [[ -n "$late" ]] ||
    problems+=("no sentence of the CI step about the metrics: push says a conflict CI reports there takes the same one-rebase path, bails ci-conflict on a second, and is not waited into ci-timeout; read literally, the conductor waits out a finished run and bails ci-timeout")
fi
report "$name"

finish
