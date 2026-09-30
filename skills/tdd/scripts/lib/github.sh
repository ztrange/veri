#!/usr/bin/env bash
# lib/github.sh — sourced, not run: defines `gh_pr_ready`, `gh_issue_view` and `gh_list`.
#
# gh_pr_ready <n> — mark draft PR <n> ready for review.
#   0  marked ready
#   2  GitHub gave no answer on either route
#
# gh_issue_view <n> body|labels — print issue <n>'s body, or its label names one per line;
#   2 when GitHub gave no answer on either route.
#
# gh_list <rest-path> <gh args…> — print `gh <gh args…>`'s JSON, or else every page of
#   `gh api --paginate <rest-path>`, one JSON array per page, back to back; 2 when GitHub gave
#   no answer on either route.

gh_pr_ready() {
  gh pr ready "$1" ||
    gh api -X POST "repos/{owner}/{repo}/pulls/$1/ccr/ready_for_review" ||
    return 2
}

gh_issue_view() {
  local filter='.body'
  [[ "$2" == labels ]] && filter='.labels[].name'
  gh issue view "$1" --json "$2" -q "$filter" 2> /dev/null ||
    gh api "repos/{owner}/{repo}/issues/$1" | python3 -c '
import json, sys
issue = json.load(sys.stdin)
if sys.argv[1] == "labels":
    for label in issue["labels"]:
        print(label["name"])
else:
    print(issue["body"] or "")
' "$2" || return 2
}

gh_list() {
  local rest="$1"; shift
  gh "$@" 2> /dev/null || gh api --paginate "$rest" || return 2
}
