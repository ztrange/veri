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
