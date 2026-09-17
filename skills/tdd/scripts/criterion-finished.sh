#!/usr/bin/env bash
# criterion-finished.sh — say whether an issue acceptance criterion is finished.
#
# Reads a ledger (checkbox markdown) on stdin. A step serves criterion k when its line ends
# in ` ⟦criterion k⟧`, optionally followed by the ` ⟂ refactor pending` mark that
# tick-ledger.sh --refactor-pending appends after it. Exits 0 when every such step is ticked with no ` ⟂ refactor pending`
# mark, and 3 when some step serving k is still open or pending.
#
# Usage:   criterion-finished.sh <k> < .tdd/issue-<n>.md
set -euo pipefail

k="$1"
tag=" ⟦criterion ${k}⟧"
pending=" ⟂ refactor pending"
done_re="^[[:space:]]*- \[x\] .*${tag}$"
step_re="^[[:space:]]*- \[.\] .*${tag}(${pending})?$"

while IFS= read -r line || [[ -n "$line" ]]; do
  if [[ "$line" =~ $step_re && ! "$line" =~ $done_re ]]; then
    exit 3
  fi
done

exit 0
