#!/usr/bin/env bash
# lib/github.sh — sourced, not run: defines `gh_pr_ready`, `gh_issue_view`, `gh_issue_edit`, `gh_list` and `gh_rest_list`.
#
# gh_pr_ready <n> — mark draft PR <n> ready for review.
#   0  marked ready
#   2  GitHub gave no answer on either route
#
# gh_issue_view <n> body|labels — print issue <n>'s body, or its label names one per line;
#   2 when GitHub gave no answer on either route.
#
# gh_issue_edit <n> <body-file> — replace issue <n>'s body with the contents of <body-file>;
#   2 when GitHub gave no answer.
#
# gh_list <rest-path> <gh args…> — print `gh <gh args…>`'s JSON, or else every page of
#   `gh api --paginate <rest-path>`, one JSON array per page, back to back; 2 when GitHub gave
#   no answer on either route.
#
# gh_rest_list <rest-path> — print every page of `gh api <rest-path>`, requested as page=1, 2, …
#   until one comes back empty, one JSON array per page, back to back; 2 when GitHub gave no answer.

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

gh_issue_edit() {
  gh api -X PATCH "repos/{owner}/{repo}/issues/$1" -F "body=@$2" > /dev/null || return 2
}

gh_list() {
  local rest="$1"; shift
  gh "$@" 2> /dev/null || gh api --paginate "$rest" || return 2
}

gh_rest_list() {
  local sep='?' page=1 body
  [[ "$1" == *\?* ]] && sep='&'
  while body="$(gh api "$1${sep}page=$page")" || return 2; [[ "$body" != "[]" ]]; do
    printf '%s' "$body"
    page=$((page + 1))
  done
}
