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
# names the run kind (#499) through the same channel.
set -euo pipefail

n="${1:-}"
if [[ -z "$n" ]]; then
  echo "capture-spec: usage: capture-spec.sh <issue-number>" >&2
  exit 2
fi

# The issue's labels, one name per line, asked once: `-q` returns the filter's output rather
# than the document, so the body is asked for on its own below — one filter answering both
# questions would have to encode the labels alongside the body, and any marker the body could
# also contain is a marker the body can forge.
labels="$(gh issue view "$n" --json labels -q '.labels[].name')"

# has_label <name> — whether the issue carries that label, matched as a whole name.
has_label() { grep -qxF -- "$1" <<<"$labels"; }

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

# No label, no section: an issue that reports no bug has no reproduction to describe, and a
# `## Bug` heading over four empty parts would tell the blind verifier there is one.
if has_label bug; then
  printf '\n## Bug\n'
  for heading in 'What happened' 'Expected' 'Steps to reproduce' 'Environment'; do
    printf '\n### %s\n\n' "$heading"
    part "$heading"
  done
fi

# No label, no section, for the same reason: the section tells the verifier the run kind, and
# an issue that is not a refactor must not be read as one. The kind (#499) reaches the blind
# verifier the way the bug report does: through this file, the one channel it reads, rather
# than through a new parameter that could carry the developer's reasoning.
if has_label refactor; then
  printf '\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n'
fi
