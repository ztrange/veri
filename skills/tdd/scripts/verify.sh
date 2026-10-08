#!/bin/sh
# verify.sh — run one blind verification of a cycle phase and return its verdict: a shim over veri/verify.py.
#
# usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#        verify.sh --step '<STEP>' diff <issue-spec-file> <branch-base-sha> <step-base-sha>
#          phase = red | green | refactor | pin | diff
#
# stdout: the verifier's reason.
# exit:   0 PASS · 1 REJECT · 2 malformed verdict, killed-stuck, a leaf that modified the
#         repository or ~/.gitconfig, a bad argument, or a build error
exec python3 "$(dirname "$0")/veri/verify.py" "$@"
