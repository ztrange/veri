#!/bin/sh
# test-quality.sh — the test files a run touched, and the develop-test-quality leaf's findings recorded:
# a shim over veri/quality_findings.py.
#
# usage: test-quality.sh files <branch-base>              (prints the test files <branch-base>..HEAD names that exist)
#        test-quality.sh anchor <ledger>                 (prints the last done step with one criterion tag)
#        test-quality.sh record <n> < <leaf-report>       (run from the worktree; writes .tdd/issue-<n>-test-quality)
# Exit:  files: 0 printed; 3 none; 2 git could not answer, or bad arguments
#        anchor: 0 printed; 3 none, or a step carries two criterion tags; 2 unreadable ledger
#        record: 0 findings recorded, each refused finding (no <file>::<case>, a kind or a why, or a case its file
#        does not define) skipped and named on stderr; 3 FINDING: none, the file written with no finding;
#        2 nothing written: bad arguments, no FINDING: line, or every finding refused
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/quality_findings.py" "$@"
