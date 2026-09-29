#!/usr/bin/env bash
# criterion-finished.sh — say whether an issue acceptance criterion is finished.
#
# Reads a ledger (checkbox markdown) on stdin; the step grammar is lib/ledger.sh's
# `ledger_steps`. A step serves criterion k when it carries `⟦criterion k⟧`. Exits 0 when
# every such step is done and not refactor-pending, and 3 when some step serving k is
# still open or pending — or when no step serves k at all, since a ticked step carrying no
# token finishes no criterion.
#
# Usage:   criterion-finished.sh <k> < .tdd/issue-<n>.md
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: criterion-finished.sh <k> < .tdd/issue-<n>.md" >&2; exit 2; }
k="$1"

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/ledger.sh"

served=0
while IFS= read -r record; do
  mapfile -td $'\t' field <<< "$record"
  [[ "${field[5]}" == "$k" ]] || continue
  served=1
  [[ "${field[1]}" == done && "${field[3]}" == 0 ]] || exit 3
done < <(ledger_steps)

[[ "$served" -eq 1 ]] || exit 3
exit 0
