# Plan for #388 — SKILL.md's Stopping section: the sequence a stopped run runs, and the `stop` event

- [x] SKILL.md has a `## Stopping` section that settles the leaves first — waiting with `wait-leaf.sh <name>` on every `.tdd/<name>.pid` still running `supervise.sh <name> ` before it touches the tree — and reaches only for `git reset --hard HEAD`, never `git checkout` ⟦criterion 1⟧
- [x] The Stopping section resets nothing and records `at=unsettled` when `rebase-merge`, `rebase-apply` or `MERGE_HEAD` is present in the worktree ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The Stopping section runs `push-branch.sh` and, on its exit 1, records `push=rejected` with the sha its stderr names, launching no reconcile leaf and bailing not at all ⟦criterion 3⟧
- [ ] The Stopping section writes exactly one `event.sh stop mode=<mode> at=<at>` mark, with `at` one of `unplanned`, `planned`, `green`, `step-done` or `unsettled`, and names `classify-bail.sh` nowhere ⟦criterion 4⟧
- [ ] The Stopping section renders `metrics.sh <n>` into a `### ⏹️ Stopped — <mode>` comment and commits no metrics file ⟦criterion 5⟧
- [ ] The Stopping section ends the run with `stop-requested.sh --clear`, opening no PR, removing no worktree and deleting no `.tdd/conductor.pid` ⟦criterion 6⟧
- [ ] SKILL.md's script reference list has an entry for `stop-requested.sh` saying what it prints and which exit codes it answers with, so the Stopping section's two calls read their contract where every other script's is read
