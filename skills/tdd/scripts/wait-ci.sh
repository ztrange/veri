#!/usr/bin/env bash
# wait-ci.sh — wait a bounded slice for a PR's checks to finish, and be called again.
#
# Usage:
#   wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]
#
# Status: 0 every check completed SUCCESS, NEUTRAL or SKIPPED, not all SKIPPED · 1 a completed check
# concluded anything else · 2 no answer (bad arguments, gh failed, unreadable rollup), or a
# check still pending past the deadline an earlier call recorded for the same head commit ·
# 3 a check is still pending, none has appeared yet, every one was SKIPPED, or the PR still
# reports a head other than <head-sha>, when this call's <slice-seconds> run out.
#
# The deadline, <total-seconds> (default <slice-seconds>) after the first call for a head
# commit, is recorded in .tdd/ci-deadline-<sha>.
#
# Tunables (env): VERI_POLL poll interval secs (default 10).
set -uo pipefail
source "$(dirname "$0")/lib/github.sh"

[[ -n "${1:-}" ]] || { echo "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]" >&2; exit 2; }
pr="$1"
repo="${pr#https://github.com/}"; repo="${repo%/pull/*}"
max="${2:-540}"
total="${3:-}"
want="${4:-}"
poll="${VERI_POLL:-10}"

deadline=""
inherited=""
slice_end=""
passing="success neutral skipped"
json_docs='
import json, sys
def docs(text):
    at, out = 0, []
    while text[at:].strip():
        doc, at = json.JSONDecoder().raw_decode(text, len(text) - len(text[at:].lstrip()))
        out.append(doc)
    return out
'

fall_back() {
  echo "wait-ci.sh: $1; bounding the wait at 540 s" >&2
  echo 540
}

ci_bound() {
  local c pages="" status
  for c in success failure; do
    pages+="$(gh run list --repo "$repo" --workflow CI --status "$c" --limit 5 \
        --json databaseId,conclusion,startedAt,updatedAt)" \
      || { fall_back "gh run list could not answer"; return; }
  done
  python3 -c "$json_docs"'
from datetime import datetime
at = lambda s: datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timestamp()
runs = [r for page in docs(sys.stdin.read()) for r in page]
runs = sorted(runs, key=lambda r: r["databaseId"], reverse=True)[:5]
if len(runs) < 5:
    sys.exit(3)
print(min(600, round(2 * sum(at(r["updatedAt"]) - at(r["startedAt"]) for r in runs) / len(runs))))
' <<< "$pages"
  status=$?
  (( status == 3 )) && { fall_back "fewer than 5 success or failure CI runs found"; return; }
  return "$status"
}

[[ -n "$total" ]] || total="$(ci_bound)" || total="$max"

pr_head() {
  gh api "repos/$repo/pulls/${pr##*/pull/}" | python3 -c '
import json, sys
print(json.load(sys.stdin)["head"]["sha"] or "")
'
}

sha_state() {
  local runs statuses
  runs="$(gh_rest_list "repos/$repo/commits/$1/check-runs" '"check_runs": *\[ *\]')" || return 2
  statuses="$(gh api "repos/$repo/commits/$1/status")" || return 2
  python3 -c "$json_docs"'
docs = docs(sys.stdin.read())
pages = docs[:-1]
states = [s["state"] for s in docs[-1].get("statuses") or []]
runs = [r for p in pages for r in p.get("check_runs") or []]
outcomes = [r.get("conclusion") if r.get("status") == "completed" else None for r in runs]
if any(o is not None and o not in sys.argv[1].split() for o in outcomes) \
        or any(s in ("failure", "error") for s in states):
    print("red")
elif None in outcomes or all(o == "skipped" for o in outcomes) \
        or "pending" in states:
    print("pending")
else:
    print("green")
' "$passing" < <(printf '%s%s' "$runs" "$statuses")
}

while :; do
  read -r head < <(pr_head) && [[ -n "$head" ]] \
    || { echo "wait-ci.sh: could not read the checks of $pr" >&2; exit 2; }
  if [[ -n "$want" && "$head" != "$want" ]]; then
    state=pending
  else
    state="$(sha_state "$head")" || { echo "wait-ci.sh: could not read the checks of $head" >&2; exit 2; }
  fi
  case "$state" in
    green) exit 0 ;;
    red) exit 1 ;;
  esac
  now="$(date +%s)"
  if [[ -z "$deadline" ]]; then
    slice_end=$(( now + max ))
    key="${want:-$head}"
    mark=".tdd/ci-deadline-$key"
    if [[ -f "$mark" ]]; then
      deadline="$(< "$mark")"; inherited=1
    else
      deadline=$(( now + total )); echo "$deadline" > "$mark"
    fi
  fi
  if (( now >= deadline )); then
    [[ -n "$inherited" ]] && { echo "wait-ci.sh: checks of $pr still pending past the deadline recorded for $key" >&2; exit 2; }
    break
  fi
  (( now >= slice_end )) && break
  sleep "$poll"
done

exit 3
