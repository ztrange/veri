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

name="#1458 the block run after the metrics: push bails nothing on a conflict exit 2 the first time and ci-conflict, never ci-timeout, once .tdd/ci-conflict-rebased exists"
problems=()
block="$(awk '
  /^[[:space:]]*\$S\/push-branch\.sh[[:space:]]*$/ { after = 1; next }
  after && /\$S\/refactor-owed\.sh render/ { exit }
  after && /\$S\/wait-ci\.sh/ { on = 1 }
  on' <<<"$step" | sed -e 's/<n>/1458/g' -e 's|<pr-url>|https://example.test/pull/1|g')"
if [[ -z "$block" ]]; then
  problems+=("no wait-ci.sh line between \$S/push-branch.sh and \$S/refactor-owed.sh render in the CI step — nothing could be run")
else
  bin="$(scratch_dir)"
  printf '#!/bin/sh\necho "PR conflicts with its base branch" >&2\nexit 2\n' > "$bin/wait-ci.sh"
  printf '#!/bin/sh\necho "$*" >> events.log\n' > "$bin/event.sh"
  printf '#!/bin/sh\necho "$1"\n' > "$bin/classify-bail.sh"
  printf '#!/bin/sh\nexit 0\n' > "$bin/ledger-steps.sh"
  printf '#!/bin/sh\nexit 0\n' > "$bin/gh"
  chmod +x "$bin"/*
  for marked in no yes; do
    work="$(scratch_dir)"
    git -C "$work" init -q
    git -C "$work" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
    mkdir "$work/.tdd"
    [[ "$marked" = yes ]] && : > "$work/.tdd/ci-conflict-rebased"
    (cd "$work" && S="$bin" PATH="$bin:$PATH" bash -c "$block" > /dev/null 2>&1)
    got="$(cat "$work/events.log" 2> /dev/null)"
    if [[ "$marked" = no ]]; then
      [[ "$got" != *bail* ]] ||
        problems+=("first conflict exit 2 after the metrics: push recorded a bail: $got")
    else
      [[ "$got" == "bail cause=ci-conflict classification=ci-conflict" ]] ||
        problems+=("second conflict exit 2 after the metrics: push recorded [$got], not bail cause=ci-conflict")
    fi
  done
fi
report "$name"

finish
