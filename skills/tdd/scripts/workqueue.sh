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
# Exit:    0 done, 2 an unknown subcommand or an issue already queued or running for any
#          worker — refused before anything is written, so the file is left byte-identical
set -euo pipefail

# shellcheck source=lib/main-working-tree.sh
source "$(dirname "$0")/lib/main-working-tree.sh"

main_tree="$(main_working_tree)"
queue="$main_tree/.tdd/workqueue"

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
