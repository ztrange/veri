## Adjudicating an exit 2

An exit 2 means no answer could be obtained. Before some of them bail, one fresh leaf, the
**adjudicator**, judges it once (ADR-0035). It decides; it never acts. `$S` is the scripts
directory, as everywhere else.

### Eligible causes

Only the causes listed here are adjudicated, each with the route tokens it allows. This list
is read by a script: one bullet per cause, `` - `<cause>`: `` then its route tokens,
backticked and comma-separated, or `none`.

- `ci-timeout`: none

`killed-stuck`, `no-verdict`, `killed-external` and preflight refusals are never adjudicated:
the first three already have a budget of their own (`VERI_STUCK_RETRIES`,
`VERI_NO_VERDICT_RETRIES`), a kill from outside is the operator's word, and a refused
preflight has spent nothing to judge. Any other exit 2 bails as before.

### Procedure

Run it in order, at the site where the eligible exit 2 came back.

1. **Check the budget.** `$S/adjudicate.sh left <n>` reads `VERI_ADJUDICATE_BUDGET`. Exit 0:
   budget is left, go on. Exit 3: it is spent, so bail with the original cause and class.
2. **Build the prompt.** `$S/build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>
   > .tdd/adjudicate-<cause>.prompt`.
3. **Launch the leaf** `adjudicate-<cause>` through `supervise.sh`, detached, then wait in the
   foreground (on an exit 3 call the wait again):

   ```
   VERI_ISSUE=<n> $S/detach-leaf.sh $S/supervise.sh adjudicate-<cause> $S/run-leaf.sh .tdd/adjudicate-<cause>.prompt --permission-mode bypassPermissions > .tdd/adjudicate-<cause>.out 2> .tdd/adjudicate-<cause>.err
   $S/wait-leaf.sh adjudicate-<cause>   # foreground; on exit 3 call it again
   ```
4. **Parse and record.** `$S/adjudicate.sh record <n> <cause> .tdd/adjudicate-<cause>.out`
   reads the answer with `parse-adjudication.sh` and records the `adjudicated` event. Act on
   its exit:
   - `0` — `retry`: run the step that returned 2 once more.
   - `1` — `bail` or `route`: bail, or take the route token the cause allows (`ci-timeout`
     allows none, so it bails).
   - `2` — unparsed: a bail with the original cause and class.

### Guards

- The adjudicator writes no file and no ledger line; the conductor records the event.
- It never relabels the 2 as a 1: a timeout stays a system failure, not a clean negative.
- A bail after adjudication keeps its original classification (`classify-bail.sh` sees the
  original cause), and a route token outside the cause's list above is read as a bail.
- ADR-0035 (`docs/adr/0035-an-exit-2-is-judged-once-before-it-bails.md`) holds the reasoning.
