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

# 1. against a gh whose GraphQL works, gh_pr_ready marks the draft ready through the ordinary
#    `gh pr ready` route, returns 0, and never calls the cloud session's ccr route
name="gh_pr_ready 42 against a gh that answers GraphQL runs gh pr ready 42, returns 0, and never calls pulls/42/ccr/ready_for_review"
calls="$scratch/calls1" err="$scratch/err1"
: > "$calls"
(
  gh() { echo "gh $*" >> "$calls"; return 0; }
  VERI_GH_DRIVER=auto
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
  VERI_GH_DRIVER=auto
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
  VERI_GH_DRIVER=auto
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
  VERI_GH_DRIVER=auto
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
  VERI_GH_DRIVER=auto
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
  VERI_GH_DRIVER=auto
  source "$LIB"
  gh_list 'repos/{owner}/{repo}/issues?per_page=2' issue list --state all --json number
) > /dev/null 2>> "$err"
rc_list=$?
problems=""
[[ "$rc_rest" -eq 2 ]] || problems+="    want gh_rest_list to return 2 on page 2's 502, got $rc_rest"$'\n'
[[ "$rc_list" -eq 2 ]] || problems+="    want gh_list to return 2 on page 2's network error, got $rc_list"$'\n'
record

# 8. with VERI_GH_DRIVER unset, every operation with a GraphQL route goes to REST alone: a gh
#    that would answer GraphQL is never asked, and a REST failure is a no-answer
name="with VERI_GH_DRIVER unset, gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready run only gh api, never gh issue or gh pr, and return 2 when gh api fails"
calls="$scratch/calls8" err="$scratch/err8"
: > "$calls"
problems=""
for rest_answers in yes no; do
  for op in view list json ready; do
    (
      gh() {
        echo "$op gh $*" >> "$calls"
        case "$1" in
          issue|pr) echo '[]'; return 0 ;;
          api)
            [[ "$rest_answers" == yes ]] || { echo 'gh: Bad Gateway (HTTP 502)' >&2; return 1; }
            case "$*" in *page=1) echo '[{"number":1}]' ;; *page=*) echo '[]' ;; *) echo '{}' ;; esac
            return 0 ;;
        esac
        return 1
      }
      python3() { cat > /dev/null; echo body; }
      unset VERI_GH_DRIVER VERI_GH_JSON
      source "$LIB"
      case "$op" in
        view) gh_issue_view 7 body ;;
        list) gh_list 'repos/{owner}/{repo}/issues' issue list --json number ;;
        json) gh_json issues.json 'repos/{owner}/{repo}/issues' issue list --json number ;;
        ready) gh_pr_ready 42 ;;
      esac
    ) > /dev/null 2>> "$err"
    rc=$?
    want=0
    [[ "$rest_answers" == yes ]] || want=2
    [[ "$rc" -eq "$want" ]] ||
      problems+="    $op with REST answering=$rest_answers: want return $want, got $rc"$'\n'
    grep -E "^$op gh api " "$calls" > /dev/null ||
      problems+="    $op with REST answering=$rest_answers: want a gh api call, got none"$'\n'
    if grep -E "^$op gh (issue|pr) " "$calls" > /dev/null; then
      problems+="    $op with REST answering=$rest_answers: want no GraphQL call, got: $(printf '%q' "$(grep -E "^$op gh (issue|pr) " "$calls")")"$'\n'
    fi
    : > "$calls"
  done
done
record


