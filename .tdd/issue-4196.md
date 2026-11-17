# Plan for #4196 — PRD 034.3a: stack-red.sh says whether CI's latest answer on the stack is red

- [x] github.workflow_runs reads the newest 100 workflow runs listed for a branch, this repository's only, as (head sha, url, status, conclusion, created at); a failed read or an answer not of the workflow-runs shape is NoAnswer ⟦criterion 4⟧
- [x] stack-red.sh prints the head sha, url and conclusion of the newest completed run whose conclusion is failure or timed_out and exits 0 ⟦criterion 2⟧
- [x] a newer run in progress, or one concluded cancelled, is skipped for an older completed one ⟦criterion 1⟧
- [x] a success, neutral or skipped answer, or no completed not-cancelled run among the 100 (none, all in progress, all cancelled), is exit 3 with nothing on stdout and stderr saying which ⟦criterion 3⟧
- [x] GitHub giving no answer or a garbled one, a fetch with no answer, and stack-branch.sh not exiting 0 (3 included) are exit 2 ⟦criterion 4⟧
- [x] stack-red.sh is a /bin/sh shim over veri/stack_red.py; veri/README.md indexes it; a process case runs the shim ⟦criterion 5⟧
- [x] the module names no repository, issue, branch, label, person or CI job ⟦criterion 6⟧
- [x] SCRIPTS.md lists stack-red.sh (SC250), graded ⟦criterion 7⟧
- [x] (amended) with the newest non-cancelled run not completed, the newest completed non-cancelled run on the same head answers, else the branch's ⟦criterion 8⟧
- [x] (amended) a re-run in progress (run_attempt > 1) is answered by its previous attempt, read from GitHub; an unreadable one is exit 2 ⟦criterion 8⟧
