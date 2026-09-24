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
# Exit:    0 done, 3 `next` found nothing launchable, 2 an unknown subcommand or an issue
#          already queued or running for any worker — refused before anything is written,
#          so the file is left byte-identical
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

if [[ "${1:-}" != assign ]]; then
  echo "workqueue.sh: unknown subcommand: ${1:-}" >&2
  exit 2
fi

worker="$2"
shift 2
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

mkdir -p "$main_tree/.tdd"
for issue in "$@"; do
  printf '%s\t%s\tqueued\t\n' "$worker" "$issue" >> "$queue"
done
