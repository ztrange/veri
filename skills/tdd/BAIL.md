## Bailing

A **bail** terminally stops this issue while preserving progress (ADR-0011). Each bail has
a **cause token** that maps to a classification via `$S/classify-bail.sh <cause>`:

- `killed-stuck` — `supervise.sh` exited **2** for a developer leaf even after its
  stuck-retry budget → **system** failure (plumbing broke).
- `killed-external` — `supervise.sh` exited **2** for a developer leaf because the leaf died
  with no recorded exit and veri did not kill it (the supervisor's
  `supervise[<name>]: killed-external` status line); never retried → **system** failure,
  distinct from `killed-stuck`.
- `no-verdict` — exit **2** from `verify.sh` / `run-verdict.sh` (a verifier with no verdict:
  unparseable, or the leaf was killed), `grade-prose.sh` (the Draft PR regrade), the
  ⟦skill-edit⟧ runner (`skill-edit-step.sh`, a bare exit 2 with no refusal message; one with a
  refusal message is `skill-edit-refused`), `resume-clean.sh`, `rebase-onto-default.sh`,
  `ledger-growth.sh` (the growth check at a ledger commit) or `cover-outcome.sh` → **system** failure.
- `skill-edit-refused` — the ⟦skill-edit⟧ runner (`skill-edit-step.sh`) exited **2** with a
  refusal message → **process** failure (the runner refused the step deterministically, and
  the plumbing did not break); the bail names the refusal.
