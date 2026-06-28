#!/usr/bin/env bash
# Seed the MULTI-criterion fixture issue used to demo the loops + ledger rung (#6).
#
# Creates one GitHub issue with several acceptance criteria that triangulate toward a
# general `slugify` — each criterion is one cycle's worth, so the conductor plans a
# multi-step ledger and loops the cycles until all are covered. Pair it with
# fixtures/demo-project/ as the target codebase, then run `/solve-issue <n>`.
#
# Usage:
#   fixtures/seed-demo-multi-issue.sh            # seed on the current repo's origin
#   GH_REPO=owner/name fixtures/seed-demo-multi-issue.sh   # seed on a specific repo
#
# Requires an authenticated `gh`.
set -euo pipefail

repo_args=()
if [[ -n "${GH_REPO:-}" ]]; then
  repo_args=(--repo "$GH_REPO")
fi

title="Demo (multi): add a general slugify(text) function"

body=$(cat <<'EOF'
## What to build

Add a `slugify(text)` function to the `slugify` package that turns an arbitrary string
into a URL-friendly slug. The behavior is specified as several criteria below; each is one
TDD cycle's worth, and together they triangulate toward the general implementation (no
single criterion should be satisfiable by hard-coding — later criteria force generality).

## Acceptance criteria

- [ ] `slugify("Hello")` returns `"hello"` (lowercases the text)
- [ ] `slugify("Hello World")` returns `"hello-world"` (spaces become single hyphens)
- [ ] `slugify("Hello, World!")` returns `"hello-world"` (runs of non-alphanumerics collapse to one hyphen)
- [ ] `slugify("--Hi--")` returns `"hi"` (leading/trailing hyphens are stripped)

## Notes

This is the seeded **multi-criterion** fixture for demoing the veri loops + ledger rung.
Run `/solve-issue <this-issue-number>` against the `fixtures/demo-project/` codebase and
watch: a committed plan ledger (`.tdd/issue-<n>.md`), one Red→Green→Refactor cycle per
criterion, each step checked off atomically with its green commit, and generality emerging
through triangulation rather than hand-written code.
EOF
)

gh issue create "${repo_args[@]}" \
  --title "$title" \
  --body "$body"