# 9. with VERI_GH_DRIVER=rest, every operation with a GraphQL route answers from REST alone, and
#    a REST failure is a no-answer that passes gh api's stderr through
name="with VERI_GH_DRIVER=rest, gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready answer from gh api alone, never gh issue or gh pr, and return 2 with gh api's stderr when it fails"
calls="$scratch/calls9" err="$scratch/err9" out="$scratch/out9" op_err="$scratch/operr9"
: > "$calls"
problems=""
for rest_answers in yes no; do
  for op in view list json ready; do
    (
      gh() {
        echo "$op gh $*" >> "$calls"
        case "$1" in
          issue|pr) echo 'graphql-answer'; return 0 ;;
          api)
            [[ "$rest_answers" == yes ]] || { echo 'gh: Bad Gateway (HTTP 502)' >&2; return 1; }
            case "$*" in *page=1) echo '[{"number":1}]' ;; *page=*) echo '[]' ;; *) echo '{}' ;; esac
            return 0 ;;
        esac
        return 1
      }
      python3() { cat > /dev/null; echo rest-body; }
      unset VERI_GH_JSON
      VERI_GH_DRIVER=rest
      source "$LIB"
      case "$op" in
        view) gh_issue_view 7 body ;;
        list) gh_list 'repos/{owner}/{repo}/issues' issue list --json number ;;
        json) gh_json issues.json 'repos/{owner}/{repo}/issues' issue list --json number ;;
        ready) gh_pr_ready 42 > /dev/null ;;
      esac
    ) > "$out" 2> "$op_err"
    rc=$?
    cat "$op_err" >> "$err"
    want=0
    [[ "$rest_answers" == yes ]] || want=2
    [[ "$rc" -eq "$want" ]] ||
      problems+="    $op with REST answering=$rest_answers: want return $want, got $rc"$'\n'
    grep -E "^$op gh api " "$calls" > /dev/null ||
      problems+="    $op with REST answering=$rest_answers: want a gh api call, got none"$'\n'
    if grep -E "^$op gh (issue|pr) " "$calls" > /dev/null; then
      problems+="    $op with REST answering=$rest_answers: want no GraphQL call, got: $(printf '%q' "$(grep -E "^$op gh (issue|pr) " "$calls")")"$'\n'
    fi
    if [[ "$rest_answers" == yes ]]; then
      case "$op" in
        view) want_out='rest-body' ;;
        list|json) want_out='[{"number":1}]' ;;
        ready) want_out='' ;;
      esac
      [[ "$(cat "$out")" == "$want_out" ]] ||
        problems+="    $op with REST answering=yes: want stdout $(printf '%q' "$want_out"), got $(printf '%q' "$(cat "$out")")"$'\n'
    else
      grep -F 'gh: Bad Gateway (HTTP 502)' "$op_err" > /dev/null ||
        problems+="    $op with REST answering=no: want gh api's stderr passed through, got $(printf '%q' "$(cat "$op_err")")"$'\n'
    fi
    : > "$calls"
  done
done
record

# 10. with VERI_GH_DRIVER=graphql, every operation with a GraphQL route answers from GraphQL
#     alone: a GraphQL failure is a no-answer with no gh api call, a success answers its stdout
name="with VERI_GH_DRIVER=graphql, gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready return 2 with no gh api call when GraphQL fails, and answer GraphQL's stdout when it succeeds"
calls="$scratch/calls10" err="$scratch/err10" out="$scratch/out10"
: > "$calls"
problems=""
for graphql_answers in yes no; do
  for op in view list json ready; do
    (
      gh() {
        echo "$op gh $*" >> "$calls"
        case "$1" in
          issue|pr)
            [[ "$graphql_answers" == yes ]] || { echo "$refusal" >&2; return 1; }
            echo 'graphql-answer'; return 0 ;;
          api)
            case "$*" in *page=1) echo '[{"number":1}]' ;; *page=*) echo '[]' ;; *) echo '{}' ;; esac
            return 0 ;;
        esac
        return 1
      }
      python3() { cat > /dev/null; echo rest-body; }
      unset VERI_GH_JSON
      VERI_GH_DRIVER=graphql
      source "$LIB"
      case "$op" in
        view) gh_issue_view 7 body ;;
        list) gh_list 'repos/{owner}/{repo}/issues' issue list --json number ;;
        json) gh_json issues.json 'repos/{owner}/{repo}/issues' issue list --json number ;;
        ready) gh_pr_ready 42 ;;
      esac
    ) > "$out" 2>> "$err"
    rc=$?
    want=0
    [[ "$graphql_answers" == yes ]] || want=2
    [[ "$rc" -eq "$want" ]] ||
      problems+="    $op with GraphQL answering=$graphql_answers: want return $want, got $rc"$'\n'
    grep -E "^$op gh (issue|pr) " "$calls" > /dev/null ||
      problems+="    $op with GraphQL answering=$graphql_answers: want a GraphQL call, got none"$'\n'
    if grep -E "^$op gh api " "$calls" > /dev/null; then
      problems+="    $op with GraphQL answering=$graphql_answers: want no gh api call, got: $(printf '%q' "$(grep -E "^$op gh api " "$calls")")"$'\n'
    fi
    if [[ "$graphql_answers" == yes ]]; then
      [[ "$(cat "$out")" == graphql-answer ]] ||
        problems+="    $op with GraphQL answering=yes: want stdout graphql-answer, got $(printf '%q' "$(cat "$out")")"$'\n'
    fi
    : > "$calls"
  done
