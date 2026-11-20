## A `⟦go-red⟧` step — a mutation probe on its named case

Run `$S/run-step.sh <n>`, again on exit 3: it runs `go-red-step.sh`, this section in one call,
and on 1 or 2 its last line names where it stopped.

A go-red guard step carries `⟦go-red⟧` among the markers that end its line and names its probe as
``probe `<file>` `<old>` → `<new>` on `<case>` ``: the
guard broken on purpose (`<old>` replaced by `<new>` in `<file>`) and the existing case that must
go red under it. It runs no Red leaf, no Green and no Refactor, and adds no test: the case is
already pinned, and what the step owes is the evidence that it guards. `go-red-step.sh` runs
`mutation-probe.sh` on that case with the `veri: one test file:` command (a repository without
that line gets exit 2, never the whole suite, whose red could come from another case), which breaks the file,
watches the case go red, restores the file and appends the probe to
`.tdd/issue-<n>-mutations.md`; then `step-tick.sh <n>` ticks the step against that record and
commits it under `test: go-red — <STEP summary> (#<n>)`. `tick-ledger.sh` exits 2 on a
`⟦go-red⟧` step unless the record holds an entry of its own probe (the same file, old and new, its
command naming the case), so no go-red step is ticked without its probe.

- **Exit 1** ticks nothing, and its last line says which:
  - `stopped at probe <case> stayed green …`: the case does not catch the break, so the guard is
    not guarded. Bail with `cause=needs-user` (`<base directory>/BAIL.md`): the plan named a break
    its case cannot see, and only the human can say whether the case or the break is wrong.
  - ``stopped at probe <file> no longer holds `<old>` ``: neither a bail. The step's probe is stale,
    so rewrite it against `<file>` as it now stands, commit the rewrite as a `plan: rewrite`
    commit, have verify-plan check it, then rerun the step.
- **Exit 2** ticks nothing: no open `⟦go-red⟧` step, a step naming no probe, no `veri: one test file:` line,
  the case already red on the unmutated file, a probe or `detect-test-command.sh` exit 2, the file
  not restored, or any `step-tick.sh` exit but 0 (a stray file its tree check finds included):
  plumbing, never the case staying green. Bail as a system failure.
