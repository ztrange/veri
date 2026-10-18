## Reconciling a rejected push

`push-branch.sh` exit **1** means the remote holds a branch the run's HEAD does not
fast-forward — usually the run's own pre-rebase history, after a resume rebased onto
`origin/main`. Its stderr names the remote's sha. Whether those remote commits are the run's
own or someone else's is a judgement, so a leaf makes it, launched **through the
supervisor** like every other:

```
cp .tdd/issue-<n>.md .tdd/reconcile-ledger.before
$S/build-develop-prompt.sh reconcile .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' <branch> <remote-sha> > .tdd/develop-reconcile.prompt
rm -f .tdd/develop-reconcile.exit .tdd/develop-reconcile.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh develop-reconcile $S/run-leaf.sh .tdd/develop-reconcile.prompt --permission-mode bypassPermissions > .tdd/develop-reconcile.out 2> .tdd/develop-reconcile.err
$S/wait-leaf.sh develop-reconcile   # foreground; on exit 3 call it again
```

After the leaf exits 0, re-run `$S/push-branch.sh` — it must now exit 0 — and check the
committed ledger `.tdd/issue-<n>.md` still carries every `[x]` tick and every
` ⟂ refactor pending` mark `.tdd/reconcile-ledger.before` had:

```
diff <($S/ledger-steps.sh < .tdd/reconcile-ledger.before | awk -F'\t' '$2 == "done" {print $4 "\t" $7}') <(git show HEAD:.tdd/issue-<n>.md | $S/ledger-steps.sh | awk -F'\t' '$2 == "done" {print $4 "\t" $7}')
```

Then continue where the push was called. A leaf exit 1 or 2, a second `push-branch.sh` exit
other than 0, or a ledger whose ticks or marks changed → **bail** with cause
`reconcile-failed` (a system failure: where the branch lives broke, not the methodology).
