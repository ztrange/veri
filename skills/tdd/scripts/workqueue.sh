#!/usr/bin/env bash
# workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns issues to named
# workers and records what happened to each.
#
# The file lives under the repository's MAIN working tree, resolved the way
# solvable-issues.sh resolves it (lib/main-working-tree.sh), so every worktree of the
# clone reads and writes the one queue. One item per line, tab-separated:
#
#   <worker>	<issue>	<state>	<detail>
#
# Usage:   workqueue.sh assign <worker> <issue>...
#          workqueue.sh next <worker>
#          workqueue.sh start <worker> <issue>
#          workqueue.sh done <worker> <issue> <merge-sha>
#          workqueue.sh park <worker> <issue> <reason>
#          workqueue.sh show [<worker>]
# Exit:    0 done, 1 `start`/`done`/`park` naming no item of that worker's in the state it
#          moves from, 3 `next` found nothing launchable, 2 an unknown subcommand, an `assign`
#          naming no worker or no issue, an empty issue, or naming one issue twice, a `done`
#          with no merge sha, a `park` reason holding a tab or a newline, an issue already
#          queued or running for any worker, or a lock not taken within
#          VERI_WORKQUEUE_LOCK_WAIT seconds — refused before anything is written, so the file
#          is left byte-identical
set -euo pipefail

source "$(dirname "$0")/lib/main-working-tree.sh"
source "$(dirname "$0")/lib/github.sh"

main_tree="$(main_working_tree)"
queue="$main_tree/.tdd/workqueue"

if [[ "${1:-}" == next ]]; then
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    exec 3< "$VERI_GH_JSON/issues.json"
  else
    issues_json="$(gh_rest_list "repos/{owner}/{repo}/issues?state=all&per_page=100")"
    exec 3< <(printf '%s' "$issues_json")
  fi
  origin_url="$(git remote get-url origin 2>/dev/null || true)"
  origin_url="${origin_url%.git}"
  repo=""
  if [[ "$origin_url" =~ [:/]([^/:]+/[^/]+)$ ]]; then
    repo="${BASH_REMATCH[1]}"
  fi
  PYTHONPATH="$(cd "$(dirname "$0")" && pwd)/lib" exec python3 -c '
import json, sys

import blocked_by

text = sys.stdin.read().rstrip("\n")
issues, at, decoder = [], 0, json.JSONDecoder()
while at < len(text):
    page, at = decoder.raw_decode(text, at)
    issues.extend(page)
worker = sys.argv[1]
open_issues = {i["number"] for i in issues if i.get("state", "").upper() == "OPEN"}
bodies = {i["number"]: i.get("body") or "" for i in issues}
with open(sys.argv[2]) as f:
    for line in f:
        owner, issue, state = line.rstrip("\n").split("\t")[:3]
        if owner != worker or state != "queued":
            continue
        if all(n not in open_issues for n in blocked_by.blockers(bodies.get(int(issue), ""), sys.argv[3])):
            print(issue)
            sys.exit(0)
sys.exit(3)
' "$2" "$queue" "$repo" <&3 3<&-
fi

# hazard: BSD has no flock; mkdir is the atomic lock.
take_lock() {
  mkdir -p "$main_tree/.tdd"
  local tries=$(( ${VERI_WORKQUEUE_LOCK_WAIT:-30} * 20 ))
  until mkdir "$queue.lock" 2>/dev/null; do
    if (( tries-- <= 0 )); then
      echo "workqueue.sh: could not take the lock $queue.lock" >&2
      exit 2
    fi
    sleep 0.05
  done
  trap 'rmdir "$queue.lock" 2>/dev/null || true' EXIT
}

if [[ "${1:-}" == start || "${1:-}" == done || "${1:-}" == park ]]; then
  case "$1" in
    start) from=queued to=running new_detail="" ;;
    done)
      if [[ -z "${4:-}" ]]; then
        echo "workqueue.sh: usage: workqueue.sh done <worker> <issue> <merge-sha>" >&2
        exit 2
      fi
      from=running to=merged new_detail="$4" ;;
    park)
      if [[ "${4:-}" == *$'\t'* || "${4:-}" == *$'\n'* ]]; then
        echo "workqueue.sh: a park reason may not hold a tab or a newline" >&2
        exit 2
      fi
      from=running to=parked new_detail="$4" ;;
  esac
  take_lock
  tmp="$queue.tmp.$$"
  moved=0
  while IFS=$'\t' read -r owner issue state detail; do
    if [[ "$owner" == "$2" && "$issue" == "$3" && "$state" == "$from" ]]; then
      state="$to" detail="$new_detail" moved=1
    fi
    printf '%s\t%s\t%s\t%s\n' "$owner" "$issue" "$state" "$detail"
  done < "$queue" > "$tmp"
  if [[ "$moved" -eq 0 ]]; then
    rm -f "$tmp"
    echo "workqueue.sh: $2 holds no $from item for issue $3" >&2
    exit 1
  fi
  mv "$tmp" "$queue"
  exit 0
fi

if [[ "${1:-}" == show ]]; then
  awk -F '\t' -v only="${2:-}" '
    only != "" && $1 != only { next }
    !($1 in items) { order[++workers] = $1 }
    { items[$1] = items[$1] "\t" $2 "\t" $3 "\n" }
    END { for (w = 1; w <= workers; w++) printf "%s\n%s", order[w], items[order[w]] }
  ' "$queue"
  exit 0
fi

if [[ "${1:-}" != assign ]]; then
  echo "workqueue.sh: unknown subcommand: ${1:-}" >&2
  exit 2
fi

if [[ $# -lt 3 ]]; then
  echo "workqueue.sh: usage: workqueue.sh assign <worker> <issue>..." >&2
  exit 2
fi

worker="$2"
shift 2
declare -A named=()
for issue in "$@"; do
  if [[ -z "$issue" ]]; then
    echo "workqueue.sh: an issue argument is empty" >&2
    exit 2
  fi
  if [[ -n "${named[$issue]:-}" ]]; then
    echo "workqueue.sh: issue $issue is named twice" >&2
    exit 2
  fi
  named[$issue]=1
done
take_lock
if [[ -f "$queue" ]]; then
  while IFS=$'\t' read -r _ held state _; do
    [[ "$state" == queued || "$state" == running ]] || continue
    for issue in "$@"; do
      if [[ "$issue" == "$held" ]]; then
        echo "workqueue.sh: issue $issue is already $state" >&2
        exit 2
      fi
    done
  done < "$queue"
fi

for issue in "$@"; do
  printf '%s\t%s\tqueued\t\n' "$worker" "$issue" >> "$queue"
done