done
record

# 11. operations with no GraphQL route — gh_issue_edit, gh_rest_list and gh_json with no gh args —
#     run their gh api call and no GraphQL call whatever VERI_GH_DRIVER says
name="gh_issue_edit, gh_rest_list and gh_json with no gh args run their gh api call and no gh issue or gh pr call under VERI_GH_DRIVER unset, auto, rest and graphql"
calls="$scratch/calls11" err="$scratch/err11"
: > "$calls"
problems=""
for driver in unset auto rest graphql; do
  for op in edit rest_list json; do
    (
      gh() {
        echo "$op gh $*" >> "$calls"
        case "$1" in
          issue|pr) echo 'graphql-answer'; return 0 ;;
          api)
            case "$*" in *page=1) echo '[{"number":1}]' ;; *page=*) echo '[]' ;; *) echo '{}' ;; esac
            return 0 ;;
        esac
        return 1
      }
      unset VERI_GH_DRIVER VERI_GH_JSON
      [[ "$driver" == unset ]] || VERI_GH_DRIVER="$driver"
      source "$LIB"
      case "$op" in
        edit) gh_issue_edit 7 "$scratch/body11" ;;
        rest_list) gh_rest_list 'repos/{owner}/{repo}/issues' ;;
        json) gh_json issues.json 'repos/{owner}/{repo}/issues' ;;
      esac
    ) > /dev/null 2>> "$err"
    rc=$?
    [[ "$rc" -eq 0 ]] ||
      problems+="    $op under VERI_GH_DRIVER=$driver: want return 0, got $rc"$'\n'
    grep -E "^$op gh api " "$calls" > /dev/null ||
      problems+="    $op under VERI_GH_DRIVER=$driver: want a gh api call, got none"$'\n'
    if grep -E "^$op gh (issue|pr) " "$calls" > /dev/null; then
      problems+="    $op under VERI_GH_DRIVER=$driver: want no GraphQL call, got: $(printf '%q' "$(grep -E "^$op gh (issue|pr) " "$calls")")"$'\n'
    fi
    : > "$calls"
  done
done
record

# 12. VERI_GH_DRIVER set but empty, or set to a value it does not know, is refused before any gh
#     process starts: every gh_* function returns 2 with one stderr line naming the variable and
#     the value
name="with VERI_GH_DRIVER empty, REST or gql, every gh_* function starts no gh process, returns 2 and prints one stderr line naming VERI_GH_DRIVER and the value"
calls="$scratch/calls12" err="$scratch/err12"
: > "$calls"
problems=""
for driver in '' REST gql; do
  for op in view list json json_rest ready edit rest_list; do
    (
      gh() {
        echo "$op gh $*" >> "$calls"
        case "$1" in
          issue|pr) echo '[]'; return 0 ;;
          api) echo '[]'; return 0 ;;
        esac
        return 1
      }
      git() { echo "$op git $*" >> "$calls"; return 1; }
      python3() { echo "$op python3 $*" >> "$calls"; cat > /dev/null; echo rest-body; }
      unset VERI_GH_JSON VERI_LABEL VERI_PRIORITY_LABEL
      export VERI_GH_DRIVER="$driver"
      source "$LIB"
      case "$op" in
        view) gh_issue_view 7 body ;;
        list) gh_list 'repos/{owner}/{repo}/issues' issue list --json number ;;
        json) gh_json issues.json 'repos/{owner}/{repo}/issues' issue list --json number ;;
        json_rest) gh_json issues.json 'repos/{owner}/{repo}/issues' ;;
        ready) gh_pr_ready 42 ;;
        edit) gh_issue_edit 7 "$scratch/body12" ;;
        rest_list) gh_rest_list 'repos/{owner}/{repo}/issues' ;;
      esac
    ) > /dev/null 2> "$err.one"
    rc=$?
    cat "$err.one" >> "$err"
    [[ "$rc" -eq 2 ]] ||
      problems+="    $op under VERI_GH_DRIVER='$driver': want return 2, got $rc"$'\n'
    if grep -E "^$op gh " "$calls" > /dev/null; then
      problems+="    $op under VERI_GH_DRIVER='$driver': want no gh process, got: $(printf '%q' "$(grep -E "^$op gh " "$calls")")"$'\n'
    fi
    lines="$(wc -l < "$err.one" | tr -d ' ')"
    if [[ "$lines" != 1 ]] || ! grep -F "VERI_GH_DRIVER" "$err.one" > /dev/null ||
        ! grep -F "'$driver'" "$err.one" > /dev/null; then
      problems+="    $op under VERI_GH_DRIVER='$driver': want one stderr line naming VERI_GH_DRIVER and '$driver', got $(printf '%q' "$(cat "$err.one")")"$'\n'
    fi
    : > "$calls"
  done
