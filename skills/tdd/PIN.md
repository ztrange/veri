## Already satisfied — the pin

A step whose criterion **earlier work already satisfies** has no failing test to write: the
honest test passes against the unmodified code. That is an **outcome** of the step, not a
failure of it — the behaviour exists and what it wants is a **regression pin**. You reach
this section from Red when the developer leaf reported `AGAINST_UNMODIFIED: PASSES` and you
ran `$S/verify.sh pin …` in place of verify-red. Its verdict replaces the
`### 🔴 Red` / `### 🔎 verify-red` pair.

`verify-pin`'s probe is recorded in `.tdd/issue-<n>-mutations.md` by the probe itself, and
that file is committed with the pin's tick (the `git add -A` below takes it).

A `⟦replaces-case⟧` step whose Red reports `AGAINST_UNMODIFIED: PASSES` takes a different
path after verify-pin, because deleting the named bash cases is still owed.
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

- **PASS (exit 0) — on a `⟦replaces-case⟧` step, take the deletion path above instead;
  on any other step, commit the test as the pin, ticking the ledger atomically.** Same
  tick-and-commit shape as Green, but the commit carries the **test alone** and the `test:`
  type, because no production code was written (the verifier reverted its own mutation, so
  the tree holds only the new test and the ticked ledger):
  Before it, run `$S/pin-fast-tier.sh '<fast-cmd>'`: on exit 1 the pin tripped a fast-tier
  guard, so commit nothing and enter the revise loop for red with `.tdd/verify-pin.reason`
  (the fast tier's output) as the reason, spending a `REVISE_BUDGET` attempt as a verify-pin
  REJECT does (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`). On exit 0
  tick and commit `test: pin` as below; on exit 2 bail as a system failure.
  ```
  $S/tick-ledger.sh .tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"
  git add -A && git commit -m "test: pin <STEP summary> (#<n>)"
  ```
  **Then run `$S/stop-requested.sh`**, immediately after that commit: it is a ledger commit
  like Green's, so handle its exit 0, exit 2 and exit 3 as the stop check in `SKILL.md`'s
  *Green* does after its push (on a stop, `Read` `<base directory>/STOPPING.md`); where
  Green continues to the Refactor loop, a pin carries on to the mirror below.
  Then **mirror**: post a `### 📌 Already satisfied — <STEP>` comment carrying the
  verifier's reason, ask whether the step's criterion is finished
  (`$S/criterion-finished.sh <k> < .tdd/issue-<n>.md`) and on exit **0** tick it in the
  **issue body** (`$S/tick-issue-criterion.sh <n> "$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`) — on exit **3** tick
  nothing — and mark it in the log —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" VERI_PHASE=pin $S/event.sh pin`.
  The step is **done** — **no Green and no Refactor**, since there is no new production
  code to write or to tidy. Loop back to the top of **step 3** for the next unchecked
  ledger step.
- **REJECT (exit 1):** enter the **revise loop** for the **red** phase, building the prompt as
  `revise red … .tdd/verify-pin.reason` (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`). The phase argument
  is the *developer* phase being redone, while the reason file is named for the *verifier*
  that rejected, here `pin`. The rejection reason is the carry-forward signal that tells the
  fresh leaf which way to go: either the pin is weak (trivial, over-coupled, or it survives
  the mutation) or a genuinely failing test exists after all. Re-verify with the phase the
  revise leaf's own `AGAINST_UNMODIFIED` line selects — `pin` on `PASSES`, `red` on `FAILS`.
  (That line's third value, `N/A`, cannot arise here: a revise of red always touches a
  test.) On a recovered `PASS` from `pin`, do the tick-and-commit above, or the deletion path
  on a `⟦replaces-case⟧` step; from `red`,
  continue to Green. On budget-exhausted, **bail** as a **process** failure.
- **Malformed / killed-stuck (exit 2):** **bail** as a **system** failure (`no-verdict`) —
  see `<base directory>/BAIL.md`.
