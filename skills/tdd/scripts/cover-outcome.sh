#!/usr/bin/env bash
# cover-outcome.sh — say whether a cover leaf found the code a refactor step will move
# covered.
#
# Reads a cover leaf's report on stdin. The leaf mutated the behaviour by hand, ran the
# suite and restored the edit; it ends with `COVERED: yes|no` and a `CAUGHT_BY:` line
# naming the test that went red under the mutation.
#
# Usage:   cover-outcome.sh < <the leaf's report>
#
# stdout:  on COVERED: yes, the test the CAUGHT_BY: line names; on COVERED: unreachable
#          or type-only, `<kind>: <proof>` from the PROOF: line.
# exit:    0 COVERED: yes · 1 COVERED: no · 2 no readable COVERED: line, or
#          unreachable|type-only with no PROOF: line or PROOF: NONE
#          3 COVERED: unreachable|type-only, proved without a test
set -uo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"

covered="" caught_by="" proof=""
while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    "COVERED: "*)   covered="${line#COVERED: }" ;;
    "CAUGHT_BY: "*) caught_by="${line#CAUGHT_BY: }" ;;
    "PROOF: "*)     proof="${line#PROOF: }" ;;
  esac
done

case "$covered" in
  yes) printf '%s\n' "$caught_by" ;;
  no)  exit 1 ;;
  unreachable|type-only)
    if [[ -z "$proof" || "$proof" == NONE ]]; then
      echo "cover-outcome: COVERED: $covered without a PROOF: line" >&2; exit 2
    fi
    printf '%s: %s\n' "$covered" "$proof"; exit 3 ;;
  *)   echo "cover-outcome: no COVERED: line found" >&2; exit 2 ;;
esac