done
record

# 13. with VERI_GH_JSON set, gh_json answers the fixture file's contents byte for byte and starts no
#     gh or python3 process, with and without gh args, under every VERI_GH_DRIVER
name="with VERI_GH_JSON set, gh_json with and without gh args prints the fixture file's contents and starts no gh or python3 process under VERI_GH_DRIVER unset, auto, rest and graphql"
calls="$scratch/calls13" err="$scratch/err13" out="$scratch/out13"
: > "$calls"
mkdir -p "$scratch/fixtures13"
printf '[{"number":7,"title":"A thing"}]\n' > "$scratch/fixtures13/prs.json"
problems=""
for driver in unset auto rest graphql; do
  for op in json json_rest; do
    (
      gh() {
        echo "$op gh $*" >> "$calls"
        case "$*" in *page=1) echo '[{"number":99}]' ;; *page=*) echo '[]' ;; *) echo '[{"number":99}]' ;; esac
      }
      python3() { echo "$op python3 $*" >> "$calls"; return 1; }
      unset VERI_GH_DRIVER
      export VERI_GH_JSON="$scratch/fixtures13"
      [[ "$driver" == unset ]] || export VERI_GH_DRIVER="$driver"
      source "$LIB"
      case "$op" in
        json) gh_json prs.json 'repos/{owner}/{repo}/pulls?state=open' pr list --json number,title ;;
        json_rest) gh_json prs.json 'repos/{owner}/{repo}/pulls?state=open' ;;
      esac
    ) > "$out" 2>> "$err"
    rc=$?
    [[ "$rc" -eq 0 ]] ||
      problems+="    $op under VERI_GH_DRIVER=$driver: want return 0, got $rc"$'\n'
    cmp -s "$out" "$scratch/fixtures13/prs.json" ||
      problems+="    $op under VERI_GH_DRIVER=$driver: want the fixture's contents, got $(printf '%q' "$(cat "$out")")"$'\n'
    if grep -E "^$op (gh|python3) " "$calls" > /dev/null; then
      problems+="    $op under VERI_GH_DRIVER=$driver: want no process, got: $(printf '%q' "$(grep -E "^$op (gh|python3) " "$calls")")"$'\n'
    fi
    : > "$calls"
  done
done
record

# #879: gh_pr_ready <n> <head-sha> waits until pulls/<n> reports <head-sha> as the head before
#    marking the PR ready, reading it again every VERI_POLL seconds
name="#879 gh_pr_ready 42 <head-sha> marks PR 42 ready only after pulls/42 reports <head-sha> as its head, reading it again after VERI_POLL seconds while it reports another"
calls="$scratch/calls879" err="$scratch/err879" reads="$scratch/reads879"
old=8a7980e1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa new=a245e8b0bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
: > "$calls"; : > "$reads"
(
  gh() {
    echo "gh $*" >> "$calls"
    case "$*" in
      *pulls/42/ccr/ready_for_review*) return 0 ;;
      *pulls/42*)
        echo x >> "$reads"
        local sha="$old"
        (($(wc -l < "$reads") >= 3)) && sha="$new"
        if [[ "$*" == *--jq* || "$*" == *" -q "* ]]; then echo "$sha"; else printf '{"head":{"sha":"%s"}}\n' "$sha"; fi
        return 0 ;;
    esac
    echo "stub gh: unexpected call $*" >&2; return 1
  }
  sleep() { echo "sleep $*" >> "$calls"; }
  unset VERI_GH_DRIVER
  VERI_POLL=7
  source "$LIB"
  gh_pr_ready 42 "$new"
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
nreads="$(grep -cE '^gh api .*pulls/42([^/]|$)' "$calls")"
[[ "$nreads" -eq 3 ]] || problems+="    want 3 reads of pulls/42, got $nreads"$'\n'
ready_at="$(grep -m1 -nF 'ccr/ready_for_review' "$calls" | cut -d: -f1)"
before="$(awk -v n="${ready_at:-1}" 'NR < n && /^gh api .*pulls\/42([^\/]|$)/ { c++ } END { print c + 0 }' "$calls")"
[[ -n "$ready_at" && "$before" -eq 3 ]] ||
  problems+="    want the ready call only after the read that reported $new, got it at call ${ready_at:-none} with $before reads before it"$'\n'
