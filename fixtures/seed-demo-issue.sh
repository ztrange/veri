#!/usr/bin/env bash
# Seed the single-criterion fixture issue used to demo the veri walking skeleton.
#
# Creates one GitHub issue, with exactly one acceptance criterion, on the repo you
# run it against. Pair it with fixtures/demo-project/ as the target codebase, then
# run `/solve-issue <n>` against the printed issue number.
#
# Usage:
#   fixtures/seed-demo-issue.sh            # seed on the current repo's origin
#   GH_REPO=owner/name fixtures/seed-demo-issue.sh   # seed on a specific repo
#
# Requires an authenticated `gh`.
set -euo pipefail

repo_args=()
if [[ -n "${GH_REPO:-}" ]]; then
  repo_args=(--repo "$GH_REPO")
fi

title="Demo: add a slugify(text) function"

body=$(cat <<'EOF'
## What to build

Add a `slugify(text)` function to the `slugify` package that turns an arbitrary
string into a URL-friendly slug.

Behavior: lowercase the text, replace any run of non-alphanumeric characters with a
single hyphen, and strip leading/trailing hyphens. For example,
`slugify("Hello, World!")` returns `"hello-world"`.

## Acceptance criteria

- [ ] `slugify("Hello, World!")` returns `"hello-world"`

## Notes

This is a seeded single-criterion fixture for demoing the veri walking skeleton.
Run `/solve-issue <this-issue-number>` against the `fixtures/demo-project/` codebase.
EOF
)

gh issue create "${repo_args[@]}" \
  --title "$title" \
  --body "$body"
