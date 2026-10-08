#!/usr/bin/env bash
# lib/github.sh — sourced, not run: defines `gh_pr_ready`, `gh_issue_view`, `gh_issue_edit`, `gh_json`, `gh_list` and `gh_rest_list`.
#
# gh_pr_ready <n> [head-sha] — mark draft PR <n> ready for review; given <head-sha>, only once
#   pulls/<n> reports it as the head, reading it again every VERI_POLL seconds (default 10),
#   at most 30 times.
#   0  marked ready
#   2  GitHub gave no answer on either route, or pulls/<n> never reported <head-sha>
#
# gh_issue_view <n> body|labels — print issue <n>'s body, or its label names one per line;
#   2 when GitHub gave no answer on either route.
#
# gh_issue_edit <n> <body-file> — replace issue <n>'s body with the contents of <body-file>;
#   2 when GitHub gave no answer.
#
# gh_json <fixture-file> <rest-path> [gh args…] — print `$VERI_GH_JSON/<fixture-file>` when
#   VERI_GH_JSON is set, otherwise `gh_list <rest-path> <gh args…>`'s JSON, or with no gh args
#   `gh_rest_list <rest-path>`'s.
#
# gh_list <rest-path> <gh args…> — print `gh <gh args…>`'s JSON, or else `gh_rest_list
#   <rest-path>`'s; 2 when GitHub gave no answer on either route.
#
# gh_rest_list <rest-path> [empty-regex] — print every page of `gh api <rest-path>`, requested as
#   page=1, 2, … until one matches <empty-regex> (default: a bare `[]`), one JSON document per
#   page, back to back; 2 when GitHub gave no answer.
#
# VERI_GH_DRIVER picks the route of gh_pr_ready, gh_issue_view, gh_list and gh_json with gh args:
#   rest (the default when unset) runs only `gh api`, graphql only the gh porcelain command with no
#   fallback, auto GraphQL then REST. Set but empty, or any other value, returns 2 with a stderr
#   line naming the variable and the value, checked at call time. gh_issue_edit, gh_rest_list and
#   gh_json with no gh args use REST under every value, and VERI_GH_JSON takes precedence over it.
#   A Claude Code cloud session, where GraphQL is refused, needs nothing set.

_gh_driver_known() {
  case "${VERI_GH_DRIVER-rest}" in
    auto|rest|graphql) ;;
    *) echo "VERI_GH_DRIVER is '${VERI_GH_DRIVER}': expected auto, rest or graphql" >&2; return 2 ;;
  esac
}

_gh_route_open() {
  case "${VERI_GH_DRIVER:-rest}:$1" in auto:graphql | graphql:graphql) ;; graphql:rest | *:graphql) return 1 ;; esac
}

_gh_graphql() {
  _gh_route_open graphql && "$@"
}

_gh_rest() {
  _gh_route_open rest && "$@"
}

gh_pr_ready() {
  _gh_driver_known || return 2
  local head tries=0
  while [[ -n "${2:-}" ]]; do
    head="$(gh api "repos/{owner}/{repo}/pulls/$1" --jq .head.sha)" || return 2
    [[ "$head" == "$2" ]] && break
    ((++tries < 30)) || { echo "gh_pr_ready: PR $1 head is $head after $tries reads, expected $2" >&2; return 2; }
    sleep "${VERI_POLL:-10}"
  done
  local gql_err ccr_err
  { gql_err="$(_gh_graphql gh pr ready "$1" 2>&1 >&3)"; } 3>&1 && return
  ccr_err="$(_gh_rest gh api -X POST "repos/{owner}/{repo}/pulls/$1/ccr/ready_for_review" 2>&1)" && return
  _gh_rest _gh_api_graphql_ready "$1" && return
  [[ -z "$gql_err" ]] || echo "$gql_err" >&2
  [[ -z "$ccr_err" ]] || echo "$ccr_err" >&2
  return 2
}

_gh_api_graphql_ready() {
  local id
  id=$(gh api "repos/{owner}/{repo}/pulls/$1" -q .node_id) || return 1
  gh api graphql -f query='mutation($id: ID!) { markPullRequestReadyForReview(input: {pullRequestId: $id}) { pullRequest { isDraft } } }' \
    -f id="$id" > /dev/null
}

gh_issue_view() {
  _gh_driver_known || return 2
  local filter='.body'
  [[ "$2" == labels ]] && filter='.labels[].name'
  _gh_graphql gh issue view "$1" --json "$2" -q "$filter" 2> /dev/null ||
    _gh_rest _gh_rest_issue_view "$1" "$2" || return 2
}

_gh_rest_issue_view() {
  gh api "repos/{owner}/{repo}/issues/$1" | python3 -c '
import json, sys
issue = json.load(sys.stdin)
if sys.argv[1] == "labels":
    for label in issue["labels"]:
        print(label["name"])
else:
    print(issue["body"] or "")
' "$2"
}

gh_issue_edit() {
  _gh_driver_known || return 2
  gh api -X PATCH "repos/{owner}/{repo}/issues/$1" -F "body=@$2" > /dev/null || return 2
}

gh_json() {
  local fixture="$1" rest="$2"; shift 2
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    cat "$VERI_GH_JSON/$fixture"
  elif (($# == 0)); then
    gh_rest_list "$rest"
  else
    gh_list "$rest" "$@"
  fi
}

gh_list() {
  local rest="$1"; shift
  _gh_graphql gh "$@" 2> /dev/null || _gh_rest gh_rest_list "$rest" || return 2
}

gh_rest_list() {
  _gh_driver_known || return 2
  local sep='?' page=1 body empty="${2:-^\[\]$}"
  [[ "$1" == *\?* ]] && sep='&'
  while body="$(gh api "$1${sep}page=$page")" || return 2; [[ ! "$body" =~ $empty ]]; do
    printf '%s' "$body"
    page=$((page + 1))
  done
}
