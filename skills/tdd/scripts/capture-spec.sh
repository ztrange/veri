#!/usr/bin/env bash
# capture-spec.sh — write the blind spec the verifier leaves read, to stdout.
#
#     capture-spec.sh <issue-number> > .tdd/issue-<n>-spec.md
#
# The spec is the issue's body, and it gains up to two more sections. `## Bug` carries the
# report's what-happened, expected, steps to reproduce and environment. A bug's Red is a
# reproduction (ADR-0015) — the test must fail for the reason reported, not for a missing
# symbol — and the developer and the blind verifier learn what that reason is through the
# one channel that already exists, this file. The verifier is blind by construction, so a
# fact not written here is a fact it cannot have. `## Refactor`, from the `refactor` label,
# names the run kind through the same channel.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"

USAGE="capture-spec: usage: capture-spec.sh <issue-number>"
require_args 1 "$@"
n="$1"

source "$HERE/lib/github.sh"

labels="$(gh_issue_view "$n" labels)"

has_label() { grep -qxF -- "$1" <<<"$labels"; }

body="$(gh_issue_view "$n" body)"

printf '%s\n' "$body"

part() {
  awk -v want="## $1" '
    /^## / { inside = ($0 == want); next }
    inside { print }
  ' <<<"$body"
}

if has_label bug; then
  printf '\n## Bug\n'
  for heading in 'What happened' 'Expected' 'Steps to reproduce' 'Environment'; do
    printf '\n### %s\n\n' "$heading"
    part "$heading"
  done
fi

if has_label refactor; then
  printf '\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n'
fi
