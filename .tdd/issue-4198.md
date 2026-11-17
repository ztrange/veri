# Plan for #4198 — PRD 034.3b: one command names the issue that turned the stack red, and the cases it broke

- [x] github.run_failed_log reads a workflow run's failed-job log (gh run view <id> --log-failed); NoAnswer when gh gives none ⟦criterion 1⟧
- [x] stack-culprit.sh reads the red cases from the failed log of the newest completed, not-cancelled run on <red-sha>, named by rerun-alone.sh's rule from the log as ci-flake.sh reads it, and runs at most the first 5, saying on stderr how many it did not run ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] the commits tested are the issue ends (next commit toward the tip belongs to another issue) from the newest tested KT5 issue end at or below <red-sha> (origin/<default> when none) to <red-sha>, an issue end inside another issue's KT5 span included ⟦criterion 3⟧
- [x] each case runs alone through the one-test-file command, oldest end first, in a detached worktree of its own under .tdd/, removed on every exit; a worktree that cannot be added is exit 2 with nothing run ⟦criterion 4⟧
- [x] a case is red at a commit when its file exists there and its alone run exits 1; 0, 4, 5 or the file absent is not red; any other exit or no exit within VERI_TIMEOUT is exit 2 ⟦criterion 5⟧
- [ ] at the first issue end with a red case it prints the red sha, the end's issue, that commit, the end before it and each red case with its first FAIL line, and exits 0 ⟦criterion 6⟧
- [ ] no issue end turning a case red is exit 3, nothing on stdout, stderr naming the cases run ⟦criterion 7⟧
- [ ] an unreadable log or one naming no case, a <red-sha> not on origin/<default>..origin/<stack>, no answer from GitHub or a fetch, and stack-branch.sh not exiting 0 are exit 2 ⟦criterion 8⟧
- [ ] on exit 0 or 3 it comments once on the stack's tracking pull request with what it printed and the red run's url, never twice for the same answer; with none open it says on stderr no comment was posted ⟦criterion 9⟧
- [ ] stack-culprit.sh is a /bin/sh shim over veri/stack_culprit.py, indexed in veri/README.md, run as a process ⟦criterion 10⟧
- [ ] the module names no repository, issue, branch, label, person or CI job ⟦criterion 11⟧
- [ ] SCRIPTS.md lists stack-culprit.sh (SC252), graded ⟦criterion 12⟧
