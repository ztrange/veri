## A `⟦go-red⟧` step — a mutation probe on its named case

Run `$S/run-step.sh <n>`, again on exit 3: it runs `go-red-step.sh`, this section in one call,
and on 1 or 2 its last line names where it stopped.

A go-red guard step names its probe as ``probe `<file>` `<old>` → `<new>` on `<case>` ``: the
guard broken on purpose (`<old>` replaced by `<new>` in `<file>`) and the existing case that must
go red under it. It runs no Red leaf, no Green and no Refactor, and adds no test: the case is
already pinned, and what the step owes is the evidence that it guards. `go-red-step.sh` runs
`mutation-probe.sh` on that case with the `veri: one test file:` command, which breaks the file,
watches the case go red, restores the file and appends the probe to
`.tdd/issue-<n>-mutations.md`; then `step-tick.sh <n>` ticks the step against that record and
commits it under `test: go-red — <STEP summary> (#<n>)`. `tick-ledger.sh` exits 2 on a
`⟦go-red⟧` step whose file has no record there, so no go-red step is ticked without its probe.

- **Exit 1** — `stopped at probe <case> stayed green …`: the case does not catch the break, so
  the guard is not guarded; nothing is ticked. Bail with `cause=needs-user`
  (`<base directory>/BAIL.md`): the plan named a break its case cannot see, and only the human
  can say whether the case or the break is wrong.
- **Exit 2** — no open `⟦go-red⟧` step, a step naming no probe, the case already red on the
  unmutated file, a probe or `detect-test-command.sh` exit 2, or the file not restored: nothing
  is ticked. Bail as a system failure.
