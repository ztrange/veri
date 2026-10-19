#!/usr/bin/env bash
# Unit tests for scripts/lib/github.sh — sourced, never executed, with `gh` mocked as a
# same-named shell function.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
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

finish
