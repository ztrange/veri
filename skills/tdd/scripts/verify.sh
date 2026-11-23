#!/bin/sh
# verify.sh — run one blind verification of a cycle phase and return its verdict: a shim over veri/verify.py.
#
# usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>] [--step-green <sha>] --branch-base <sha> <phase> <issue-spec-file> <test-path> [<target-test-id>]
#          --branch-base is the run's recorded branch base (hex, 7-40 chars); every phase, diff included, exits 2 without it
#          --step-green is the step's green tick: refactor exits 2 without it, every other phase exits 2 with it (#4544)
#          phase = red | green | refactor | pin | plan | diff
#          diff takes the run's branch base from --branch-base, and <step-base-sha> as its one sha positional:
#          verify.sh --step '<STEP>' --branch-base <sha> diff <issue-spec-file> <step-base-sha>
#          branch judges the whole branch and names no test: verify.sh --fast-cmd '<CMD>' --branch-base <sha> branch <issue-spec-file>
#
# stdout: the verifier's reason.
# exit:   0 PASS · 1 REJECT · 2 malformed verdict, killed-stuck, a leaf that modified the
#         repository or ~/.gitconfig, a bad argument, or a build error
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/verify.py" "$@"
