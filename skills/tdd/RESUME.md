## Resume

The committed ledger makes a run **resumable**: re-running `/tdd <n>` picks up
where a previous run stopped (a bail, an interruption, or a human pause), without redoing
finished steps.

On a resume the issue's missing opt-in label is expected, since the claim removed it at the
first launch; never stop or ask about it.

On re-run, preflight step 3 calls `issue-worktree.sh` again; because it is **idempotent** it
prints the same `.tdd/wt/<n>` path and creates nothing, so the `cd` puts you back in the very
worktree the previous run committed in — the branch is already checked out there, nothing is
re-created or switched, and a resumed run's baseline runs on the branch head there, before
any cycle of the resumed run starts. When that baseline is red, preflight step 3 runs the red suites on
`origin/<default>`: in a throwaway checkout made with `git worktree add --detach <scratch> origin/<default>` (removed afterwards),
it runs the test command restricted to the branch-red suites — `make test TESTS="<those suite paths>"` here — in the foreground,
and writes `<default-red-file>`, one suite still red there per line, optionally followed by ` — ` and its first FAIL line, or the
single line `none` when no suite is red there. It then asks `$S/suite-red-resume.sh check .tdd/issue-<n>.md <branch-red-file> <default-red-file>`:
exit 1 refuses as it always has, and exit 0 — the last bail was `suite-red` and every branch-red suite is green on the
default branch — saves the branch-red list to `.tdd/resume-suite-red` and goes on. The **resume check** then finds an existing
`.tdd/issue-<n>.md`. When it does:

1. Do **not** re-plan — the ledger is the source of truth — except that the amended
   criteria are planned with `--planned` in sub-step 3. Re-write only the blind spec
   file (`.tdd/issue-<n>-spec.md`) since it is run scratch, not committed.
   Here, ahead of sub-step 2's refactor clear and every later ledger commit: when the
   committed ledger holds step lines beyond its plan commit and there is no
   `.tdd/issue-<n>-added.md`, run `$S/ledger-growth.sh record-existing .tdd/issue-<n>.md` once, before
   the resume's first ledger commit, and stage `.tdd/issue-<n>-added.md` in that same commit with the ledger.
