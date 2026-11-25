## Adjudicating an exit 2

An exit 2 means no answer could be obtained. Before some of them bail, one fresh leaf, the
**adjudicator**, judges it once (ADR-0035). It decides; it never acts. `$S` is the scripts
directory, as everywhere else.

### Eligible causes

Only the causes listed here are adjudicated, each with the route tokens it allows. This list
is read by a script: one bullet per cause, `` - `<cause>`: `` then its route tokens,
backticked and comma-separated, or `none`.

- `ci-timeout`: none
- `ci-conflict`: `rebase`
- `pr-ready-failed`: none
- `report-missing`: none
- `step-add-refused`: none
- `replaces-report-failed`: none
- `unreplaced-cases`: `replaces-report`
- `reconcile-failed`: none
- `criterion-unreadable`: none

`killed-stuck`, `no-verdict`, `killed-external` and preflight refusals are never adjudicated:
the first three already have a budget of their own (`VERI_STUCK_RETRIES`,
`VERI_NO_VERDICT_RETRIES`), a kill from outside is the operator's word, and a refused
preflight has spent nothing to judge. Any other exit 2 bails as before.

### Waivable rules

A few rules may be waived once per run, for one step, when the adjudicator answers `deviate`
(ADR-0037). A waivable cause is a bail, not an exit 2. `graded-edit-outside-skill-edit` is
judged at the bail: `BAIL.md`'s first sub-step sends it through the *Procedure* below.
`tests-frozen-refused` is judged at the step's first freeze refusal in the green phase, before
any `REVISE_BUDGET` is spent. The adjudicator judges whether the refused change is needed
for the criterion and whether the rule's resume action keeps the rule's purpose. This list is read by a script: one bullet per rule, `` - `<rule-id>`: `` then the
bail cause that names it, backticked, then its purpose and its resume action.

- `graded-edit`: `graded-edit-outside-skill-edit` — Purpose: only a `⟦skill-edit⟧` step signs a
  graded unit, so no graded prose lands without a grade. Resume action: keep the step's commit
  and append, through `add-ledger-step.sh`, one `⟦added⟧` `⟦skill-edit⟧` step naming each unit
  `graded-changed.sh` printed (it counts against `VERI_STEP_GROWTH_PERCENT`), then go on from
  the refusing step's next sub-step. An `add-ledger-step.sh` refusal bails with the original
  cause.
- `tests-frozen`: `tests-frozen-refused` — Purpose: green cannot pass by editing the test
  verify-red judged. Resume action: send the test-only edit to the blind `diff` verifier and,
  on its PASS, re-record the step's frozen tests and launch verify-green.

A rule absent from this list is never waived, whatever the adjudicator answers. These are never
waivable: the blind verifier's inputs, a verify-green or verify-refactor REJECT of production
code, exit-code semantics, `supervise.sh`, the committed ledger, the skill snapshot pin, a
missing or obsolete target, and a real spec gap.

### Procedure

Run it in order, at the site where the eligible exit 2 came back.

1. **Check the budget.** `$S/adjudicate.sh left <n>` reads `VERI_ADJUDICATE_BUDGET`. Exit 0:
   budget is left, go on. Exit 3: it is spent, so bail with the original cause and class.
   Exit 2: the event log could not be read, so bail with the original cause and class, with no
   adjudication.
   Every bail that follows a launched adjudicator (any answer, or its own no-answer) is written
   by a bare command in a Bash call of its own, never by a line guarded by a shell variable set
   in an earlier call: the conductor's Bash calls share no variables, and the leaf's launch and
   wait take calls of their own.
