#!/usr/bin/env bash
# capture-spec.sh — write the blind spec the verifier leaves read, to stdout.
#
#     capture-spec.sh <issue-number> > .tdd/issue-<n>-spec.md
#
# The spec is the issue's body, and it gains one more section: `## Bug`, carrying the
# report's what-happened, expected, steps to reproduce and environment. A bug's Red is a
# reproduction (ADR-0015) — the test must fail for the reason reported, not for a missing
# symbol — and the developer and the blind verifier learn what that reason is through the
# one channel that already exists, this file. The verifier is blind by construction, so a
# fact not written here is a fact it cannot have.
set -euo pipefail

n="${1:-}"
if [[ -z "$n" ]]; then
  echo "capture-spec: usage: capture-spec.sh <issue-number>" >&2
  exit 2
fi

body="$(gh issue view "$n" --json body -q .body)"

printf '%s\n' "$body"

# One `## ` section of the body, heading dropped: the lines from the wanted heading to the
# next `## `. The parts are re-emitted under `### ` headings below, so the whole report sits
# inside one `## Bug` section rather than four top-level ones a reader has to collect.
part() {
  awk -v want="## $1" '
    /^## / { inside = ($0 == want); next }
    inside { print }
  ' <<<"$body"
}

printf '\n## Bug\n'
for heading in 'What happened' 'Expected' 'Steps to reproduce' 'Environment'; do
  printf '\n### %s\n\n' "$heading"
  part "$heading"
done
