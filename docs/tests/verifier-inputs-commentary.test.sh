#!/usr/bin/env bash
# The commentary describes build-verify-prompt.sh's inputs as a property of every input, and
# quotes no sentence the script no longer holds (#2525).
set -u
cd "$(dirname "$0")/../.." || exit 2
fail=0
for stale in 'built from two inputs' "only inputs are the" 'no third arrow'; do
  if grep -q "$stale" docs/wt/commentary.py; then
    echo "FAIL - docs/wt/commentary.py still says: $stale"
    fail=1
  fi
done
[ "$fail" = 0 ] && echo "ok - the verifier's inputs are described as they are"
exit "$fail"
