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
  ⟦skill-edit⟧ runner (`skill-edit-step.sh`), `resume-clean.sh`, `rebase-onto-default.sh`,
  `ledger-growth.sh` (the growth check at a ledger commit) or `cover-outcome.sh` → **system** failure.
- `unreplaced-cases` — `unreplaced-cases.sh` exited **1** a second time, after the one correction
  leaf, naming `⟦replaces-case⟧` cases with no `REPLACES:` line (or exited **2**, no answer, which
  bails at once with no correction) before verify-green → **process** failure.
- `replaces-report-failed` → **system** failure: `wait-leaf.sh develop-replaces-report` exited 1 or 2
  (the correction leaf did not finish cleanly, a killed-stuck one included) before verify-red.
- `revise-exhausted` — a step spent its `REVISE_BUDGET` and the blind verifier still says
  `REJECT` → **process** failure (methodology spoke).
- `revise-impossible` — a revise leaf answered `IMPOSSIBLE`, saying no revision can meet the
  verifier's objection → **process** failure (methodology spoke), distinct from
  `revise-exhausted`: there the attempts ran out, here the leaf declined to make another.
- `untestable-criterion` — a Red developer leaf reported `AGAINST_UNMODIFIED: UNTESTABLE`:
  the step's criterion cannot be pinned as a lightweight, behavior-level test → **process**
  failure (the criterion as phrased cannot be tested as behavior, not that the plumbing
  broke).
- `step-too-big` — a split was refused for `VERI_STEP_GROWTH`, so the smaller steps are filed
  under `## Owed steps` rather than in the plan → **process** failure (the step was too big for
  one green; `add-ledger-step.sh` exit 1 says so, and nothing in the plumbing broke). Three
  splits lead here, because all three grow the plan and share that one budget: a Green
  developer leaf's `SPLIT:`, the split the revise-exhausted leaf answers, and the split the
  over-budget leaf answers.
- `step-added-off-route` — `ledger-growth.sh` exited **1** at a ledger commit: a step line the
  plan commit did not hold has no matching record from `add-ledger-step.sh` (in the tracked
  `.tdd/issue-<n>-added.md` or its `step-added` events), lacks `⟦added⟧` when its record shows
  no repair or `--planned` insertion, or the `⟦added⟧` lines exceed `VERI_STEP_GROWTH` →
  **process** failure (the plan grew by a route other than `add-ledger-step.sh`; stderr names
  the line). No commit is made over it. To resume, take the named line out of the uncommitted
  ledger, or put it back in through `add-ledger-step.sh` within `VERI_STEP_GROWTH`, commit, and
  resume the run.
- `step-add-refused` → **system** failure: `add-ledger-step.sh` exited 2 at any of its call
  sites because the anchor matched no step or several, `VERI_STEP_GROWTH` was unreadable, or
  `--criterion` was malformed (the conductor passed a call the script refused, not a
  methodology answer).
- `pr-ready-failed` — `pr-ready.sh` exited non-zero at the Draft PR step (GitHub refused or
  never answered the ready request, after its refusal retries) → **system** failure (#2581).
- `ci-timeout` — a readied PR's check was still pending when the Draft PR step's bounded CI
  wait ran out → **system** failure (CI never answered, not the methodology).
- `ci-conflict` — a readied PR still conflicted with its base branch after the CI step's one
  rebase, so no workflow could start → **system** failure (CI could not answer, not the
  methodology).
- `ci-red` — a readied PR's CI check failed again after a CI repair step → **process**
  failure (CI answered, and the repair did not fix what it said).
- `suite-red` — the Draft PR step's full run was red again after a `⟦suite-repair⟧` step →
  **process** failure (the suite answered, and the repair did not fix what it said).
- `rebased-tip-red` — the Draft PR step's full run was red on the tip `rebase-onto-default.sh`
  rebased → **process** failure (the suite answered on the rebased tip).
- `rebase-unresolved` — a rebase not resolved within budget → **process** failure (the
  conflict was not resolved, and the plumbing did not break).
- `missing-reroutes-exhausted` — a step's repeat `missing` reroutes spent
  `VERI_MISSING_REROUTE_BUDGET` and verify-green still names a behaviour no test pins →
  **process** failure (the methodology spoke: the tests still do not pin the criterion).
- `graded-edit-outside-skill-edit` — a step not marked `⟦skill-edit⟧` changed a unit listed
  in a `GRADED` file (`graded-changed.sh` exited **1**) → **process** failure (the step
  edited graded prose by a route other than the ⟦skill-edit⟧ runner, and the plumbing did
  not break).

**A bail reached first stays a bail**, whatever stop is waiting behind it: the methodology or
the plumbing has already answered, and a pause would hide that answer from the resume. Ask
`$S/stop-requested.sh` once before sub-step 1 and keep what it printed. A `REJECT` that
exhausts `REVISE_BUDGET` bails even with a stop pending, and a killed-stuck leaf with no `now`
pending bails as it always has — only a pending `now` turns a leaf's exit 2 into the stop
(see *Launching a leaf*). When exit 0 said one was waiting, the bail comment in sub-step 6
adds that a stop was pending, naming its mode.

To bail:

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
6. Post a `### ⛔ Bailed — <phase> (<classification> failure)` comment that names the phase,
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
   gh api repos/{owner}/{repo}/issues/<pr-number>/comments -f body="<the same ### ⛔ Bailed — <phase> (<classification> failure) comment, or a link to the issue comment sub-step 6 posted>"
   ```
   Either way the PR carries sub-step 6's skill-drift block: a link-only comment quotes that
   block alongside the link.
   It stays a **draft**: nobody is asked to review a run that stopped. The ledger's completed
   steps stay checked, so a re-run resumes from the failing step (see `RESUME.md`) and edits this
   same PR rather than opening another.
8. Report to the user: the phase, the **classification** (system vs process), the reason,
   sub-step 6's skill-drift block, the branch name, and the **worktree path** — the logs named above are inside it, and it
   is where a re-run will resume. Leave it in place; only a merged PR retires it.