2. **Build the prompt.** `$S/build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>
   > .tdd/adjudicate-<cause>.prompt`. Each site names its `<stderr-file>` and `<command…>`; at every
   `report-missing` site they are `.tdd/suite-reported.err` and `suite-reported.sh <leaf>`, `<leaf>`
   the leaf whose report was checked (`develop-green` in `SKILL.md`).
   At every `step-add-refused` site they are `.tdd/add-ledger-step.err` and the `add-ledger-step.sh`
   call that exited 2.
   At the `replaces-report-failed` site they are `.tdd/develop-replaces-report.err` and
   `wait-leaf.sh develop-replaces-report`.
   At the `unreplaced-cases` site (its first check only) they are `.tdd/unreplaced-cases.err` and
   `unreplaced-cases.sh <step line> <report>`.
   At the `reconcile-failed` site (`RECONCILE.md`) they are `.tdd/develop-reconcile.err` and
   `wait-leaf.sh develop-reconcile` for the leaf's exit 2, and `.tdd/push-branch.err` and
   `push-branch.sh` for the second push's exit 2.
   At the `criterion-unreadable` site (`SKILL.md`, a step's mirror to the issue) they are
   `.tdd/criterion-finished.err` and `criterion-finished.sh <k>`.
   For `graded-edit-outside-skill-edit` (`BAIL.md`'s first sub-step) they are
   `.tdd/graded-changed.out`, the units `graded-changed.sh` printed, and that
   `graded-changed.sh <sha>` call.
3. **Launch the leaf** `adjudicate-<cause>` through `supervise.sh`, detached, then wait in the
   foreground (on an exit 3 call the wait again). Remove the cause's completion and pid files
   first, as *Launching a leaf* in `SKILL.md` does, so a second adjudication of one cause never
   ends its wait on the first one's:

   ```
   rm -f .tdd/adjudicate-<cause>.exit .tdd/adjudicate-<cause>.pid
   VERI_ISSUE=<n> $S/detach-leaf.sh $S/supervise.sh adjudicate-<cause> $S/run-leaf.sh .tdd/adjudicate-<cause>.prompt --permission-mode bypassPermissions > .tdd/adjudicate-<cause>.out 2> .tdd/adjudicate-<cause>.err
   $S/wait-leaf.sh adjudicate-<cause>   # foreground; on exit 3 call it again
   ```
   Any other exit of the wait goes on to step 4: a leaf that left no answer records `unparsed`.
4. **Parse and record.** `$S/adjudicate.sh record <n> <cause> .tdd/adjudicate-<cause>.out`
   reads the answer with `parse-adjudication.sh` and records the `adjudicated` event. Act on
   its exit:
   - `0` — `retry`: run the step that returned 2 once more, but only where the cause's own site
     states a retry (`ci-timeout`, `ci-conflict`, `pr-ready-failed`). For any other cause, a
     waivable one included, exit `0` is a bail with the original cause and class, the
     `adjudicated` event still saying `outcome=retry`.
   - `1` — `bail` or `route`: bail, or take the route token the cause allows (`ci-timeout`
     allows none, so it bails; `ci-conflict`'s `rebase` is the path its site in `DRAFT-PR.md`
     states, and `unreplaced-cases`'s `replaces-report` the correction leaf its site in `SKILL.md`
     states).
   - `2` — unparsed: a bail with the original cause and class.
   - `4` — `deviate`, read only for a cause *Waivable rules* names (for any other cause the
     answer is unparsed, exit 2). Run `$S/adjudicate.sh deviation-left <n>`, which reads
     `VERI_DEVIATION_BUDGET` (default 1); its exit 3 (spent) or 2 (unreadable log, bad knob) bails
     with the original cause and class. On exit 0 take the rule's resume action first (for
     `graded-edit`, the `add-ledger-step.sh` call); a refused resume action bails with the
     original cause and class, and since nothing was recorded it spends no deviation budget.
     Only once the resume action succeeded record the deviation, in this order, `<id>` the rule,
     `<k>` the step and `<reason>` the answer's one line of reason:
     ```
     VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh deviated rule=<id> step=<k> reason="<reason>"
     ```
     then append to the committed ledger, and commit it, the line
     `- [ ] deviated from <id> at step <k>: <action> — <reason> ⟦human-owed⟧ ⟦deviation <id>⟧ ⟦criterion k⟧`,
     `<action>` the resume action in a few words (`added a ⟦skill-edit⟧ step` for
     `graded-edit`). `/vmerge` reviews that line before the merge.

### Guards

- The adjudicator writes no file and no ledger line; the conductor records the event.
- It never relabels the 2 as a 1: a timeout stays a system failure, not a clean negative.
- A bail after adjudication keeps its original classification (`classify-bail.sh` sees the
  original cause), and a route token outside the cause's list above is read as a bail.
- ADR-0035 (`docs/adr/0035-an-exit-2-is-judged-once-before-it-bails.md`) holds the reasoning.