grep -Fx "sleep 7" "$calls" > /dev/null || problems+="    want a 'sleep 7' between reads, got none"$'\n'
record

# #879: gh_pr_ready <n> <head-sha> gives up after a bounded number of reads of pulls/<n> that
#    all report another sha, returning 2 with PR <n> unready and both shas named on stderr
name="#879 gh_pr_ready 42 <head-sha> returns 2 without marking PR 42 ready when pulls/42 still reports another sha after its bounded number of reads, naming both shas on stderr"
calls="$scratch/calls879b" err="$scratch/err879b" reads="$scratch/reads879b"
: > "$calls"; : > "$reads"
(
  gh() {
    echo "gh $*" >> "$calls"
    case "$*" in
      *pulls/42/ccr/ready_for_review*) return 0 ;;
      *pulls/42*)
        echo x >> "$reads"
        (($(wc -l < "$reads") > 200)) && { echo "stub gh: pulls/42 read more than 200 times" >&2; return 1; }
        if [[ "$*" == *--jq* || "$*" == *" -q "* ]]; then echo "$old"; else printf '{"head":{"sha":"%s"}}\n' "$old"; fi
        return 0 ;;
    esac
    echo "stub gh: unexpected call $*" >&2; return 1
  }
  sleep() { echo "sleep $*" >> "$calls"; }
  unset VERI_GH_DRIVER
  VERI_POLL=7
  source "$LIB"
  gh_pr_ready 42 "$new"
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 2 ]] || problems+="    want return 2, got $rc"$'\n'
ready_calls="$(grep -E 'ccr/ready_for_review|^gh pr ready' "$calls")"
[[ -z "$ready_calls" ]] || problems+="    want no ready call, got: $ready_calls"$'\n'
nreads="$(wc -l < "$reads" | tr -d ' ')"
((nreads <= 200)) || problems+="    want a bounded number of reads of pulls/42, got $nreads before the stub refused"$'\n'
grep -F "$new" "$err" | grep -F "$old" > /dev/null || problems+="    want a stderr line naming $new and $old, got none"$'\n'
record

# #879: gh_pr_ready <n> with no head-sha marks the PR ready at once, as before the wait existed
name="#879 gh_pr_ready 42 with no head-sha marks PR 42 ready at once, reading no pulls/42 and never sleeping"
calls="$scratch/calls879c" err="$scratch/err879c"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    case "$*" in
      *pulls/42/ccr/ready_for_review*) return 0 ;;
      *pulls/42*)
        if [[ "$*" == *--jq* || "$*" == *" -q "* ]]; then echo "$old"; else printf '{"head":{"sha":"%s"}}\n' "$old"; fi
        return 0 ;;
    esac
    echo "stub gh: unexpected call $*" >&2; return 1
  }
  sleep() { echo "sleep $*" >> "$calls"; }
  unset VERI_GH_DRIVER
  VERI_POLL=7
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
grep -F "ccr/ready_for_review" "$calls" > /dev/null ||
  problems+="    want a ready call for PR 42, got: $(printf '%q' "$(cat "$calls")")"$'\n'
nreads="$(grep -cE '^gh api .*pulls/42([^/]|$)' "$calls")"
[[ "$nreads" -eq 0 ]] || problems+="    want no read of pulls/42, got $nreads"$'\n'
if grep -E '^sleep ' "$calls" > /dev/null; then
  problems+="    want no sleep, got: $(grep -E '^sleep ' "$calls" | tr '\n' ' ')"$'\n'
