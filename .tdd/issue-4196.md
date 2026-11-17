# Plan for #4196 — PRD 034.3a: stack-red.sh says whether CI's latest answer on the stack is red

- [x] github.workflow_runs reads the newest 100 workflow runs listed for a branch, this repository's only, as (head sha, url, status, conclusion, created at); a failed read or an answer not of the workflow-runs shape is NoAnswer ⟦criterion 4⟧
- [ ] stack-red.sh prints the head sha, url and conclusion of the newest completed run whose conclusion is failure or timed_out and exits 0 ⟦criterion 2⟧
- [ ] a newer run in progress, or one concluded cancelled, is skipped for an older completed one ⟦criterion 1⟧
- [ ] a success, neutral or skipped answer, or no completed not-cancelled run among the 100 (none, all in progress, all cancelled), is exit 3 with nothing on stdout and stderr saying which ⟦criterion 3⟧
- [ ] GitHub giving no answer or a garbled one, a fetch with no answer, and stack-branch.sh not exiting 0 (3 included) are exit 2 ⟦criterion 4⟧
- [ ] stack-red.sh is a /bin/sh shim over veri/stack_red.py; veri/README.md indexes it; a process case runs the shim ⟦criterion 5⟧
- [ ] the module names no repository, issue, branch, label, person or CI job ⟦criterion 6⟧
- [ ] SCRIPTS.md lists stack-red.sh (SC250), graded ⟦criterion 7⟧
