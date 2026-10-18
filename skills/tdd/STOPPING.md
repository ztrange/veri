## Stopping

A **stop** is not a bail. A bail ends an issue; a stop pauses one, at an operator's word —
`stop-requested.sh` printed a mode (`at-ledger`, `at-leaf` or `now`) at a checkpoint — and
leaves the run resumable. Run this sequence in order.

1. **Settle the leaves before you touch the tree.** A live leaf owns the working tree
   (#170), so reset nothing while any `.tdd/<name>.pid` names a process still running
   `supervise.sh <name> …`. For each one that does, call `$S/wait-leaf.sh <name>` — again on
   an exit 3, as everywhere else — until it returns 0, 1 or 2. Under mode `now` that wait
   ends at once: `stop-run.sh` has already sent that supervisor its TERM, and
   `supervise.sh:350-355` recorded a 2 in the completion file.
2. **Settle the tree.** Ask first whether it is the run's to settle. If `git rev-parse
   --git-path rebase-merge` or `git rev-parse --git-path rebase-apply` names a directory
   that exists, or `MERGE_HEAD` resolves, an interrupted rebase or merge is in progress:
   **reset nothing**, record `at=unsettled`, say in the comment what a human must finish
   (`git rebase --continue` or `--abort`, `git merge --abort`) and skip the rest of this
   step. Dropping that tree would throw away conflict resolutions no commit holds yet, and
   `git reset --hard HEAD` cannot put a half-finished rebase back.
   Otherwise, and only with `git reset --hard HEAD` — a non-empty `git
   status --porcelain` is the half-done step, dropped exactly as *Bailing* step 1 drops it
   and for the reason given there. That reset is the only reach for the tree this section
   has: restoring a path out of some other tree is not what dropping a half-done step
   means. Say in the narration what was dropped.
3. **Push the branch**, `$S/push-branch.sh`, so the run's commits and leaf logs live
   somewhere a resume can reach. Exit **0** is the normal path. Exit **1** — the remote
   holds a branch this HEAD does not fast-forward — is answered here by **recording it, not
   by fixing it**: take the remote's sha from the script's stderr, record
   `push=rejected sha=<remote-sha>` and say so in the comment. A stop launches no leaves, so
   the reconcile leaf `<base directory>/RECONCILE.md` would otherwise launch (read it when that event happens) is not an option;
   and a stop has no cause, so a rejected push is not a bail either — the run stays paused
   and resumable, and the resume reconciles. Exit **2** is recorded the same way.
4. **Mark the stop**, exactly once, with the boundary the run actually reached. `<at>` is
   read off the committed ledger: `at=unplanned` when there is no ledger yet, `at=planned`
   when the ledger is committed and no step is green, `at=green` when the newest ledger
   commit ticked a step that still carries `⟂ refactor pending`, `at=step-done` when every
   ticked step has had that mark taken off again, and `at=unsettled` when step 2 refused the
   tree — that last one wins over the others, because where the tree stands is the first
   thing a resume has to deal with.
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/event.sh stop mode=<mode> at=<at>
   ```
   That is the whole record of the pause, and it is never a `bail` mark: a stop has no
   cause, so there is no system-versus-process label to derive and nothing to derive it
   from. Both keys ride on the one line — `mode` says which checkpoint the operator's stop
   was taken at, `at` says how far the work got — so a reader who asks "where did this run
   pause?" reads one mark, not two.
5. **Report.** Render `$S/metrics.sh <n>` — after the mark, so it reads it — straight into
   a `### 📊 Metrics` block, and post one `### ⏹️ Stopped — <mode>` comment carrying that
   block, the boundary reached (`at=<at>`), what step 2 dropped, the branch, the worktree
   path, any `push=rejected sha=<remote-sha>`, and the resume command
   `$S/run-conductor.sh <n>`. The metrics go into the comment and nowhere else: **no
   metrics file is written or committed**. Committing them marks an ending, as *Done* and
   *Bailing* do, and a stopped run will be resumed.
6. **Clear and end.** Run `$S/stop-requested.sh --clear`, so the request does not outlive
   the stop it asked for and pause the resumed run at its first checkpoint, then end the
   run. Open **no** PR and ready none; leave the worktree where it is; leave
   `.tdd/conductor.pid` in place. The resume picks all three up, and liveness is the whole
   rule (step 1.2): the conductor exiting is what frees the issue.