fi
record

# 14. with VERI_GH_DRIVER unset, a 404 on the ccr route — github.com has no such REST route —
#     falls back to GraphQL's markPullRequestReadyForReview over gh api graphql, never gh pr ready
name="#888: with VERI_GH_DRIVER unset, gh_pr_ready 42 whose pulls/42/ccr/ready_for_review 404s sends markPullRequestReadyForReview with the PR's node id over gh api graphql, never runs gh pr ready, and returns 0"
calls="$scratch/calls14" err="$scratch/err14"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*) echo 'gh: Not Found (HTTP 404)' >&2; return 1 ;;
      *markPullRequestReadyForReview*) echo '{"data":{"markPullRequestReadyForReview":{"pullRequest":{"isDraft":false}}}}' ;;
      *' -q '* | *' --jq '* | *--jq=*) echo 'PR_kwDOnode42' ;;
      *graphql*) echo '{"data":{"repository":{"pullRequest":{"id":"PR_kwDOnode42"}}}}' ;;
      *pulls/42*) echo '{"number":42,"node_id":"PR_kwDOnode42","draft":true}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
grep -E '^gh api graphql .*markPullRequestReadyForReview.*PR_kwDOnode42|^gh api graphql .*PR_kwDOnode42.*markPullRequestReadyForReview' "$calls" > /dev/null ||
  problems+="    want a 'gh api graphql' markPullRequestReadyForReview call carrying PR_kwDOnode42, got: $(printf '%q' "$(cat "$calls")")"$'\n'
if grep -E '^gh pr ' "$calls" > /dev/null; then
  problems+="    want no gh pr call, got: $(printf '%q' "$(grep -E '^gh pr ' "$calls")")"$'\n'
fi
record

# 15. with VERI_GH_DRIVER unset, when the ccr route and the gh api graphql fallback both fail,
#     the PR is not readied and gh_pr_ready says so with 2
name="#888: with VERI_GH_DRIVER unset, gh_pr_ready 42 whose pulls/42/ccr/ready_for_review 404s and whose gh api graphql markPullRequestReadyForReview fails with a 502 tries both and returns 2"
calls="$scratch/calls15" err="$scratch/err15"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*) echo 'gh: Not Found (HTTP 404)' >&2; return 1 ;;
      *markPullRequestReadyForReview*) echo 'gh: Bad Gateway (HTTP 502)' >&2; return 1 ;;
      *' -q '* | *' --jq '* | *--jq=*) echo 'PR_kwDOnode42' ;;
      *pulls/42*) echo '{"number":42,"node_id":"PR_kwDOnode42","draft":true}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 2 ]] || problems+="    want return 2, got $rc"$'\n'
grep -F 'ccr/ready_for_review' "$calls" > /dev/null ||
  problems+="    want a pulls/42/ccr/ready_for_review call, got: $(printf '%q' "$(cat "$calls")")"$'\n'
grep -E '^gh api graphql .*markPullRequestReadyForReview' "$calls" > /dev/null ||
  problems+="    want a 'gh api graphql' markPullRequestReadyForReview call, got: $(printf '%q' "$(cat "$calls")")"$'\n'
record

# 16. with VERI_GH_DRIVER unset, a 404 on the ccr route that the gh api graphql fallback then
#     recovers from leaves no trace on stderr: the PR is ready, and nothing reads like a failure
name="#1054: with VERI_GH_DRIVER unset, gh_pr_ready 42 whose pulls/42/ccr/ready_for_review 404s and whose gh api graphql markPullRequestReadyForReview then readies it returns 0 with no HTTP 404 line on stderr"
calls="$scratch/calls16" err="$scratch/err16"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*) echo 'gh: Not Found (HTTP 404)' >&2; return 1 ;;
      *markPullRequestReadyForReview*) echo '{"data":{"markPullRequestReadyForReview":{"pullRequest":{"isDraft":false}}}}' ;;
      *' -q '* | *' --jq '* | *--jq=*) echo 'PR_kwDOnode42' ;;
      *pulls/42*) echo '{"number":42,"node_id":"PR_kwDOnode42","draft":true}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
