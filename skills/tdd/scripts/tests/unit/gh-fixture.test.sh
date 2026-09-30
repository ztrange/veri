#!/usr/bin/env bash
# Unit tests for scripts/tests/lib/gh-fixture.sh — sourced, never executed: the helper that
# registers a PR in a VERI_GH_JSON fixture's prs.json.
#
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/gh-fixture.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/harness.sh"
source "$HERE/../lib/gh-fixture.sh"
scratch="$(scratch_dir)"

# 1. a second registration that lands between the first one's read of the PR lines and its
#    write of prs.json is still in prs.json afterwards
name="register_pr #588: a registration interleaved between another's read of the PR lines and its write of prs.json is not lost"
fx="$scratch/fx1"
mkdir -p "$fx"
printf '[]\n' > "$fx/prs.json"
interleaved=0
register_pr_between_read_and_write() {
  (( interleaved )) && return 0
  interleaved=1
  register_pr "$fx" 13 false
}
register_pr "$fx" 12 false
unset -f register_pr_between_read_and_write
content="$(cat "$fx/prs.json")"
problems=()
[[ "$interleaved" -eq 1 ]] || problems+=("the interleaving never happened: the helper never called register_pr_between_read_and_write")
[[ "$content" == *'pull/12"'* ]] || problems+=("PR 12 missing from prs.json: $content")
[[ "$content" == *'pull/13"'* ]] || problems+=("PR 13 missing from prs.json: $content")
report "$name"

finish