- `row-untraced` — the ⟦skill-edit⟧ runner (`skill-edit-step.sh`) exited **1** because a
  `trace-rows` leaf answered `UNTRACED` for a row of the issue → **process** failure (the
  methodology spoke: the row is the issue's, and no author edit makes it true).
- `unreplaced-cases` — `unreplaced-cases.sh` exited **1** a second time, after the one correction
  leaf, naming `⟦replaces-case⟧` cases with no `REPLACES:` line — or exited **2**, no answer, on its first
  check and the adjudication (`Read` `<base directory>/ADJUDICATE.md`) did not route it to the correction
  leaf, or exited **2** on its second check, which bails at once — before verify-green → **process**
  failure, keeping its cause and class after an adjudication.
- `replaces-report-failed` → **system** failure: `wait-leaf.sh develop-replaces-report` exited 1 or 2
  (the correction leaf did not finish cleanly, a killed-stuck one included) before verify-red. The wait's
  exit 2 can be adjudicated first (`Read` `<base directory>/ADJUDICATE.md`): the bail keeps this cause and class.
- `revise-exhausted` — a step spent its `REVISE_BUDGET` and the blind verifier still says
  `REJECT` → **process** failure (methodology spoke).
- `revise-impossible` — a revise leaf answered `IMPOSSIBLE`, saying no revision can meet the
  verifier's objection → **process** failure (methodology spoke), distinct from
  `revise-exhausted`: there the attempts ran out, here the leaf declined to make another.
- `untestable-criterion` — a Red developer leaf reported `AGAINST_UNMODIFIED: UNTESTABLE`:
  the step's criterion cannot be pinned as a lightweight, behavior-level test → **process**
  failure (the criterion as phrased cannot be tested as behavior, not that the plumbing
  broke).
- `step-too-big` — a split was refused for the growth cap, ⌈`VERI_STEP_GROWTH_PERCENT` × P ÷ 100⌉
  (default 50; P the steps of the verified plan, the ledger at the commit `ledger-growth.sh
  plan-sha` prints), so the smaller steps are filed
  under `## Owed steps` rather than in the plan → **process** failure (the step was too big for
  one green; `add-ledger-step.sh` exit 1 says so, and nothing in the plumbing broke). Three
  splits lead here, because all three grow the plan and share that one budget: a Green
  developer leaf's `SPLIT:`, the split the revise-exhausted leaf answers, and the split the
  over-budget leaf answers.
- `step-added-off-route` — `ledger-growth.sh` exited **1** at a ledger commit: a step line the
  plan commit did not hold has no matching record from `add-ledger-step.sh` (in the tracked
  `.tdd/issue-<n>-added.md` or its `step-added` events), lacks `⟦added⟧` when its record shows
  no repair or `--planned` insertion, or the `⟦added⟧` lines exceed `VERI_STEP_GROWTH_PERCENT` of
  the plan's steps →
  **process** failure (the plan grew by a route other than `add-ledger-step.sh`; stderr names
  the line). No commit is made over it. To resume, take the named line out of the uncommitted
  ledger, or put it back in through `add-ledger-step.sh` within `VERI_STEP_GROWTH_PERCENT`, commit, and
  resume the run.
- `step-add-refused` → **system** failure: `add-ledger-step.sh` exited 2 at any of its call
  sites because the anchor matched no step or several, `VERI_STEP_GROWTH_PERCENT` was unreadable or
  the retired `VERI_STEP_GROWTH` was set (any value: the old absolute count no longer bounds
  growth), no plan commit could be read, or
  `--criterion` was malformed (the conductor passed a call the script refused, not a
  methodology answer). The bail can follow an adjudication (`Read`
  `<base directory>/ADJUDICATE.md`): it keeps this cause and class.
- `prep-owed` — `add-ledger-step.sh` refused with exit **1** the step a `prep` answer asks
  for (the insertion would exceed `VERI_STEP_GROWTH_PERCENT` of the plan's steps) → **process** failure (the methodology
  spoke: the prep step is owed and the plan has no room for it, and the plumbing did not
  break); the bail comment names the cases the step was to update.
- `no-seam` — a legacy step's `develop-seam` leaf answered `REACHES: no`: the region has no seam
  that drives it without an edit → **process** failure, carrying the leaf's reason.
- `surround-owed` — the planned stop of a legacy run made before the Surround phase existed:
  every step's seam is confirmed and its next phase is `surround` → **process** failure.
- `surround-short` — a legacy step's mutant table stayed shorter than `VERI_SURROUND_MUTANTS`
  after its one free relaunch of `develop-surround` → **process** failure.
- `tidy-first-owed` — `add-ledger-step.sh` refused with exit **1** the step a green leaf's
  `TIDY_FIRST:` answer asks for (the ledger at `VERI_STEP_GROWTH_PERCENT` of the plan's steps;
  the text is parked under `## Owed steps`) → **process** failure (the methodology spoke: the
  tidy step is owed and the plan has no room for it); the bail comment names the refactoring.
- `pr-ready-failed` — `pr-ready.sh` exited non-zero at the Draft PR step (GitHub refused or
  never answered the ready request, after its refusal retries) → **system** failure (#2581). The bail can follow an
  adjudication (`Read` `<base directory>/ADJUDICATE.md`): it keeps this cause and class.
- `report-missing` — a phase leaf's report carried no `SUITE:` line (`suite-reported.sh` exited
  2) → **system** failure. The bail can follow an adjudication (`Read`
  `<base directory>/ADJUDICATE.md`): it keeps this cause and class.
- `reconcile-failed` — the reconcile of a rejected push failed (the `develop-reconcile` leaf
  exited 1 or 2, the second `push-branch.sh` exited other than 0, or the ledger's ticks or marks
  changed; `RECONCILE.md`) → **system** failure. Its exit-2 sources can be adjudicated first
  (`Read` `<base directory>/ADJUDICATE.md`): the bail keeps this cause and class.
- `criterion-unreadable` — `criterion-finished.sh` exited 2 at a step's mirror (the criterion
  could not be read) → **system** failure. The bail can follow an adjudication (`Read`
  `<base directory>/ADJUDICATE.md`): it keeps this cause and class.
- `rerecord-failed` — `tests-frozen.sh rerecord-refactored` exited **2** (no answer) after a
  verify-refactor PASS or a `skipped` one → **system** failure.
- `go-red-probe-unresolvable` — `go-red-step.sh` stopped at its probe with exit **2** because
  no test file under the worktree defines the ⟦go-red⟧ step's case, or more than one does, so
  `mutation-probe.sh` has no one file to run it in → **system** failure.
- `ci-timeout` — a readied PR's check was still pending when the Draft PR step's bounded CI
  wait ran out → **system** failure (CI never answered, not the methodology). The bail can follow an
  adjudication (`Read` `<base directory>/ADJUDICATE.md`): it keeps this cause and class.
- `ci-conflict` — a readied PR still conflicted with its base branch after the CI step's one
  rebase, so no workflow could start → **system** failure (CI could not answer, not the
  methodology). The bail can follow an adjudication (`Read` `<base directory>/ADJUDICATE.md`): it keeps
  this cause and class.
- `ci-red` — a readied PR's CI check failed again after a CI repair step → **process**
  failure (CI answered, and the repair did not fix what it said).
- `suite-red` — the Draft PR step's full run was red again after a `⟦suite-repair⟧` step →
  **process** failure (the suite answered, and the repair did not fix what it said).
