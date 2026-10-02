#!/usr/bin/env bash
# cover-outcome.sh — say whether a cover leaf found the code a refactor step will move
# covered.
#
# Reads a cover leaf's report on stdin. The leaf mutated the behaviour by hand, ran the
# suite and restored the edit; it ends with `COVERED: yes|no` and a `CAUGHT_BY:` line
# naming the test that went red under the mutation. A step no test can observe may instead
# end `COVERED: unreachable` — it only deletes code no caller reaches — or `COVERED:
# type-only` — it changes only types — with a `PROOF:` line standing in for the red test:
# the callers, or the type-check command the conductor reruns after the transform.
#
# Usage:   cover-outcome.sh < <the leaf's report>
#
# stdout:  on COVERED: yes, the test the CAUGHT_BY: line names; on unreachable or type-only,
#          `<kind>: <the PROOF: line>`.
# exit:    0 COVERED: yes · 1 COVERED: no · 2 no readable COVERED: line, or unreachable or
#          type-only with no proof · 3 unreachable or type-only — nothing a test can observe
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
  unreachable | type-only)
    if [[ -z "$proof" || "$proof" == NONE ]]; then
      echo "cover-outcome: COVERED: $covered with no PROOF: line" >&2; exit 2
    fi
    printf '%s: %s\n' "$covered" "$proof"; exit 3 ;;
  *)   echo "cover-outcome: no COVERED: line found" >&2; exit 2 ;;
esac
