#!/bin/sh
# tests-frozen.sh — record a step's test files, then check that none of them has changed: a shim over veri/tests_frozen.py.
#
# usage: tests-frozen.sh record <record-file>|--step <step-text> [--red-case <red-test-id>] <test-file>...
#        tests-frozen.sh check <record-file>|--step <step-text>
#        tests-frozen.sh diff --step <step-text>
#        tests-frozen.sh snapshot --step <step-text>
#        tests-frozen.sh check-earlier <ledger> --step <step-text> [--except <case>]...
#        tests-frozen.sh rerecord-earlier <ledger> --step <step-text>
#        tests-frozen.sh rerecord-refactored <ledger> <green-sha>
#        tests-frozen.sh rerecord-rebased <ledger> <pre-rebase-sha>
#        tests-frozen.sh rerecord-approved <ledger> --approval <text> <case>...
#        tests-frozen.sh path <step-text>
#
# path prints the step's record file, .tdd/tests-frozen-<k>.record, where <k> is the first 16 hex
# digits of the SHA-256 of the step text: a step text is often longer than a filename may be and
# may hold a "/", so the text itself is never the filename. --step <step-text> in place of a record
# file uses that path. A step marked ⟦suite-repair⟧ or ⟦ci-repair⟧ is never frozen: for it record
# --step writes nothing and check --step exits 0, because its fix is often an edit to the very test
# file the full run or CI left red.
# A step marked ⟦fixture-repair⟧ is frozen like any other step except for the fixture file its step
# text names, which Green may edit outside its recorded cases, on two conditions: every recorded case
# body in that file stays unchanged, and the record holds at least one case body for that file; a
# fixture file the record holds no case bodies for is flagged like any other.
# A step marked ⟦guard-subject: <path>⟧ may change the file it
# names (any other unrecorded test file is still flagged); the case pinning the behaviour stays frozen.
#
# rerecord-approved re-records exactly the named cases of the earlier records at their HEAD bodies, each with its
# helpers: line, on a human's non-empty --approval text, and logs one tests-frozen-rerecord-approved event per case
# (case, file, approval). A case is named <file>::<case>, or by a bare case name that must match exactly one recorded
# case. Exit 0 re-recorded; 2 no answer: no case or approval given, a named case no record holds or absent at HEAD, a
# bare name matching more than one recorded case (each match named; nothing written), or a record that cannot be written (every rewritten record restored).
#
# rerecord-earlier, for a ⟦diff-checked⟧ step, rewrites the earlier steps' frozen records of the cases
# that step's own diff (step base..HEAD) changed, at their content at HEAD; any other step exits 3.
#
# Exit: 0 recorded, the path printed, or every recorded file is byte-identical (nothing on stdout),
#       1 with one path per line on stdout for each recorded file edited or deleted,
#       2 bad arguments (a missing ledger or --step for check-earlier, an empty step text included) or an unreadable record/file;
#         for check-earlier also a ledger that is not the run's .tdd/issue-<n>.md when the issue is known (VERI_ISSUE,
#         else a tdd/<n>- branch), named on stderr with no pass marker written;
#         for rerecord-earlier also a ledger no commit touches (no step base), a git show of a recorded file that
#         fails, or a record that cannot be written,
#       3 rerecord-earlier given a step that is not ⟦diff-checked⟧.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/tests_frozen.py" "$@"
