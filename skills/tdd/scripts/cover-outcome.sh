#!/usr/bin/env bash
# cover-outcome.sh — say whether a cover leaf found the code a refactor step will move
# covered.
#
# Reads a cover leaf's report on stdin. The leaf mutated the behaviour by hand, ran the
# suite and restored the edit; it ends with `COVERED: yes|no` and a `CAUGHT_BY:` line
# naming the test that went red under the mutation (issue #499).
#
# Usage:   cover-outcome.sh < <the leaf's report>
#
# stdout:  on COVERED: yes, the test the CAUGHT_BY: line names.
# exit:    0 COVERED: yes · 1 COVERED: no · 2 no readable COVERED: line
set -uo pipefail

covered="" caught_by=""
while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    "COVERED: "*)   covered="${line#COVERED: }" ;;
    "CAUGHT_BY: "*) caught_by="${line#CAUGHT_BY: }" ;;
  esac
done

case "$covered" in
  yes) printf '%s\n' "$caught_by" ;;
  no)  exit 1 ;;
  *)   echo "cover-outcome: no COVERED: line found" >&2; exit 2 ;;
esac