grep -E '^gh api graphql .*markPullRequestReadyForReview' "$calls" > /dev/null ||
  problems+="    want a 'gh api graphql' markPullRequestReadyForReview call, got: $(printf '%q' "$(cat "$calls")")"$'\n'
if grep -F 'HTTP 404' "$err" > /dev/null; then
  problems+="    want no HTTP 404 line on stderr, got: $(printf '%q' "$(grep -F 'HTTP 404' "$err")")"$'\n'
fi
record

# 17. with VERI_GH_DRIVER unset, when the ccr route and the gh api graphql fallback both fail,
#     gh_pr_ready returns 2 and stderr carries each route's own failure message
name="#1054: with VERI_GH_DRIVER unset, gh_pr_ready 42 whose pulls/42/ccr/ready_for_review 404s and whose gh api graphql markPullRequestReadyForReview fails with a 502 returns 2 with both routes' failure messages on stderr"
calls="$scratch/calls17" err="$scratch/err17"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*) echo 'gh: Not Found (HTTP 404)' >&2; return 1 ;;
      *markPullRequestReadyForReview*) echo 'gh: Bad Gateway (HTTP 502)' >&2; return 1 ;;
      *' -q '* | *' --jq '* | *--jq=*) echo 'PR_kwDOnode42' ;;
      *pulls/42*) echo '{"number":42,"node_id":"PR_kwDOnode42","draft":true}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 2 ]] || problems+="    want return 2, got $rc"$'\n'
grep -F 'gh: Not Found (HTTP 404)' "$err" > /dev/null ||
  problems+="    want the ccr route's 'gh: Not Found (HTTP 404)' on stderr"$'\n'
grep -F 'gh: Bad Gateway (HTTP 502)' "$err" > /dev/null ||
  problems+="    want the gh api graphql route's 'gh: Bad Gateway (HTTP 502)' on stderr"$'\n'
record

# 18. with VERI_GH_DRIVER unset, a ccr route that readies the PR is the only route taken: the
#     gh api graphql fallback is never called, and gh_pr_ready returns 0
name="#1054: with VERI_GH_DRIVER unset, gh_pr_ready 42 whose pulls/42/ccr/ready_for_review succeeds readies PR 42 by that route alone, never calls gh api graphql, and returns 0"
calls="$scratch/calls18" err="$scratch/err18"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*) echo '{"number":42,"draft":false}' ;;
      *markPullRequestReadyForReview*) echo '{"data":{"markPullRequestReadyForReview":{"pullRequest":{"isDraft":false}}}}' ;;
      *' -q '* | *' --jq '* | *--jq=*) echo 'PR_kwDOnode42' ;;
      *pulls/42*) echo '{"number":42,"node_id":"PR_kwDOnode42","draft":true}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
grep -E '^gh api -X POST .*pulls/42/ccr/ready_for_review' "$calls" > /dev/null ||
  problems+="    want a POST to pulls/42/ccr/ready_for_review, got: $(printf '%q' "$(cat "$calls")")"$'\n'
if grep -E '^gh api graphql' "$calls" > /dev/null; then
  problems+="    want no gh api graphql call, got: $(printf '%q' "$(grep -E '^gh api graphql' "$calls")")"$'\n'
fi
record

# 19. with VERI_GH_DRIVER unset, the 404 body gh api prints on stdout for a refused ccr route
#     never reaches the caller's stdout once the gh api graphql fallback readies the PR
name="#1063: with VERI_GH_DRIVER unset, gh_pr_ready 42 whose pulls/42/ccr/ready_for_review 404s with its response body on stdout and whose gh api graphql markPullRequestReadyForReview then readies it returns 0 with nothing on stdout"
calls="$scratch/calls19" err="$scratch/err19" out="$scratch/out19"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*)
        printf '{\n  "message": "Not Found",\n  "documentation_url": "https://docs.github.com/rest",\n  "status": "404"\n}\n'
        echo 'gh: Not Found (HTTP 404)' >&2
        return 1 ;;
      *markPullRequestReadyForReview*) echo '{"data":{"markPullRequestReadyForReview":{"pullRequest":{"isDraft":false}}}}' ;;
      *' -q '* | *' --jq '* | *--jq=*) echo 'PR_kwDOnode42' ;;
      *pulls/42*) echo '{"number":42,"node_id":"PR_kwDOnode42","draft":true}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > "$out" 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
