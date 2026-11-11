## Already satisfied — the pin

A step whose criterion **earlier work already satisfies** has no failing test to write: the
honest test passes against the unmodified code. That is an **outcome** of the step, not a
failure of it — the behaviour exists and what it wants is a **regression pin**. You reach
this section from Red when the developer leaf reported `AGAINST_UNMODIFIED: PASSES` and you
ran `$S/verify.sh pin …` in place of verify-red. Its verdict replaces the
`### 🔴 Red` / `### 🔎 verify-red` pair, the comments `$S/comment.sh <n> red` and
`$S/comment.sh <n> verify-red` would otherwise post.

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
  verifier's reason, ask whether the step's criterion is finished
  (`$S/criterion-finished.sh <k> < .tdd/issue-<n>.md`) and on exit **0** tick it in the
  **issue body** (`$S/tick-issue-criterion.sh <n> "$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`) — on exit **3** tick
  nothing — and mark it in the log —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" VERI_PHASE=pin $S/event.sh pin`.
  The step is **done** — **no Green and no Refactor**, since there is no new production
  code to write or to tidy. Loop back to the top of **step 3** for the next unchecked
  ledger step.
- **REJECT (exit 1):** run
  `$S/pin-reject-route.sh [--missing-reroute] .tdd/verify-pin.reason .tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" <target-test>`,
  passing `--missing-reroute` on a step reached by a `missing` reroute, and `<target-test>`
  the step's `TARGET_TEST` from the red leaf's report. The script retires the step only when
  that case passes, and it runs the case to find out; a failing case makes it print `revise`
  and exit 1, leaving the line unticked and unmarked with no retirement event, so you enter
  the revise loop for red (or park the step when the revise budget is spent), never retiring
  it by hand. It prints `retired`
  or `revise`, except that under `--missing-reroute` a reason with a before-state-green clause
  (a clause naming the before-state and green or pass, with no fail, red, not, n't or after in it) prints `unpinnable-missing`, ticks nothing and exits 2: only the
  added missing case is unpinnable, not the step. A reason with no such clause and no `stays green` retires the step via `--already-holds`. A reason reporting a surviving mutant of the
  added case (`stays green`, the target red on the before-state) is not that: it is exit 1 and
  enters the revise loop for red. The routing is the script's decision, never your reading of the reason. On its
  exit **0** the step is retired: commit the retired ledger, write no `revise` mark, spend no
  `REVISE_BUDGET` attempt, post the step's retirement to the thread, and loop back to
  `next-unchecked.sh` for the next unchecked ledger step; this holds on a step reached by a
  `missing` reroute too, whose green is then not re-run. On its exit **1** enter the revise
  loop as follows (`build-develop-prompt.sh revise red` refuses, exit 2, only a `verify-pin.reason`
  with a before-state-green clause, not every `stays green` reason, so that reason never
  reaches it); on its exit **2** printing
  `unpinnable-missing` (only under `--missing-reroute`) **bail** with `cause=unpinnable-missing`
  as a **process** failure, and on any other (bare) exit **2** **bail** as a
  **system** failure. Exit 2 still means bad arguments (a missing `<target-test>` included) or
  no answer: read exit 1 as the methodology speaking and exit 2 as the plumbing breaking, except
  when it prints `unpinnable-missing`, which is the methodology speaking (a process failure).
  The revise loop: enter it for the **red** phase, building the prompt as
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
