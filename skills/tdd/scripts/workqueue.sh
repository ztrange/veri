#!/usr/bin/env bash
# workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns issues to named
# workers and records what happened to each (issue #271).
#
# The file lives under the repository's MAIN working tree, resolved the way
# solvable-issues.sh resolves it (lib/main-working-tree.sh, #166), so every worktree of the
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
#          naming no worker or no issue, an empty issue, or naming one issue twice, an issue
#          already queued or running for any worker, or a lock not taken within
#          VERI_WORKQUEUE_LOCK_WAIT seconds — refused before anything is written, so the file
#          is left byte-identical
set -euo pipefail

# shellcheck source=lib/main-working-tree.sh
source "$(dirname "$0")/lib/main-working-tree.sh"

main_tree="$(main_working_tree)"
queue="$main_tree/.tdd/workqueue"

# `next` prints the worker's first `queued` issue whose `## Blocked by` names no open issue,
# and exits 3 printing nothing when none of the worker's `queued` items is launchable.
# The issues come from `gh`, or from `$VERI_GH_JSON/issues.json` the way solvable-issues.sh
# reads its fixtures, and the section is read by lib/blocked_by.py (#460), not a copy of it.
if [[ "${1:-}" == next ]]; then
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    issues_json="$(cat "$VERI_GH_JSON/issues.json")"
  else
    issues_json="$(gh issue list --state all --limit 10000 --json number,body,state)"
  fi
  # This repository's owner/name, which blocked_by.blockers compares a `## Blocked by` URL
  # against the way solvable-issues.sh does: read off `origin`'s URL — `https://github.com/
  # <owner>/<name>.git` or `git@github.com:<owner>/<name>.git` — and empty with no origin,
  # which reads any github.com issue URL as local.
  origin_url="$(git remote get-url origin 2>/dev/null || true)"
  origin_url="${origin_url%.git}"
  repo=""
  if [[ "$origin_url" =~ [:/]([^/:]+/[^/]+)$ ]]; then
    repo="${BASH_REMATCH[1]}"
  fi
  PYTHONPATH="$(cd "$(dirname "$0")" && pwd)/lib" exec python3 -c '
import json, sys

import blocked_by

issues = json.loads(sys.argv[1])
worker = sys.argv[2]
open_issues = {i["number"] for i in issues if i.get("state", "").upper() == "OPEN"}
bodies = {i["number"]: i.get("body") or "" for i in issues}
with open(sys.argv[3]) as f:
    for line in f:
        owner, issue, state = line.rstrip("\n").split("\t")[:3]
        if owner != worker or state != "queued":
            continue
        if all(n not in open_issues for n in blocked_by.blockers(bodies.get(int(issue), ""), sys.argv[4])):
            print(issue)
            sys.exit(0)
sys.exit(3)
' "$issues_json" "$2" "$queue" "$repo"
fi

# Every write holds the lock — a directory beside the queue, since `mkdir` either creates it
# or fails, atomically, where BSD has no flock — so concurrent workers never read the file
# while another is rewriting it and lose that write. A writer waits at most
# VERI_WORKQUEUE_LOCK_WAIT seconds (default 30) for it, then exits 2 having written nothing:
# a lock left behind by a killed writer must end in an error someone reads, not a hang.
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

# `start` moves the worker's `queued` line for the issue to `running`, `done` its `running`
# line to `merged` with the sha as its detail and `park` it to `parked` with the reason, in place: every line keeps its
# position, and the new file replaces the old one by `mv` from beside it.
if [[ "${1:-}" == start || "${1:-}" == done || "${1:-}" == park ]]; then
  case "$1" in
    start) from=queued to=running new_detail="" ;;
    done) from=running to=merged new_detail="$4" ;;
    park) from=running to=parked new_detail="$4" ;;
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
  # No line of this worker's was in the `from` state: a clean refusal, and the file is left
  # as it was rather than replaced.
  if [[ "$moved" -eq 0 ]]; then
    rm -f "$tmp"
    echo "workqueue.sh: $2 holds no $from item for issue $3" >&2
    exit 1
  fi
  mv "$tmp" "$queue"
  exit 0
fi

# `show` prints the queue grouped by worker: the worker's name on a line of its own, then one
# tab-indented `<issue>\t<state>` line per item of that worker's, in file order. Workers come
# in the order they first appear in the file. `show <worker>` prints that worker's group alone.
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

# A call naming no worker, or a worker and no issue, is refused before the lock is taken:
# an assignment of nothing is a caller's mistake, not a no-op.
if [[ $# -lt 3 ]]; then
  echo "workqueue.sh: usage: workqueue.sh assign <worker> <issue>..." >&2
  exit 2
fi

worker="$2"
shift 2
# One call naming an issue twice would queue it twice, which two calls are refused: the
# same mistake, refused the same way, before anything is written.
declare -A named=()
for issue in "$@"; do
  # An empty word names no issue: queuing it would write a line with no issue field.
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