[[ -s "$out" ]] && problems+="    want nothing on stdout, got: $(printf '%q' "$(cat "$out")")"$'\n'
record

# 20. with VERI_GH_DRIVER unset and every route failing, the 404 body the refused ccr route
#     printed on stdout reaches the caller on stderr
name="#1063: with VERI_GH_DRIVER unset, gh_pr_ready 42 whose pulls/42/ccr/ready_for_review 404s with its response body on stdout and whose gh api graphql markPullRequestReadyForReview also fails returns 2 with that body on stderr"
calls="$scratch/calls20" err="$scratch/err20" out="$scratch/out20"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*)
        printf '{\n  "message": "Not Found",\n  "documentation_url": "https://docs.github.com/rest",\n  "status": "404"\n}\n'
        echo 'gh: Not Found (HTTP 404)' >&2
        return 1 ;;
      *markPullRequestReadyForReview*) echo 'gh: Something went wrong (HTTP 502)' >&2; return 1 ;;
      *' -q '* | *' --jq '* | *--jq=*) echo 'PR_kwDOnode42' ;;
      *pulls/42*) echo '{"number":42,"node_id":"PR_kwDOnode42","draft":true}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > "$out" 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 2 ]] || problems+="    want return 2, got $rc"$'\n'
grep -F '"documentation_url": "https://docs.github.com/rest",' "$err" > /dev/null ||
  problems+="    want the ccr route's response body on stderr"$'\n'
record

# 21. with VERI_GH_DRIVER unset, a gh whose gh pr ready fails with GraphQL's 403 is never asked:
#     the PR is readied over REST alone and nothing reaches stderr
name="#623: with VERI_GH_DRIVER unset, gh_pr_ready 42 against a gh whose gh pr ready fails with GraphQL's HTTP 403 readies PR 42 over pulls/42/ccr/ready_for_review, never runs gh pr ready, returns 0 and prints nothing on stderr"
calls="$scratch/calls21" err="$scratch/err21"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    if [[ "$1" == pr ]]; then echo "$refusal (HTTP 403)" >&2; return 1; fi
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*) echo '{"number":42,"draft":false}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_DRIVER VERI_GH_JSON
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
grep -E '^gh api -X POST .*pulls/42/ccr/ready_for_review' "$calls" > /dev/null ||
  problems+="    want a POST to pulls/42/ccr/ready_for_review, got: $(printf '%q' "$(cat "$calls")")"$'\n'
if grep -E '^gh pr ready' "$calls" > /dev/null; then
  problems+="    want no gh pr ready call, got: $(printf '%q' "$(grep -E '^gh pr ready' "$calls")")"$'\n'
fi
[[ -s "$err" ]] && problems+="    want nothing on stderr, got: $(printf '%q' "$(cat "$err")")"$'\n'
record

# 22. with VERI_GH_DRIVER=auto, the 403 a refused gh pr ready prints never reaches stderr once
#     the REST ready route readies the PR
name="#623: with VERI_GH_DRIVER=auto, gh_pr_ready 42 against a gh whose gh pr ready fails with GraphQL's HTTP 403 and whose REST ready route then succeeds returns 0 with no line of that 403 on stderr"
calls="$scratch/calls22" err="$scratch/err22"
: > "$calls"
(
  gh() {
    echo "gh $*" >> "$calls"
    if [[ "$1" == pr ]]; then echo "$refusal (HTTP 403)" >&2; return 1; fi
    [[ "$1" == api ]] || return 1
    case "$*" in
      *ccr/ready_for_review*) echo '{"number":42,"draft":false}' ;;
      *) return 1 ;;
    esac
  }
  unset VERI_GH_JSON
  VERI_GH_DRIVER=auto
  source "$LIB"
  gh_pr_ready 42
) > /dev/null 2> "$err"
rc=$?
problems=""
[[ "$rc" -eq 0 ]] || problems+="    want return 0, got $rc"$'\n'
if grep -F 'HTTP 403' "$err" > /dev/null; then
  problems+="    want no line of the 403 on stderr, got: $(printf '%q' "$(cat "$err")")"$'\n'
fi
record

finish
