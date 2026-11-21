## Resume

The committed ledger makes a run **resumable**: re-running `/tdd <n>` picks up
where a previous run stopped (a bail, an interruption, or a human pause), without redoing
finished steps.

On a resume the issue's missing opt-in label is expected, since the claim removed it at the
first launch; never stop or ask about it.

On re-run, preflight step 3 calls `issue-worktree.sh` again; because it is **idempotent** it
prints the same `.tdd/wt/<n>` path and creates nothing, so the `cd` puts you back in the very
worktree the previous run committed in — the branch is already checked out there, nothing is
re-created or switched (a branch only origin holds, whose issue carries this lane's `taken:<lane>` label,
is resumed by recreating the worktree from origin's branch tip; another lane's claim is refused, exit 2; with no exact branch the issue's one `tdd/<n>-*` branch is reused whatever slug is passed, and two or more such branches exit 2 naming each and the requested branch), and a resumed run's baseline runs on the branch head there, before
any cycle of the resumed run starts, unless preflight step 3 skips it as already proven green: a green baseline this
machine recorded for the branch head's tree under the same key, or a CI `push` run concluded `success` on exactly that sha. When that baseline is red, preflight step 3 first runs each test file the red baseline
names alone, once, with the repo's own runner (`make test TESTS="<file>"` here), and asks
`$S/suite-red-resume.sh flake resume <red-file> <alone-red-file>`: on exit 0 — every file passed alone — the `suite-flake` event names
the files, no `.tdd/resume-suite-red` is written, and the resume goes on as on a green baseline; on exit 1 — any file still red alone,
or the output names no file — the baseline takes the path below. Otherwise preflight step 3 runs the red suites on
`origin/<default>`: in a throwaway checkout made with `git worktree add --detach <scratch> origin/<default>` (removed afterwards),
it runs the test command restricted to the branch-red suites — `make test TESTS="<those suite paths>"` here — in the foreground,
and writes `<default-red-file>`, one suite still red there per line, optionally followed by ` — ` and its first FAIL line, or the
single line `none` when no suite is red there. It then asks `$S/suite-red-resume.sh check .tdd/issue-<n>.md <branch-red-file> <default-red-file>`:
exit 1 refuses as it always has, and exit 0 — every branch-red suite is green on the
default branch, whatever the previous bail's cause — saves the branch-red list to `.tdd/resume-suite-red` and goes on. The **resume check** then finds an existing
`.tdd/issue-<n>.md`. When it does:

Run `$S/resume-start.sh <n>` first, again on exit 3. On exit 0 it made sub-steps 1–4's fixed calls and the owed
verify-plan: take **STEP**, `<pr-url>` and the verdict from its last lines `step=`, `pr_url=` and `verify_plan=`
(`PASS` or `skip`), commit an `insert`'s ledger as sub-step 4 says, and run the cycle loop. On exit 1 or 2 go on by
the sub-step its `stopped at` line names. It asks sub-step 2's pending refactor before sub-step 1's record: only when
`next-pending-refactor.sh` exits 3 does it make that record, committed alone as
`chore: record the steps the ledger grew before its record (#<n>)`; a pending refactor stops it at 2 with no record
made, so no commit lands between that step's green commit and its refactor. A stop at 4 after its
`comment.sh <n> resuming` line exited 0 has already marked the resume and posted the Resuming comment: do not repeat
them.

1. Do **not** re-plan — the ledger is the source of truth — except that the amended
   criteria are planned with `--planned` in sub-step 3. Re-write only the blind spec
   file (`.tdd/issue-<n>-spec.md`) since it is run scratch, not committed.
   Here, ahead of sub-step 2's refactor clear and every later ledger commit: when the
   committed ledger holds step lines beyond its plan commit and there is no
   `.tdd/issue-<n>-added.md`, run `$S/ledger-growth.sh record-existing .tdd/issue-<n>.md` once, before
   the resume's first ledger commit, and stage `.tdd/issue-<n>-added.md` in that same commit with the ledger.
   `resume-start.sh` makes this record only when no refactor is pending, as its own commit; after its stop at 2
   with a refactor pending the record is still owed here, and the conductor runs `record-existing` after
   verify-refactor's PASS, immediately before sub-step 2's cleared-ledger commit, and stages it in that commit
   (made earlier, the untracked file would make the Refactor loop's step-2 `git status --porcelain` check refuse the dirty tree).
   A passed `⟦skill-edit⟧` step that a post-review change must redo is reopened with
   `$S/ledger-growth.sh reopen .tdd/issue-<n>.md <needle> <change>`, which records the step itself (exit 3: no ticked step matches; exit 2: ambiguous needle or not a `⟦skill-edit⟧` step).
2. **Use the reset preflight already made, then ask for a pending refactor.** Whatever killed
   the previous run killed its leaf too, at whatever point the run had reached — a usage
   limit takes the conductor and every leaf together — so a resumed worktree may carry
   uncommitted work from a killed **Red** or **Green** leaf just as readily as from a killed
   refactor one. No verifier has seen any of it and none of it may reach the PR, so it is
   thrown away **before** the ask, not under one of its answers: preflight step 3's
   `resume-clean.sh` already captured `git status --porcelain` and ran `git reset --hard HEAD`,
   ahead of the resume rebase; its stdout is `$stray`: the paths on the `stray=` lines of `$S/preflight.sh`'s
   output (its last lines on exit 0, the lines before its `stopped at` line on a stop), not a capture
   you make or hold. Do not capture again here — the tree is clean, so a second capture
   would empty `$stray`.
   `$stray` holds the paths that reset discarded, and sub-step 4 is what does the naming:
   a killed leaf's stray work is real work — the run that prompted this left a 235-line
   untracked test file behind — and it has to go loudly, not in silence.
   Then `$S/next-pending-refactor.sh < .tdd/issue-<n>.md` prints the first checked step whose
   refactor-pending mark is still there — a step the previous run left **green but not
   tidied**, because it was killed between that step's green commit and its
   verify-refactor. **Exit 3** means no step carries the mark: go to sub-step 3. Otherwise
   **STEP** is that description, and this step's refactor loop is re-entered where it
   stopped:
   ```
   green=<green-sha>
   touched="$($S/refactor-touched.sh "$green")"
   count="$(git log --format=%s "$green"..HEAD | grep -c '^refactor:')"
   left=$(( ${VERI_REFACTOR_BUDGET:-5} - count )); (( left < 0 )) && left=0
   ```
   `<green-sha>` is the step's own **green tick**: the newest commit whose change to
   `.tdd/issue-<n>.md` touches a line other than a re-pin step's (`⟦diff-checked⟧ edit the
   case of the pin on …`), as `fused_step.green_tick` finds it, so a re-pin plan or tick
   committed while the step still carries the mark is passed over (#4510). The tick is
   atomic with the green commit and the clear that would follow never happened. So `$touched`
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
   to be. Run its **verify-refactor** after it, unless the run pinned it off (below) — the check the interruption skipped — with
   `$green` as the cycle loop's `<green-sha>`:
   `verify.sh --branch-base <base> --step "<STEP>" --fast-cmd '<fast-cmd>' refactor <spec-file> <test-path> "$green"`, launched as there. Its
   PASS clears the mark and commits the cleared ledger exactly as in the cycle loop; then
   come back here and ask sub-step 2 again.
   **Unless `refactor` is listed in `.tdd/issue-<n>-skip-verify`:** then no verify-refactor
   launches, and the cycle loop's *Refactor loop* step 5 **Switched off** branch is taken
   instead — the `verify-refactor-skipped reason=switched-off` event with `VERI_STEP` this
   step, `skipped` in `.tdd/verdict-refactor.exit`, the `SKIPPED (switched off)` comment
   (`$S/comment.sh <n> verify-refactor`), then `pin-recheck.sh`, the pending-mark clear and
   the cleared-ledger commit — before sub-step 2 is asked again. The pin decides, never
   `VERI_SKIP_VERIFY` at the resume: a resumed run keeps the configuration it started with.
3. `next-unchecked.sh < .tdd/issue-<n>.md` gives the **first unchecked step** — the cycle
   loop continues from exactly there, so **STEP** is that step's description, bound here
   instead of at the top of the cycle loop. Already-checked steps (and their commits) are
   kept. Before that pick, plan each criterion that is unticked in the issue body when the
   resume starts and that no ledger step's `⟦criterion k⟧` serves — scope a human amended in —
   with `add-ledger-step.sh --planned --criterion k`, one call per criterion, committed as a
   `plan:` commit before the cycle loop with `git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md`,
   so the insertion records travel with the ledger. Those steps are planned steps, not `⟦added⟧` growth,
   and do not count against `VERI_STEP_GROWTH_PERCENT`. Every other insertion during the resume omits
   --planned, stays `⟦added⟧` and counts. A conductor never sets or raises `VERI_STEP_GROWTH_PERCENT`,
   `REVISE_BUDGET`, `VERI_REFACTOR_BUDGET`, `VERI_STUCK_RETRIES` or `VERI_NO_VERDICT_RETRIES`
   mid-run, in its environment or in a scratch helper, and a budget it cannot fit inside is a bail.
4. Post a `### ▶️ Resuming` comment by running `$S/comment.sh <n> resuming --note-file <path>`, naming that step and, when `$stray` is non-empty, the
   paths it lists, said as what they are: the stray work sub-step 2's reset discarded, seen
   by no verifier and now gone. Mark the pick-up in the log —
   `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/event.sh resume` — then, when
   `.tdd/resume-suite-red` exists, run `$S/suite-red-resume.sh insert .tdd/issue-<n>.md .tdd/resume-suite-red`, commit the
   ledger with `.tdd/issue-<n>-added.md`, and hand the inserted `⟦suite-repair⟧` step to the cycle loop first. When `insert` exits 1 — the growth cap filed the step as
   owed — bail with cause `suite-red`, naming the branch-red suites; when it exits 2 — no answer, or a reorder of pending `⟦skill-edit⟧` steps that a non-skill-edit step separates — bail with cause `no-verdict`, carrying that stderr line, and insert no step. `insert` inserts no step when the union of the units of the consecutive pending `⟦skill-edit⟧` steps from the first unchecked step explains the whole red; the first such `⟦skill-edit⟧` step is then handed to the cycle loop first, and a red those units do not jointly explain still gets the `⟦suite-repair⟧` step;
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
   Before the first step leaf, check whether the plan was rewritten since it was last verified: run
   `$S/plan-reverify.sh .tdd/issue-<n>.md`. On **exit 0** — the newest `plan:` commit is at or after the last
   verify-plan PASS — run step 2c's verify-plan on the ledger; a REJECT follows step 2c's revise-plan route.
   On **exit 3** — every `plan:` commit is older than that PASS — skip verify-plan.
   Then run the cycle loop as normal. Go to the **draft PR** only when
   `next-pending-refactor.sh` and `next-unchecked.sh` have **both** exited 3: every step is
   checked, and every checked step's refactor is verified. An unchecked `⟦full-suite⟧` or
   `⟦human-owed⟧` line does not hold the run back from its draft PR — no cycle ticks either,
   and `next-unchecked.sh` skips both.

Because each step was checked off **atomically with its green commit**, the ledger and the
git history agree on exactly what is done — so resume never repeats or skips a step.
