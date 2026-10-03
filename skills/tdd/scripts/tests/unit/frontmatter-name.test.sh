#!/usr/bin/env bash
# Unit tests for scripts/tests/lib/frontmatter-name.sh — the name a markdown file's
# frontmatter declares, sourced, not run.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/frontmatter-name.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib/frontmatter-name.sh"
source "$HERE/../lib/harness.sh"

name="frontmatter_name prints the frontmatter's name, and nothing for a name outside it or after it"
dir="$(scratch_dir)"
printf '%s\n' '---' 'description: x' 'name:   tdd' '---' 'name: body' > "$dir/in.md"
printf '%s\n' 'intro' '---' 'name: late' '---' > "$dir/out.md"
printf '%s\n' '---' 'description: x' '---' 'name: body' > "$dir/body.md"
actual="$(
  # shellcheck disable=SC1090
  source "$LIB"
  printf '[%s] [%s] [%s]' "$(frontmatter_name "$dir/in.md")" "$(frontmatter_name "$dir/out.md")" \
    "$(frontmatter_name "$dir/body.md")"
)"
expect_eq "$name" "[tdd] [] []" "$actual"

finish
