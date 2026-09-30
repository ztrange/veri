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
source "$HERE/../lib/harness.sh"
scratch="$(scratch_dir)"
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
proxy='gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)'

record() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$name"
    printf '%s' "$problems"
    echo "    stderr: $(printf '%q' "$(cat "$err")")"
  fi
}

three_pages_on_repos() {
  local path="" paginate="" include="" query="" page body link
  while (($#)); do
    case "$1" in
      --paginate) paginate=1 ;;
      -i|--include) include=1 ;;
      -X|--method) [[ "$2" == GET ]] || return 1; shift ;;
      -f|-F|--field|--raw-field) query+="&$2"; shift ;;
      -*) echo "stub gh: unsupported flag $1" >&2; return 1 ;;
      *) path="$1" ;;
    esac
    shift
  done
  if [[ "$path" == *repositories/* ]]; then echo "$proxy" >&2; return 1; fi
  [[ "$path" == *repos/* ]] || { echo "stub gh: unexpected path $path" >&2; return 1; }
  query="${path#*\?}&$query"
  [[ "$path" == *\?* ]] || query="&$query"
  page=1
  [[ "&$query" =~ \&page=([0-9]+) ]] && page="${BASH_REMATCH[1]}"
  case "$page" in
    1) body='[{"number":1},{"number":2}]' ;;
    2) body='[{"number":3},{"number":4}]' ;;
    3) body='[{"number":5},{"number":6}]' ;;
    *) body='[]' ;;
  esac
  link=""
  ((page < 3)) &&
    link="Link: <https://api.github.com/repositories/1275470346/issues?per_page=2&page=$((page + 1))>; rel=\"next\""
  if [[ -n "$include" ]]; then
    printf 'HTTP/2.0 200 OK\n'
    [[ -n "$link" ]] && printf '%s\n' "$link"
    printf '\n'
  fi
  printf '%s\n' "$body"
  if [[ -n "$paginate" && -n "$link" ]]; then echo "$proxy" >&2; return 1; fi
  return 0
}

numbers_in() {
  grep -oE '"number": *[0-9]+' "$1" | grep -oE '[0-9]+$' | tr '\n' ' '
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

# 3. a GitHub failure that is not the GraphQL refusal gives no answer, so gh_pr_ready returns
#    2 — a 404 on the ordinary route, a 502 on the ccr route
name="gh_pr_ready 42 returns 2 when gh pr ready fails with a 404, and when pulls/42/ccr/ready_for_review fails with a 502"
err="$scratch/err3"
(
  gh() { echo "HTTP 404: Not Found (https://api.github.com/graphql)" >&2; return 1; }
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc_ordinary=$?
(
  gh() {
    case "$1" in
      issue|pr|repo) echo "HTTP 403: $refusal" >&2; return 1 ;;
      api) echo "HTTP 502: Bad Gateway" >&2; return 1 ;;
    esac
    return 1
  }
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2>> "$err"
rc_ccr=$?
problems=""
[[ "$rc_ordinary" -eq 2 ]] || problems+="    want return 2 from the ordinary route's 404, got $rc_ordinary"$'\n'
[[ "$rc_ccr" -eq 2 ]] || problems+="    want return 2 from the ccr route's 502, got $rc_ccr"$'\n'
record

# 4. the cloud session's proxy refuses the repositories/{id} paths GitHub's Link: rel="next"
#    names, so gh_rest_list pages on the repos/{owner}/{repo} path it was given instead
name="gh_rest_list repos/{owner}/{repo}/issues?per_page=2 against a gh serving three pages on repos/…?page=N and refusing repositories/ with the proxy's 403 prints items 1–6 and returns 0"
calls="$scratch/calls4" err="$scratch/err4" out="$scratch/out4"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "${1:-}" == api ]] || return 1
    shift
    three_pages_on_repos "$@"
  }
  source "$LIB"
  gh_rest_list 'repos/{owner}/{repo}/issues?per_page=2'
) > "$out" 2> "$err"
rc=$?
got="$(numbers_in "$out")"
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
[[ "$got" == "1 2 3 4 5 6 " ]] ||
  problems+="    want items 1 2 3 4 5 6, got: $(printf '%q' "$got")"$'\n'
if grep -F "repositories/" "$calls" > /dev/null; then
  problems+="    want no repositories/ request, got: $(printf '%q' "$(grep -F repositories/ "$calls")")"$'\n'
fi
record

# 5. a rest-path with no query string of its own gets page=N as its query string
name="gh_rest_list repos/{owner}/{repo}/pulls against a gh serving only repos/{owner}/{repo}/pulls?page=N prints items 1–3 and returns 0"
calls="$scratch/calls5" err="$scratch/err5" out="$scratch/out5"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    case "$*" in
      'api repos/{owner}/{repo}/pulls?page=1') printf '%s\n' '[{"number":1},{"number":2}]' ;;
      'api repos/{owner}/{repo}/pulls?page=2') printf '%s\n' '[{"number":3}]' ;;
      'api repos/{owner}/{repo}/pulls?page='*) printf '%s\n' '[]' ;;
      *) echo 'gh: Not Found (HTTP 404)' >&2; return 1 ;;
    esac
  }
  source "$LIB"
  gh_rest_list 'repos/{owner}/{repo}/pulls'
) > "$out" 2> "$err"
rc=$?
got="$(numbers_in "$out")"
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc; gh saw: $(printf '%q' "$(cat "$calls")")"$'\n'
[[ "$got" == "1 2 3 " ]] || problems+="    want items 1 2 3, got: $(printf '%q' "$got")"$'\n'
record

# 6. when the gh subcommand route fails, gh_list falls back to REST, which pages on the
#    repos/{owner}/{repo} path through the same three-page stub as case 4
name="gh_list repos/{owner}/{repo}/issues?per_page=2 with gh issue list refused and a gh serving three pages on repos/…?page=N and refusing repositories/ with the proxy's 403 prints items 1–6 and returns 0"
calls="$scratch/calls6" err="$scratch/err6" out="$scratch/out6"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    if [[ "${1:-}" != api ]]; then echo "HTTP 403: $refusal" >&2; return 1; fi
    shift
    three_pages_on_repos "$@"
  }
  source "$LIB"
  gh_list 'repos/{owner}/{repo}/issues?per_page=2' issue list --state all --json number
) > "$out" 2> "$err"
rc=$?
got="$(numbers_in "$out")"
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
[[ "$got" == "1 2 3 4 5 6 " ]] ||
  problems+="    want items 1 2 3 4 5 6, got: $(printf '%q' "$got")"$'\n'
if grep -F "repositories/" "$calls" > /dev/null; then
  problems+="    want no repositories/ request, got: $(printf '%q' "$(grep -F repositories/ "$calls")")"$'\n'
fi
record

# 7. a later page that fails for a reason other than the proxy's refusal gives no answer, so
#    gh_rest_list and gh_list return 2 — a 502 on page 2, a network error on page 2
name="gh_rest_list and gh_list repos/{owner}/{repo}/issues?per_page=2 return 2 when page 1 answers and page 2 fails with a 502, and with a network error"
err="$scratch/err7"
(
  gh() {
    case "$*" in
      'api repos/{owner}/{repo}/issues?per_page=2&page=1') printf '%s\n' '[{"number":1},{"number":2}]' ;;
      'api repos/{owner}/{repo}/issues?per_page=2&page=2') echo 'gh: Bad Gateway (HTTP 502)' >&2; return 1 ;;
      *) echo 'stub gh: unexpected call' >&2; return 1 ;;
    esac
  }
  source "$LIB"
  gh_rest_list 'repos/{owner}/{repo}/issues?per_page=2'
) > /dev/null 2> "$err"
rc_rest=$?
(
  gh() {
    case "$*" in
      'api repos/{owner}/{repo}/issues?per_page=2&page=1') printf '%s\n' '[{"number":1},{"number":2}]' ;;
      'api repos/{owner}/{repo}/issues?per_page=2&page=2')
        echo 'error connecting to api.github.com' >&2; return 1 ;;
      *) echo "HTTP 403: $refusal" >&2; return 1 ;;
    esac
  }
  source "$LIB"
  gh_list 'repos/{owner}/{repo}/issues?per_page=2' issue list --state all --json number
) > /dev/null 2>> "$err"
rc_list=$?
problems=""
[[ "$rc_rest" -eq 2 ]] || problems+="    want gh_rest_list to return 2 on page 2's 502, got $rc_rest"$'\n'
[[ "$rc_list" -eq 2 ]] || problems+="    want gh_list to return 2 on page 2's network error, got $rc_list"$'\n'
record

finish
