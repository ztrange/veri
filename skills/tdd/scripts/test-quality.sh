#!/bin/sh
# test-quality.sh — the test files a run touched, and the develop-test-quality leaf's findings recorded:
# a shim over veri/quality_findings.py.
#
# usage: test-quality.sh files <branch-base>              (prints the test files <branch-base>..HEAD names that exist)
#        test-quality.sh record <n> < <leaf-report>       (run from the worktree; writes .tdd/issue-<n>-test-quality.md)
# Exit:  files: 0 printed; 3 none; 2 git could not answer, or bad arguments
#        record: 0 findings recorded; 3 FINDING: none, the file written with no finding;
#        2 nothing written: bad arguments, no FINDING: line, or a line naming no <file>::<case> or a case its file does not define
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/quality_findings.py" "$@"