- `rebased-tip-red` — the Draft PR step's full run was red on the tip `rebase-onto-default.sh`
  rebased → **process** failure (the suite answered on the rebased tip).
- `rebase-unresolved` — a rebase not resolved within budget → **process** failure (the
  conflict was not resolved, and the plumbing did not break).
- `branch-rejected` — `verify-branch` said `REJECT` (exit **1**) with `VERI_BRANCH_REPAIRS`
  repair steps already in the ledger → **process** failure (the methodology spoke: the
  branch was judged and the repairs did not satisfy the verifier).
- `missing-reroutes-exhausted` — a step's repeat `missing` reroutes spent
  `VERI_MISSING_REROUTE_BUDGET` and verify-green still names a behaviour no test pins →
  **process** failure (the methodology spoke: the tests still do not pin the criterion).
- `unpinnable-missing` — a missing-reroute's demanded case is green on the before-state and
  cannot be pinned → **process** failure (the methodology spoke: the verifier demanded a test
  that no red-first case can pin, and the plumbing did not break).
- `repair-reroutes-exhausted` — a step's `WRONG_TEST` naming no case took its `repair` once
  more after the free reroute, and the next such report still names no case → **process**
  failure (the methodology spoke: the verifier still cannot say which test is wrong).
- `graded-edit-outside-skill-edit` — a step not marked `⟦skill-edit⟧` changed a unit listed
  in a `GRADED` file (`graded-changed.sh` exited **1**) → **process** failure (the step
  edited graded prose by a route other than the ⟦skill-edit⟧ runner, and the plumbing did
  not break).
- `unwired` — `unwired.sh` exited **1** at the Draft PR step: the run's range adds a non-test
  file that no other non-test file names → **process** failure (the methodology spoke: code
  nothing reaches is not delivered); the PR stays a draft. A human wires each named file into a
  caller or removes it, then runs `release-issue.sh <n>`. A file wired in a way a stem search
  cannot see (a Go file of the same package, a migration found by its framework) can stay: the
  bail recorded every listed file as pending in `.tdd/issue-<n>-unwired-pending`, and only a
  successful release (`release-issue.sh <n>` exit 0) accepts them, moving every pending file
  to `.tdd/issue-<n>-unwired-accepted`; a release that exits 2 accepts none. A resume without a
  release bails `unwired` again; a released run's resume goes on when every file `unwired.sh`
  prints is accepted and bails `unwired` again when one is not.

**A bail reached first stays a bail**, whatever stop is waiting behind it: the methodology or
the plumbing has already answered, and a pause would hide that answer from the resume. Ask
`$S/stop-requested.sh` once before sub-step 1 and keep what it printed. A `REJECT` that
exhausts `REVISE_BUDGET` bails even with a stop pending, and a killed-stuck leaf with no `now`
pending bails as it always has — only a pending `now` turns a leaf's exit 2 into the stop
(see *Launching a leaf*). When exit 0 said one was waiting, the bail comment in sub-step 6
adds that a stop was pending, naming its mode.

You may run `$S/bail.sh <n> <cause> <phase> --note-file <path> [--attempt <k>]` for
sub-steps 1–8 below. On its exit 2, or with the script unavailable, bail by the sub-steps
below, every one of which stays.

To bail:

0. **Ask whether the rule may be waived.** Before the bail is classified or anything is reset,
   check whether its cause is one `ADJUDICATE.md`'s *Waivable rules* names
   (`graded-edit-outside-skill-edit`, rule `graded-edit`). If it is, and
   `$S/adjudicate.sh left <n>` and `$S/adjudicate.sh deviation-left <n>` both exit 0, run the
   adjudicator as `ADJUDICATE.md`'s *Procedure* says. On `deviate` (exit 4) the run does not
   bail: it takes the rule's resume action. For `graded-edit` that is: keep the step's commit,
   append through `add-ledger-step.sh` one `⟦added⟧` `⟦skill-edit⟧` step naming each unit
   `graded-changed.sh` printed (it counts against `VERI_STEP_GROWTH_PERCENT`), then go on from
   the refusing step's next sub-step; an `add-ledger-step.sh` refusal bails with the original
   cause. Any other answer, or either budget spent or unreadable (exit 3 or 2), goes on to
   sub-step 1 with the original cause and class. `bail.sh` does not run this sub-step.
