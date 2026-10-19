#!/bin/sh
# pin-fast-tier.sh — run the fast tier over the tree a pin would commit; run from the worktree.
#
# usage: pin-fast-tier.sh <fast-cmd>
#
# On failure the command's own output is written to .tdd/verify-pin.reason.
#
# Exit: 0 the fast command passed,
#       1 it failed (output in .tdd/verify-pin.reason),
#       2 no command given.
if [ $# -lt 1 ] || [ -z "$1" ]; then
  echo "usage: pin-fast-tier.sh <fast-cmd>" >&2
  exit 2
fi
mkdir -p .tdd
if out="$(sh -c "$1" 2>&1 < /dev/null)"; then
  exit 0
fi
printf '%s\n' "$out" > .tdd/verify-pin.reason
exit 1
