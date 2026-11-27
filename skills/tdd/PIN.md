## Already satisfied — the pin

A step whose criterion **earlier work already satisfies** has no failing test to write: the
behaviour exists, and the step is an **outcome**, not a failure. Such an already-holding step
takes one of two forms. Either the Red leaf names the existing tests that cover the criterion
(`AGAINST_UNMODIFIED: HOLDS`, with `COVERING_TESTS: <id>…`) and writes nothing, or no existing
test covers it and the leaf adds one test that passes against the unmodified code
(`AGAINST_UNMODIFIED: PASSES`). Neither owes a fail-at-base or a mutation: the test is never
shown to fail on any earlier commit, and no production code is broken to watch it go red. You reach this section from
Red, which ran `$S/holds-step.sh` on `HOLDS` and then `$S/verify.sh pin …` in place of verify-red, with the
`COVERING_TESTS:` ids on `HOLDS` and the step's `TARGET_TEST` on `PASSES`. The verify-pin verdict replaces the
`### 🔴 Red` / `### 🔎 verify-red` comment pair, the comments `$S/comment.sh <n> red` and
`$S/comment.sh <n> verify-red` would otherwise post.

verify-pin judges only that the named tests pass now and cover the criterion, and their quality: it runs
no probe and applies no mutation, so no file but the test is committed with a `PASSES` pin's tick.

**Switched off:** with `pin` listed in `.tdd/issue-<n>-skip-verify`, no verify-pin launches on any
step — not on Red's `PASSES` or `HOLDS`, not on a `red-missing` added case that passes, not as a
revised red's re-verify. Record `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh verify-pin-skipped reason=switched-off`,
write `skipped` to `.tdd/verdict-pin.exit`, and take the PASS branch below as on exit 0: on `PASSES`
with `pin-fast-tier.sh` (and `rerun-alone.sh` on its exit 1), on `HOLDS` with the tick resting on
`holds-step.sh` exit 0 alone, or the `⟦replaces-case⟧` deletion path. The
`### 📌 Already satisfied — <STEP>` mirror comment carries `verify-pin — SKIPPED (switched off)` where it would
carry the verifier's reason.

A `⟦replaces-case⟧` step whose Red reports `AGAINST_UNMODIFIED: PASSES` is verified by the
reduced verify-pin like any other `PASSES` step, then takes a different path after it,
because deleting the named bash cases is still owed.
A `⟦replaces-case⟧` step skips verify-red, so on that verify-pin PASS first run
`$S/tests-frozen.sh record --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" <test-path>` to record its replacement
cases before the deletion green checks them; tests-frozen exit 2 is a bail. Then commit nothing yet,
and launch a green leaf exactly as *Green* does, whose only change
is deleting exactly the named cases. By now the unreplaced-cases check from *Red* has
bailed with cause=unreplaced-cases only on a second exit 1 after its one correction leaf, or on exit 2. After the
deletion green, run `$S/replaces-case-survivors.sh "<step text>"` before that verify-green launches;
on exit 1 relaunch the green leaf naming the survivors, as *Green* does, record the relaunch as an
event (`$S/event.sh`), and launch no verifier on that green. Each relaunch spends one `REVISE_BUDGET`
attempt, and when it is spent the run bails with `cause=revise-exhausted`. Judge it by the replaces-case verify-green, whose PASS
is accepted only once `$S/mutation-parity.sh <pairs-table>` on that step's pairs table
exits **0**, as on *Green*'s verify, then commit the pytest cases, the deletion
and the ticked ledger in one tick-and-commit, as *Green*'s PASS does.
That tick carries `--refactor-pending`, so the ` ⟂ refactor pending` mark follows the
deletion green and the Refactor phase runs on the step as after any Green.
Every other step takes the verdict as follows:

- **PASS (exit 0) — on a `⟦replaces-case⟧` step, take the deletion path above instead.**
  **On `HOLDS`** retire the step, with no commit of a test: tick it with
  `$S/tick-ledger.sh --already-holds .tdd/verify-pin.reason --case <id> .tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"`,
  one `--case` per `COVERING_TESTS:` id, which marks it ` ⟂ retired already holds`; commit that
  ticked ledger alone, post `$S/comment.sh <n> retire`, run no Green and no Refactor, and loop back
  to the top of **step 3** for the next unchecked ledger step.
  **On `PASSES`** commit the test as the pin, ticking the ledger atomically. Same
  tick-and-commit shape as Green, but the commit carries the **test alone** and the `test:`
  type, because no production code was written, so the tree holds only the new test and the
  ticked ledger:
  Before it, run `$S/pin-fast-tier.sh '<fast-cmd>'`: on exit 1 first run
  `$S/rerun-alone.sh '<alone-cmd>' .tdd/verify-pin.reason`, where `<alone-cmd>` is the value of
  the repo CLAUDE.md's `veri: one test file:` line (the repo's own runner for one test target,
  a test file or a pytest node id, taking the target as `$1`: `make test TESTS="$1"` on veri), read with
  `$S/detect-test-command.sh --tier "one test file"`. When the repo declares no such line
  (that call exits 3), skip `rerun-alone.sh` and, on `pin-fast-tier.sh` exit 1, enter the
  revise loop for red exactly as on a `rerun-alone.sh` exit 1 below, never guessing a runner. On
  its exit 0 every target the red output names (a failing pytest node id, else a file) passed alone, and the script itself has written
  the one `suite-flake` event naming those targets: tick and commit
  `test: pin` as below. On its exit 1 (a target stays red, or the output names none) the pin
  tripped a fast-tier guard, so commit nothing and enter the revise loop for red with
  `.tdd/verify-pin.reason` (the fast tier's output) as the reason, spending a `REVISE_BUDGET`
  attempt as a verify-pin REJECT does (when a verifier answers `REJECT`, `Read`
  `<base directory>/REVISE.md`). On `pin-fast-tier.sh` exit 0
  tick and commit `test: pin` as below; on exit 2 from either script bail as a system failure.
  ```
  $S/tick-ledger.sh .tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"
  git add -A && git commit -m "test: pin <STEP summary> (#<n>)"
  ```
  **Then run `$S/stop-requested.sh`**, immediately after that commit: it is a ledger commit
  like Green's, so handle its exit 0, exit 2 and exit 3 as the stop check in `SKILL.md`'s
  *Green* does after its push (on a stop, `Read` `<base directory>/STOPPING.md`); where
  Green continues to the Refactor loop, a pin carries on to the mirror below.
  Then **mirror**: post a `### 📌 Already satisfied — <STEP>` comment carrying the
  verifier's reason with `$S/comment.sh <n> pin`, ask whether the step's criterion is finished
  (`$S/criterion-finished.sh <k> < .tdd/issue-<n>.md`) and on exit **0** tick it in the
  **issue body** (`$S/tick-issue-criterion.sh <n> "$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`) — on exit **3** tick
  nothing — and mark it in the log —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" VERI_PHASE=pin $S/event.sh pin`.
  The step is **done** — **no Green and no Refactor**, since there is no new production
  code to write or to tidy. Loop back to the top of **step 3** for the next unchecked
  ledger step.
- **REJECT (exit 1):** enter the revise loop for the **red** phase on `REVISE_BUDGET`
  (`Read` `<base directory>/REVISE.md`), straight from the verdict, building the prompt as
  `revise red … .tdd/verify-pin.reason`; no script routes the REJECT and no step is retired on it. The phase argument
  is the *developer* phase being redone, while the reason file is named for the *verifier*
  that rejected, here `pin`. The rejection reason is the carry-forward signal that tells the
  fresh leaf which way to go: the tests do not cover the criterion, the added test is weak
  (trivial or over-coupled), or a genuinely failing test exists after all. Re-verify with the phase the
  revise leaf's own `AGAINST_UNMODIFIED` line selects — `pin` on `PASSES` or `HOLDS`, `red` on `FAILS`;
  on `HOLDS` only after `$S/holds-step.sh` over the `HEAD` the revise leaf launched on passes, the first-try gate.
  On a recovered `PASS` from `pin`, do the PASS bullet's tick above, or the deletion path
  on a `⟦replaces-case⟧` step; from `red`,
  continue to Green. On budget-exhausted, **bail** as a **process** failure.
- **Malformed / killed-stuck (exit 2):** **bail** as a **system** failure (`no-verdict`) —
  see `<base directory>/BAIL.md`.