2. **Use the reset preflight already made, then ask for a pending refactor.** Whatever killed
   the previous run killed its leaf too, at whatever point the run had reached — a usage
   limit takes the conductor and every leaf together — so a resumed worktree may carry
   uncommitted work from a killed **Red** or **Green** leaf just as readily as from a killed
   refactor one. No verifier has seen any of it and none of it may reach the PR, so it is
   thrown away **before** the ask, not under one of its answers: preflight step 3's
   `resume-clean.sh` already captured `git status --porcelain` and ran `git reset --hard HEAD`,
   ahead of the resume rebase; its stdout is `$stray`. Do not capture again here — the tree is clean, so a second capture
   would empty `$stray`.
   `$stray`, that script's stdout, holds the paths that reset discarded, and sub-step 4 is what does the naming:
   a killed leaf's stray work is real work — the run that prompted this left a 235-line
   untracked test file behind — and it has to go loudly, not in silence.
   Then `$S/next-pending-refactor.sh < .tdd/issue-<n>.md` prints the first checked step whose
   refactor-pending mark is still there — a step the previous run left **green but not
   tidied**, because it was killed between that step's green commit and its
   verify-refactor. **Exit 3** means no step carries the mark: go to sub-step 3. Otherwise
   **STEP** is that description, and this step's refactor loop is re-entered where it
   stopped:
   ```
   green="$(git log -1 --format=%H -- .tdd/issue-<n>.md)"
   touched="$($S/refactor-touched.sh "$green")"
   count="$(git log --format=%s "$green"..HEAD | grep -c '^refactor:')"
   left=$(( ${VERI_REFACTOR_BUDGET:-5} - count )); (( left < 0 )) && left=0
   ```
   `$green` is the step's **green commit** — the last commit that changed the ledger, since
   the tick is atomic with it and the clear that would follow never happened. So `$touched`
   — that commit's `git diff --name-only`, through the same script the cycle loop calls —
   is the same bounds the interrupted loop had, and `$count` the transforms it already
   committed. Run the **Refactor loop** (the cycle loop's sub-section) with `$touched` as
   its bounds and **`VERI_REFACTOR_BUDGET=$left`** in the environment of every call that
   reads it — `refactor-budget.sh`, `build-develop-prompt.sh refactor` and
   `leaf-timeout.sh`. One leaf is handed the budget as a number and spends it, so the
   relaunched leaf gets the run's budget **reduced** by `$count`, never the ambient one:
   on the ambient number the interrupted step pays for its tidying twice over, which is the
   cost the budget exists to bound. A `$left` of 0 is a budget already spent, and
   `refactor-budget.sh 0` then skips the leaf — the step is tidied as far as it was funded
   to be. Run its **verify-refactor** after it — the check the interruption skipped — with
   `$green` as the cycle loop's `<green-sha>`:
   `verify.sh --step "<STEP>" --fast-cmd '<fast-cmd>' refactor <spec-file> <test-path> "$green"`, launched as there. Its
   PASS clears the mark and commits the cleared ledger exactly as in the cycle loop; then
   come back here and ask sub-step 2 again.
3. `next-unchecked.sh < .tdd/issue-<n>.md` gives the **first unchecked step** — the cycle
   loop continues from exactly there, so **STEP** is that step's description, bound here
   instead of at the top of the cycle loop. Already-checked steps (and their commits) are
   kept. Before that pick, plan each criterion that is unticked in the issue body when the
   resume starts and that no ledger step's `⟦criterion k⟧` serves — scope a human amended in —
   with `add-ledger-step.sh --planned --criterion k`, one call per criterion, committed as a
   `plan:` commit before the cycle loop with `git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md`,
   so the insertion records travel with the ledger. Those steps are planned steps, not `⟦added⟧` growth,
   and do not count against `VERI_STEP_GROWTH`. Every other insertion during the resume omits
   --planned, stays `⟦added⟧` and counts. A conductor never sets or raises `VERI_STEP_GROWTH`,
   `REVISE_BUDGET`, `VERI_REFACTOR_BUDGET`, `VERI_STUCK_RETRIES` or `VERI_NO_VERDICT_RETRIES`
   mid-run, in its environment or in a scratch helper, and a budget it cannot fit inside is a bail.
4. Post a `### ▶️ Resuming` comment naming that step and, when `$stray` is non-empty, the
   paths it lists, said as what they are: the stray work sub-step 2's reset discarded, seen
   by no verifier and now gone. Mark the pick-up in the log —
   `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/event.sh resume` — then, when
   `.tdd/resume-suite-red` exists, run `$S/suite-red-resume.sh insert .tdd/issue-<n>.md .tdd/resume-suite-red`, commit the
   ledger with `.tdd/issue-<n>-added.md`, and hand the inserted `⟦suite-repair⟧` step to the cycle loop first. When `insert` exits 1 — the growth cap filed the step as
   owed — bail with cause `suite-red`, naming the branch-red suites; when it exits 2 — no answer — bail with cause `no-verdict`;
   then **reuse the claim the previous run left on the branch**, which every tick of the cycle
   loop edits and step 4 rewrites:
   ```
   gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'   # → <pr-url>, the PR step 2.3 opened; <pr-number> is its last path segment
   ```
   A resumed run skips step 2 outright, so this is where the url comes from: it is read off
   the branch, never remembered. It edits that PR and opens **no second one** — a second
   PR-creating `gh api` call against a branch that already has an open PR is either a refusal that ends
   the resume where it started, or two pages claiming one issue, which is the failure #195
   exists to prevent. Only when this prints nothing is there **no open PR** to reuse: the
   previous run was killed inside step 2.3's own window, between the plan commit and the
   PR-creating `gh api` call that follows it. Then, and only then, run that sub-step's push and
   PR-creating `gh api` call here — opening the first PR a branch has ever had is not opening a second.
   Then run the cycle loop as normal. Go to the **draft PR** only when
   `next-pending-refactor.sh` and `next-unchecked.sh` have **both** exited 3: every step is
   checked, and every checked step's refactor is verified. An unchecked `⟦full-suite⟧` or
   `⟦human-owed⟧` line does not hold the run back from its draft PR — no cycle ticks either,
   and `next-unchecked.sh` skips both.

Because each step was checked off **atomically with its green commit**, the ledger and the
git history agree on exactly what is done — so resume never repeats or skips a step.
