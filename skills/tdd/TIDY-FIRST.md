## A green report carrying `TIDY_FIRST:` — a tidy-first step ahead

A green leaf that sees the step would be one small change after a behaviour-preserving
restructuring of code already committed answers one `TIDY_FIRST: <refactoring> | <file>::<symbol> | <why>`
line in place of `IMPL_PATH:` and `SUITE:`, and leaves the working tree as it found it. Read the
answer with `$S/tidy-first.sh < .tdd/develop-green.out`:

- **Exit 0** prints the step to insert, ending `⟦diff-checked⟧`. Launch no verify-green: there is
  no implementation to judge. Discard the step's uncommitted work as the `prep` answer does
  (`REVISE.md`), then insert the printed step ahead of the stuck step with its `⟦criterion k⟧`
  tag (`add-ledger-step.sh` gives an inserted step its anchor's), commit the ledger, and write the
  `tidy-first` event beside the `step-added` one:
  ```
  git reset --hard HEAD
  git clean -f -- <test-path>
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$step" added=1; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh tidy-first anchor="$step" refactoring='<refactoring>'
  $S/add-ledger-step.sh .tdd/issue-<n>.md before "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<the printed step>' 2> .tdd/add-ledger-step.err
  git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: tidy first ahead of <STEP summary> (#<n>)"
  ```
  The two events go first because they read the stuck step's title, which the insertion moves.
  The inserted step runs as any `⟦diff-checked⟧` step does (`develop-diff`, then the blind `diff`
  verifier; `Read` `<base directory>/DIFF-CHECKED.md`). Once it is ticked, the stuck step starts
  again from Red, its revise loop at attempt 1.
  A `TIDY_FIRST:` answer spends no `REVISE_BUDGET` attempt and writes no `revise` mark for the
  stuck step: the budget is for a rejected product.
- **Exit 3**: the report has no `TIDY_FIRST:` line; go on as the green report would without it.
- **Exit 1** is a verify-green REJECT whose reason is the script's stderr line, spending
  `REVISE_BUDGET`, with no verifier launched: the leaf answered, wrongly (`Read`
  `<base directory>/REVISE.md`).
- **Exit 2**: no answer could be read (the smell catalogue unreadable), so **bail** as a system
  failure with cause `no-verdict` (`Read` `<base directory>/BAIL.md`).

The inserted step carries `⟦added⟧` and counts toward `VERI_STEP_GROWTH_PERCENT`, with no budget of
its own: `add-ledger-step.sh` exit **1** (the plan has no room; the script has parked the text under
`## Owed steps`) **bails** with cause `tidy-first-owed`, naming the refactoring; exit **2** bails
`step-add-refused`, adjudicated first as any insertion's exit 2 is (`Read`
`<base directory>/BAIL.md`). When the insertion succeeds, write no bail event.
