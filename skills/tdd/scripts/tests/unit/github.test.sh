#!/usr/bin/env bash
# Unit tests for scripts/lib/github.sh — sourced, never executed, with `gh` mocked as a
# same-named shell function.
#
# Fast tier (#336): no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/github.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../../lib/github.sh"
pass=0 fail=0
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

record() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $name"
    printf '%s' "$problems"
    echo "    stderr: $(printf '%q' "$(cat "$err")")"
  fi
}

# 1. against a gh whose GraphQL works, gh_pr_ready marks the draft ready through the ordinary
#    `gh pr ready` route, returns 0, and never calls the cloud session's ccr route
name="gh_pr_ready 42 against a gh that answers GraphQL runs gh pr ready 42, returns 0, and never calls pulls/42/ccr/ready_for_review"
calls="$scratch/calls1" err="$scratch/err1"
: > "$calls"
(
  gh() { echo "gh $*" >> "$calls"; return 0; }
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
grep -Fx "gh pr ready 42" "$calls" > /dev/null ||
  problems+="    want a 'gh pr ready 42' call, got: $(printf '%q' "$(cat "$calls")")"$'\n'
if grep -F "ccr/ready_for_review" "$calls" > /dev/null; then
  problems+="    want no ccr/ready_for_review call, got one"$'\n'
fi
record

# 2. against a gh that refuses GraphQL with the cloud session's 403, gh_pr_ready marks the
#    draft ready through the REST route that 403 names, pulls/{n}/ccr/ready_for_review
name="gh_pr_ready 42 against a gh that refuses GraphQL with the 403 calls pulls/42/ccr/ready_for_review over gh api and returns 0"
calls="$scratch/calls2" err="$scratch/err2"
: > "$calls"
(
  refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
  gh() {
    echo "gh $*" >> "$calls"
    case "$1" in
      issue|pr|repo) echo "HTTP 403: $refusal" >&2; return 1 ;;
      api)
        if [[ "${2:-}" == graphql ]]; then echo "HTTP 403: $refusal" >&2; return 1; fi
        return 0 ;;
    esac
    return 1
  }
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
grep -E '^gh api .*pulls/42/ccr/ready_for_review' "$calls" > /dev/null ||
  problems+="    want a 'gh api …pulls/42/ccr/ready_for_review' call, got: $(printf '%q' "$(cat "$calls")")"$'\n'
record

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
