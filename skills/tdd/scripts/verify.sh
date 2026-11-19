#!/bin/sh
# verify.sh — run one blind verification of a cycle phase and return its verdict: a shim over veri/verify.py.
#
# usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>] --branch-base <sha> <phase> <issue-spec-file> <test-path> [<target-test-id>]
#          --branch-base is the run's recorded branch base (hex, 7-40 chars); every phase but diff exits 2 without it
#          phase = red | green | refactor | pin | plan | diff
#          for diff the third positional is <branch-base-sha> and the fourth <step-base-sha>:
#          verify.sh --step '<STEP>' diff <issue-spec-file> <branch-base-sha> <step-base-sha>
#
# stdout: the verifier's reason.
# exit:   0 PASS · 1 REJECT · 2 malformed verdict, killed-stuck, a leaf that modified the
#         repository or ~/.gitconfig, a bad argument, or a build error
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/verify.py" "$@"
