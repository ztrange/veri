# Plan for #4409 — PRD 033.2b: an Opus session may skip the local gate, and a red gate over a skipped join freezes the local stack

- [x] `--skip-suite <model-id> <reason>` with an id naming neither `opus` nor `fable`, or no reason, is exit 2 before the lock, nothing happening ⟦criterion 1⟧
- [x] `--skip-suite` with `.tdd/github-outage` absent, or a join that is not offline, is exit 2 before the lock, nothing happening ⟦criterion 1⟧
- [x] `--skip-suite` on an offline join runs no gate and the amend writes `Veri-Suite: skipped <model-id> <reason>` ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] the offline join's amend writes `Veri-Suite: passed` after a green gate and `Veri-Suite: not gated` with no all-tier command ⟦criterion 2⟧
- [x] `stack-red.sh` while the outage file exists makes no GitHub call: `.tdd/stack-local-red` present prints `<sha> <path> local`, exit 0; absent exit 3; an unreadable file or no stack named exit 2 ⟦criterion 4⟧
- [x] the offline join runs `stack-red.sh` before its rebase: exit 0 refuses (exit 1) naming the file, any exit but 0 and 3 is exit 2 ⟦criterion 4⟧
- [x] a red gate while a commit of `origin/<stack>..<stack>` carries `Veri-Suite: skipped` writes `.tdd/stack-local-red` (the gated sha, the failed cases); with none it writes nothing ⟦criterion 3⟧
- [x] `--local-green` outside an outage is exit 2; with no `.tdd/stack-local-red` exit 3; else under the merge lock it runs the all-tier command on `<stack>`'s tip in a worktree it adds and removes: green removes the file (exit 0), red keeps it (exit 1) ⟦criterion 5⟧
- [ ] the graded prose of vdev, vmerge and SCRIPTS.md says what D152, M45, SC596 and SC599 say, each regraded ⟦criterion 6⟧
- [ ] the logic lives in `queued_merge.py` and `stack_red.py` behind their shims and names no repository, issue, branch, label or person ⟦criterion 7⟧