1. **Preserve the attempt first.** The tree the troubled leaf left is the evidence a reader
   of this bail will want, and the very next step throws it away — so snapshot it before the
   reset, from inside the worktree:
   ```
   $S/preserve-attempt.sh <n> "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" <phase> <attempt> bail
   ```
   `<phase>` is the leaf whose trouble caused the bail (`develop-green`, `verify-red`, …) and
   `<attempt>` its number (`1` outside the revise loop, `k` inside it). Best-effort: note it
   if it fails and bail anyway — a bail that stops for a failed snapshot loses the report too.
2. **Revert only the half-done step.** Completed steps are committed; the failing step's
   test/code is still uncommitted (the cycle bailed before its atomic green commit). Drop
   exactly that half-done work — `git reset --hard HEAD` — which leaves every completed
   step's commit (and the ledger's checked steps) intact.
3. **Classify deterministically.** `classification="$($S/classify-bail.sh <cause>)"`
   (`<cause>` is one of the tokens above). This keeps the label consistent rather than
   ad-hoc; an unknown token makes it exit non-zero — pick the right token. Then mark the stop
   in the log — the mark sub-step 6's `### ⛔ Bailed` comment mirrors — with the cause token
   and that classification, before anything renders it:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" VERI_PHASE=<phase> $S/event.sh bail cause=<cause> classification="$classification"
   ```
4. **Render and commit the metrics**, from inside the worktree and before the push, so the
   branch carrying the progress carries the account of it too: `$S/metrics.sh <n> >
   .tdd/issue-<n>-metrics.md; metrics=$?`, then `if [ "$metrics" = 0 ]; then git add
   .tdd/issue-<n>-metrics.md && git commit -m "metrics: what bailing on #<n> cost (#<n>)";
   fi`. This is the ending the report is worth most at — every attempt a bailed step spent is waste, and only the file says how much.
5. **Push the branch** so completed steps, that metrics commit and the leaf logs are
   recoverable, from inside the worktree (where you already are):
   `git push -u origin tdd/<n>-<slug>` (best-effort; note if it fails).
6. Post the `### ⛔ Bailed — <phase> (<classification> failure)` comment by running
   `$S/comment.sh <n> bailed --note-file <path>`, the note carrying what only you know. The comment names the phase,
   carries the `### 📊 Metrics` block just committed (or, when `$metrics` is not 0, the line
   `metrics could not be rendered: metrics.sh exited $metrics` in its place), carries the last reason
   (`.tdd/verify-<phase>.reason` on a `revise-exhausted` bail, the develop-red leaf's `WHY:`
   line on an `untestable-criterion` bail, `.tdd/pr-ready.err`'s text on a `pr-ready-failed` bail,
   the kill cause otherwise; a `ci-red` bail's reason
   names each CI check that failed, the `failed=` field its bail mark read from the head's
   check runs),
   then, after the reason, the skill-drift block — the stdout of `drift="$($S/skill-drift.sh)";
   drift_exit=$?`, or, when `$drift_exit` is not 0, the line `Skill drift: unavailable —
   skill-drift.sh exited $drift_exit` in its place, and the bail goes on either way —
   and points at the progress log (`.tdd/<phase>.log` or
   `.tdd/revise-<phase>-*.log`) for forensics.
7. **Leave the draft PR open, and put the bail diagnostic on it.** Step 2.3 opened it at the
   plan commit, and it is the run's claim on this issue: `solvable-issues.sh` leaves out an
   issue an open PR says `Closes #<n>` for, so taking it down would hand the issue back to
   the pool for the next machine to re-take and re-bail, and would discard the visible record
   a bail exists to leave. A bail also means a human has to look, and the draft PR is where
   they look — so the comment sub-step 6 posted to the issue thread reaches the PR too, or the
   page a reader opens still says a run is in progress when it stopped:
   ```
   gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'   # → <pr-url>, the PR step 2.3 opened; <pr-number> is its last path segment
   $S/comment.sh <n> bailed --pr --note-file <path>   # posts the same ### ⛔ Bailed — <phase> (<classification> failure) comment to repos/{owner}/{repo}/issues/<pr-number>/comments
   ```
   (A link to the issue comment sub-step 6 posted may stand in for the full comment.)
   Either way the PR carries sub-step 6's skill-drift block: a link-only comment quotes that
   block alongside the link.
   It stays a **draft**: nobody is asked to review a run that stopped. The ledger's completed
   steps stay checked, so a re-run resumes from the failing step (see `RESUME.md`) and edits this
   same PR rather than opening another.
8. Report to the user: the phase, the **classification** (system vs process), the reason,
   sub-step 6's skill-drift block, the branch name, and the **worktree path** — the logs named above are inside it, and it
   is where a re-run will resume. Leave it in place; only a merged PR retires it.
