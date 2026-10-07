#!/bin/sh
# cover-outcome.sh — say whether a cover leaf found the code a refactor step will move covered: a shim over veri/cover_outcome.py.
#
# Reads a cover leaf's report on stdin. The leaf mutated the behaviour by hand, ran the
# suite and restored the edit; it ends with `COVERED: yes|no` and a `CAUGHT_BY:` line
# naming the test that went red under the mutation.
#
# usage: cover-outcome.sh (the cover leaf's report on stdin)
#
# stdout:  on COVERED: yes, the test the CAUGHT_BY: line names; on COVERED: unreachable
#          or type-only, `<kind>: <proof>` from the PROOF: line.
# exit:    0 COVERED: yes · 1 COVERED: no · 2 no readable COVERED: line, or
#          unreachable|type-only with no PROOF: line or PROOF: NONE
#          3 COVERED: unreachable|type-only, proved without a test
exec python3 "$(dirname "$0")/veri/cover_outcome.py" "$@"
