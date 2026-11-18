# Plan for #4389 — PRD 038.6: resume-start.sh starts a resume (RESUME.md 1-4) and the owed verify-plan in one call

- [x] resume-start.sh exits 2 on bad arguments or a missing .tdd/issue-<n>-preflight, ledger or .tdd/issue-<n>-run-start, before any call ⟦criterion 5⟧
- [ ] a clean resume runs next-pending-refactor.sh, next-unchecked.sh, the resume event, comment.sh resuming with a note naming the step and the stray paths, and reads the PR url off the branch, in order ⟦criterion 1⟧
- [ ] ledger-growth.sh record-existing runs and its record is committed only when the ledger holds steps beyond its plan commit and there is no .tdd/issue-<n>-added.md, and suite-red-resume.sh insert runs only when .tdd/resume-suite-red exists ⟦criterion 1⟧
- [ ] on exit 0 it writes .tdd/issue-<n>-resume-start with step=, pr_url= and verify_plan= and prints the same lines last ⟦criterion 4⟧
- [ ] verify_plan=owed launches verdict-plan after stop-requested.sh through detach-leaf.sh supervise.sh, waits, and comments on a PASS; skip launches nothing; events.jsonl is never opened ⟦criterion 2⟧
- [ ] a wait whose slice ran out exits 3 with a wait record, and a second call only waits again ⟦criterion 2⟧
- [ ] it stops with exit 1 naming the sub-step on a pending refactor, an unserved criterion, an insert exit 1 or 2, no open PR, and a verify-plan REJECT ⟦criterion 3⟧
- [ ] a stop writes no bail event, calls no classify-bail.sh and prints one line per call, never a leaf's output file ⟦criterion 5⟧
- [ ] RESUME.md names the call before sub-step 1 and SCRIPTS.md lists the script, graded by RS230 and SC585 ⟦criterion 6⟧
