---
name: solve-issue
description: >-
  Drive one GitHub issue end-to-end under TDD: scope it into a committed plan ledger, then
  loop Red → Green → Refactor cycles — each blind-verified by an independent agent — until
  every acceptance criterion is covered, narrating each phase to the issue thread and
  leaving the result on a draft PR. Resumable from the ledger. Invoke as
  `/solve-issue <number>`. Use when the user names one GitHub issue to solve under TDD.
---

# solve-issue — the veri conductor

You are the **conductor**. You drive exactly one GitHub issue end-to-end, looping a Red →
Green → Refactor cycle over every step of its plan, but you **write no code yourself**.
Each phase is performed by a short-lived developer **leaf** (`claude -p` subprocess), and
after each phase a separate **blind independent verifier** leaf confirms the work. Every
leaf — developer or verifier — is launched **through the supervisor** (`supervise.sh`),
never directly, so a hung or runaway leaf is killed instead of stalling the whole run. You
orchestrate the leaves, branch on their verdicts, narrate every phase and verdict to the
issue thread, and leave the result on a **draft PR** for a human to review and merge.

This slice lifts veri from a single criterion to a **full multi-criterion issue**, solved
by a **resumable loop** over a committed **ledger**, on top of everything earlier (blind
verification, the supervisor, and the two retry axes — the **revise loop** on a `REJECT`
and the supervisor's **stuck-retry**, all still in force):

- **Scope & plan → ledger.** The conductor decomposes the issue into a checklist of small
  steps — each one cycle's worth, aligned to an acceptance criterion — written to a
  committed per-issue **ledger** (`.tdd/issue-<n>.md`) that is the **source of truth** for
  which steps are done, and mirrored to the issue thread.
- **The cycle loop.** The conductor loops Red → Green → Refactor over the ledger's steps
  until every criterion is covered, checking each step off in the ledger **atomically with
  its green commit** so git and ledger never diverge.
- **Resume.** Re-running `/solve-issue <n>` reads the ledger and continues from the first
  unchecked step.

Hardened edges (#7) have since landed too, and are described below: the preflight
baseline bail, reverting only the half-done step, and deterministic cause classification.
Still **out of scope**: the loop and parallel rungs of the scope ladder. A step that
exhausts its revise budget, or a leaf that stays killed-stuck past the supervisor's
budget, **bails** — preserving completed steps' commits and classifying the cause
(process vs system).

## The two roles, and why the verifier is blind

- A **developer leaf** writes the failing test, the implementation, or the refactor. It
  is allowed to see everything: the issue, the repo, the prior phases.
- A **verifier leaf** confirms one developer claim. It is **blind**: it receives only the
  test, the issue's behavior spec, and the repo — never the developer's rationale — and
  it establishes ground truth by **running the test itself**. Blindness is enforced
  structurally: the verifier prompt is built by `build-verify-prompt.sh`, whose only
  inputs are the spec and the test path, so the developer's reasoning physically cannot
  reach it (see ADR-0003).

You — the conductor — must keep these roles distinct. Do **not** write the test or the
implementation yourself, and do **not** pass a developer leaf's explanation into a
verification.

## The scripts (this skill's `scripts/` directory)

Let `S=<base directory>/scripts`, where *base directory* is the path the harness printed
when this skill loaded (`Base directory for this skill: …/solve-issue`). It is the same
skill whether it lives in the target repo's `.claude/skills/` or is symlinked into
`~/.claude/skills/` for use from any repo — never assume a repo-relative path. All leaf
machinery lives there and is unit-tested (`$S/tests/*.test.sh`):

- `$S/supervise.sh <name> <cmd> [args...]` — **the leaf launcher.** Spawns `<cmd>` under a
  heartbeat + hard-timeout watchdog, owns the `.tdd/<name>.log` progress log, and returns
  the captured output on stdout. **Exit 0 = success, 1 = leaf-failure, 2 = killed-stuck**
  (hung past the heartbeat window or over the hard timeout, **after** its stuck-retry
  budget). A one-line status goes to stderr. Tunables: `VERI_HEARTBEAT` (silence window s,
  default 45), `VERI_TIMEOUT` (hard cap s, default 900), `VERI_STUCK_RETRIES` (extra
  attempts after a killed-stuck, default 1 — the **liveness** axis, independent of the
  conductor's verdict-axis `REVISE_BUDGET`). Because leaves **stream** (below), the default
  `VERI_HEARTBEAT` is a real silence window — a working leaf keeps it fresh, a genuinely
  hung one trips it — so just use the defaults; no need to pin heartbeat to the timeout.
  **Every leaf is launched through this — never call `run-leaf.sh` or `claude` directly.**
- `$S/run-leaf.sh <prompt-file|-> [claude args...]` — the inner leaf invocation. Runs
  `claude -p --output-format stream-json` so the leaf **streams events as it works** (that
  is the supervisor's heartbeat), then appends the clean final result. You always run it
  *via* `supervise.sh`, not on its own.
- `$S/extract-result.sh` — pulls the final result text out of a leaf's stream-json (used
  by `run-leaf.sh`; passes plain text through unchanged).
- `$S/build-verify-prompt.sh <red|green|refactor|pin> <spec-file> <test-path> [target]` —
  assemble the blind verifier prompt. Used by `verify.sh`; you rarely call it directly.
- `$S/verify.sh <red|green|refactor|pin> <spec-file> <test-path> [target]` — the **verify
  verb**: build the blind prompt → launch the verifier leaf **through the supervisor** →
  parse the verdict. Prints the verifier's **reason** on stdout; **exit 0 = PASS, 1 =
  REJECT, 2 = malformed or killed-stuck**. The `pin` phase is the *already satisfied*
  check: the verifier confirms the test passes now, **fails** under a behaviour-removing
  mutation it applies and then reverts itself, and is behaviour-level — the same trivial
  / over-coupled / too-complex bar as `red`.
- `$S/parse-verdict.sh` — extracts `PASS|REJECT` + reason from a leaf's output (used by
  `verify.sh`).
- `$S/tick-criterion.sh '<substring>'` — the pure text transform both tick wrappers
  delegate to: reads a checkbox body on stdin, flips the first unchecked `- [ ]` matching
  the substring, writes it back on stdout. **Exit 3** if nothing matched.
- `$S/tick-issue-criterion.sh <n> '<substring>'` — tick a criterion checkbox in the
  issue body (the human-facing mirror).
- `$S/next-unchecked.sh < .tdd/issue-<n>.md` — print the **first unchecked ledger step**'s
  description; **exit 3** when none remain (the loop-done / nothing-to-resume signal).
- `$S/tick-ledger.sh .tdd/issue-<n>.md '<substring>'` — check a step off in the **committed
  ledger**, in place (staged + committed together with that step's green code).
- `$S/classify-bail.sh <cause>` — deterministically classify a bail cause
  (`killed-stuck`/`no-verdict` → `system`, `revise-exhausted` → `process`; unknown → exit
  non-zero). Used in the *Bailing* step so the classification is consistent, not ad-hoc.
- `$S/ensure-run-state-ignored.sh [repo-root]` — make the **target repo** ignore veri's run
  scratch (`.tdd/*.log`, `.rc`, `.prompt`, the blind spec) while keeping the ledger
  tracked. Idempotent; prints `added` when it wrote the rule, `already present` when it
  was there. Run once per issue right after branching (step 1) so the first `git add -A`
  never sweeps leaf logs into history.

## Inputs

- `$ARGUMENTS` contains the issue **number** `<n>`. If no number was given, ask the user
  for one and stop until they answer.

## Procedure

Work through these steps in order. If a **preflight** step fails, stop and tell the user
what is wrong — do not start a cycle on a poisoned baseline. Once the cycle is underway,
drive it to a draft PR or to a clean stop on a `REJECT`.

### 0. Preflight — baseline checks (bail before any cycle)

These run **first**, before any branch or cycle. If any fails, the baseline is poisoned —
**bail immediately**: report which check failed and stop. This is a degenerate bail (no
branch, no commits, nothing to revert or push) — just refuse to start. A red, dirty, or
unauthenticated baseline never gets a cycle.

1. **Git repo & clean tree.** `git rev-parse --is-inside-work-tree` succeeds and
   `git status --porcelain` is empty. If dirty, stop and ask the user to commit or stash.
2. **`gh` and `claude` authenticated.** `gh auth status` succeeds, and `claude auth status`
   reports `"loggedIn": true`. Every leaf is a `claude -p` subprocess: with an expired
   session each one fails at launch (`supervise.sh` exit 1 before any work), which is
   neither a verdict nor a hang and so has no bail classification — catch it here.
3. **Suite is green at baseline.** Determine the test command (see *Detecting the test
   command*) and run it. If already red, stop and report — a cycle must not start on a
   red baseline.
4. **Default branch.** Capture it for the PR base:
   `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.

### 1. Read the issue, capture the spec, and branch (or resume)

1. Read the issue: `gh issue view <n> --json number,title,body,url`.
2. **Write the behavior spec to a file** the verifier leaves will read:
   `mkdir -p .tdd && gh issue view <n> --json body -q .body > .tdd/issue-<n>-spec.md`.
   (The verifier is blind; this on-disk spec — never your narration — is what it sees.)
3. Derive a slug from the title — lowercase, non-alphanumerics to `-`, collapse and trim
   `-`, cap to ~6 words. Create and switch to the per-issue branch:
   `git switch -c tdd/<n>-<slug>` (off the default branch). If it already exists, switch.
4. **Ignore run state.** `$S/ensure-run-state-ignored.sh` makes the target's `.gitignore`
   ignore `.tdd/*` except the ledger. If it prints `added`, commit that as the branch's
   first commit: `git add .gitignore && git commit -m "chore: ignore veri run state (#<n>)"`.
   `already present` means nothing to do. Without this, the atomic `git add -A` in Green
   would commit every leaf log and prompt.
5. **Resume check.** If `.tdd/issue-<n>.md` (the ledger) already exists on the branch, this
   is a **resume**: skip step 2 (the plan is already written), post a `### ▶️ Resuming`
   comment naming the next unchecked step, and go straight to the cycle loop (step 3).
   Otherwise continue to step 2 to scope and plan.

### 2. Scope & plan → the ledger

Decompose the issue into a **plan**: a checklist of small steps, each one cycle's worth and
aligned to an acceptance criterion. Surface sizing (note if a step looks too big to be one
cycle) but do **not** gate on it.

1. Write the plan as a checkbox list to the **ledger** `.tdd/issue-<n>.md`, e.g.:
   ```
   # Plan for #<n> — <issue title>

   - [ ] <step 1: a behaviour-level criterion, one cycle's worth>
   - [ ] <step 2: …>
   ```
   Each step's text should be a distinctive, behaviour-level description — it doubles as the
   substring you will pass to `tick-ledger.sh`. Prefer the issue's own acceptance-criteria
   wording where it maps cleanly to one cycle.
2. **Commit the ledger** as the run's starting point:
   `git add .tdd/issue-<n>.md && git commit -m "plan: scope #<n> into <k> steps (#<n>)"`.
   (The ledger is committed — step 1.4 guaranteed `.gitignore` tracks `.tdd/issue-*.md`
   while ignoring leaf logs.)
3. **Mirror the plan** to the issue thread: post a `### 🗺️ Plan` comment listing the steps,
   noting that the ledger is the source of truth and each step will be blind-verified.

### 2b. Start comment

Post a short comment announcing veri has started, naming the branch and the number of plan
steps, and noting each phase will be blind-verified: `gh issue comment <n> --body "..."`.

### 3. The cycle loop

Loop until the ledger has no unchecked step. Each iteration runs **one full cycle** (Red →
Green → Refactor) for the next step:

```
$S/next-unchecked.sh < .tdd/issue-<n>.md        # exit 3 ⇒ all steps done → go to step 4 (PR)
```

Let **STEP** be that step's description. Run the Red, Green, and Refactor phases below
**against STEP's criterion** (use STEP's wording as the criterion the leaves pin, and as
the `<substring>` for ticking). When a step's cycle completes (refactor verified), loop
back to `next-unchecked.sh` for the following step. The phase sub-steps are:

#### Red — one failing test (developer leaf), then verify-red (blind)

1. **Develop.** Compose a developer-leaf prompt that instructs it to write **exactly one**
   failing test pinning **STEP's criterion** to **observable external behavior** (not internals),
   with **no production code**, and to run it and confirm it fails for the right reason.
   Include in the prompt: the issue's behavior spec, the test command, and the target test
   file/name. **Require the leaf to end its report with the line
   `AGAINST_UNMODIFIED: FAILS | PASSES`** — whether the test fails against the *unmodified*
   code. A criterion earlier work already satisfies cannot yield a failing test, and that
   fact has to reach you as data: in #30's step 3 it did not, and a faithful test spent two
   verify-red `REJECT`s and two revise leaves reporting IMPOSSIBLE before the run bailed and
   the revert discarded it. Write the prompt to `.tdd/develop-red.prompt`, then launch the
   leaf **through the supervisor**:
   ```
   $S/supervise.sh develop-red $S/run-leaf.sh .tdd/develop-red.prompt --permission-mode bypassPermissions
   ```
   If `supervise.sh` exits **2 (killed-stuck)**, the leaf hung or ran away — **bail**
   cleanly (see *Bailing on a killed-stuck leaf*); do not retry. Otherwise the leaf wrote
   the test to disk — note the **test path** and **target test id** it used.
2. **Verify (blind).** Branch on the leaf's `AGAINST_UNMODIFIED` line. On **`FAILS`**, run
   the red verifier against the on-disk test and spec:
   ```
   $S/verify.sh red .tdd/issue-<n>-spec.md <test-path> <target-test-id>
   ```
   On **`PASSES`** the criterion is **already satisfied** — never send that test to
   verify-red, whose verdict on a passing test can only be `REJECT`. Run the pin check
   instead and continue at *Already satisfied — the pin*:
   ```
   $S/verify.sh pin .tdd/issue-<n>-spec.md <test-path> <target-test-id>
   ```
   Either way, capture its **stdout (the reason)** and its **exit code**.
3. **Narrate + branch (the `FAILS` path).** Post a `### 🔴 Red` comment with the test and
   the failing output, followed by a `### 🔎 verify-red — PASS|REJECT` comment carrying the
   verifier's reason.
   - **PASS (exit 0):** continue to Green.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. It
     returns either PASS (continue to Green) or budget-exhausted (**bail**, process failure).
   - **Malformed / killed-stuck (exit 2):** the verdict could not be obtained (unparseable
     or the verifier leaf was killed) — **bail** as a system failure (see *Bailing*), not a
     clean process stop.

#### Green — minimum implementation (developer leaf), then verify-green (blind)

1. **Develop.** Compose a developer-leaf prompt to write the **minimum** production code
   that makes the failing test pass — no generality, options, or cases the test does not
   demand — and to run the **full suite** and confirm green. Include the spec, the test
   command, and the target test. Write to `.tdd/develop-green.prompt` and launch **through
   the supervisor** (exit **2** → **bail**):
   ```
   $S/supervise.sh develop-green $S/run-leaf.sh .tdd/develop-green.prompt --permission-mode bypassPermissions
   ```
2. **Verify (blind).** `$S/verify.sh green .tdd/issue-<n>-spec.md <test-path> <target-test-id>`.
3. **Narrate + branch.** Post `### 🟢 Green` (implementation + green suite output) and
   `### 🔎 verify-green — PASS|REJECT` (the reason).
   - **PASS — check off the ledger step and commit atomically.** Tick STEP in the ledger,
     then commit the code **and** the ticked ledger in **one** commit so git and ledger
     never diverge:
     ```
     $S/tick-ledger.sh .tdd/issue-<n>.md '<distinctive substring of STEP>'
     git add -A && git commit -m "feat: <STEP summary> (#<n>)"
     ```
     Continue to the Refactor loop.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. On a
     recovered PASS, do the same atomic tick-and-commit and continue; on budget-exhausted,
     **bail**.
   - **Malformed / killed-stuck (exit 2):** **bail** — see *Bailing*.

#### Refactor loop — behavior-preserving transforms until none, then verify-refactor (blind, once)

1. **Loop the transforms.** Repeatedly launch a developer leaf that applies **one**
   behavior-preserving transformation (naming, duplication, clarity) and runs the **full
   suite**, keeping it green (revert any change that breaks it). Each leaf returns either
   "applied <transform>, suite green" or "nothing left to tidy". Keep going until a leaf
   reports **nothing remains** (or you've made the codebase genuinely clean). Crucial rule:
   **no untested generality** — generality comes only from **triangulation**. If the code
   is **overfit** (e.g. hard-codes the one tested case), the leaf must **flag it as needing
   a triangulating test**, *not* hand-generalize it. Write each prompt to
   `.tdd/develop-refactor.prompt` and launch **through the supervisor** (exit **2** → **bail**):
   ```
   $S/supervise.sh develop-refactor $S/run-leaf.sh .tdd/develop-refactor.prompt --permission-mode bypassPermissions
   ```
   Commit a transform only if it changed something:
   `git add -A && git commit -m "refactor: <what> (#<n>)"`.
2. **Verify (blind, once) on the settled result.** `$S/verify.sh refactor .tdd/issue-<n>-spec.md <test-path>`
   — one verdict on the final state (suite still green, code up to standard, no smuggled
   generality).
3. **Narrate + branch.** Post `### 🛠️ Refactor` (the transforms applied, or "no refactor
   warranted", plus any triangulation flagged) and `### 🔎 verify-refactor — PASS|REJECT`.
   - **PASS:** the step's cycle is complete — **mirror to the issue**: post a `### ✅ Step
     done` comment, and tick the matching acceptance criterion in the **issue body**
     (`$S/tick-issue-criterion.sh <n> '<substring>'`, the human mirror). Then loop back to
     the top of **step 3** for the next unchecked ledger step.
   - **REJECT (exit 1):** enter the **revise loop**; on recovered PASS, mirror and loop; on
     budget-exhausted, **bail**. (Earlier steps' commits are preserved.)
   - **Malformed / killed-stuck (exit 2):** **bail**. (Earlier steps' commits are preserved.)

### 4. Draft PR

Reached when `next-unchecked.sh` exits 3 — every ledger step is checked off. The full suite
must be green and all work committed before this step.

1. Push the branch: `git push -u origin tdd/<n>-<slug>`.
2. Open a **draft** PR linked to the issue; the body must contain `Closes #<n>`:
   ```
   gh pr create --draft --base <default-branch> \
     --title "<type>: <criterion summary> (#<n>)" \
     --body "Closes #<n>

   <summary: the plan's steps, each a blind-verified R→G→R cycle, ledger committed>"
   ```
3. **Never merge the PR.** Landing the code is always the human's deliberate act.
4. Post a final `### ✅ Done — <pr-url>` comment.

Report back to the user with the branch name and the PR URL.

## Already satisfied — the pin

A step whose criterion **earlier work already satisfies** has no failing test to write: the
honest test passes against the unmodified code. That is an **outcome** of the step, not a
failure of it — the behaviour exists and what it wants is a **regression pin**. You reach
this section from Red when the developer leaf reported `AGAINST_UNMODIFIED: PASSES` and you
ran `$S/verify.sh pin …` in place of verify-red. Its verdict replaces the
`### 🔴 Red` / `### 🔎 verify-red` pair:

- **PASS (exit 0) — commit the test as the pin, ticking the ledger atomically.** Same
  tick-and-commit shape as Green, but the commit carries the **test alone** and the `test:`
  type, because no production code was written (the verifier reverted its own mutation, so
  the tree holds only the new test and the ticked ledger):
  ```
  $S/tick-ledger.sh .tdd/issue-<n>.md '<distinctive substring of STEP>'
  git add -A && git commit -m "test: pin <STEP summary> (#<n>)"
  ```
  Then **mirror**: post a `### 📌 Already satisfied — <STEP>` comment carrying the
  verifier's reason, and tick the matching acceptance criterion in the **issue body**
  (`$S/tick-issue-criterion.sh <n> '<substring>'`). The step is **done** — **no Green and
  no Refactor**, since there is no new production code to write or to tidy. Loop back to
  the top of **step 3** for the next unchecked ledger step.
- **REJECT (exit 1):** enter the **revise loop** for the red phase — see *Revising on a
  REJECT*. The rejection reason is the carry-forward signal that tells the fresh leaf which
  way to go: either the pin is weak (trivial, over-coupled, or it survives the mutation) or
  a genuinely failing test exists after all. Re-verify with the phase the revise leaf's own
  `AGAINST_UNMODIFIED` line selects — `pin` on `PASSES`, `red` on `FAILS`. On a recovered
  `PASS` from `pin`, do the tick-and-commit above; from `red`, continue to Green. On
  budget-exhausted, **bail** as a **process** failure.
- **Malformed / killed-stuck (exit 2):** **bail** as a **system** failure (`no-verdict`) —
  see *Bailing*.

## Revising on a REJECT

A `REJECT` (verify.sh exit **1**) does **not** stop the run. The conductor gets a bounded
**attempt budget** — `REVISE_BUDGET` revise attempts, **default 2** — to satisfy the blind
verifier before bailing the step. The rejection **reason is the carry-forward signal**:
leaves never share context, so each revise leaf is told explicitly what to fix.

For attempt `k = 1 … REVISE_BUDGET`:

1. **Mirror.** Post a `### ♻️ Revise <phase> — attempt <k>/<REVISE_BUDGET>` comment carrying
   the verifier's **rejection reason verbatim**.
2. **Fresh developer leaf.** Compose a revise prompt that includes the issue spec, the
   **current test and/or code on disk**, and the **rejection reason**, instructing a brand-
   new leaf to address *that specific objection* — rewrite the test (red), fix the
   implementation (green), or redo the tidy-up (refactor) — without drifting beyond what the
   criterion and the reason require. Write it to `.tdd/revise-<phase>-<k>.prompt` and launch
   **through the supervisor** (exit **2 → bail**, system failure):
   ```
   $S/supervise.sh revise-<phase>-<k> $S/run-leaf.sh .tdd/revise-<phase>-<k>.prompt --permission-mode bypassPermissions
   ```
3. **Re-verify (blind, same phase).** `$S/verify.sh <phase> .tdd/issue-<n>-spec.md <test-path> [target]`.
   - **PASS (exit 0):** the step is recovered. Post `### 🔎 verify-<phase> (revised) — PASS`
     with the reason, and resume the cycle from where that phase's PASS would continue.
   - **REJECT (exit 1):** if attempts remain, loop; otherwise fall through to the bail below.
   - **Malformed / killed-stuck (exit 2):** **bail** (system failure).

If all `REVISE_BUDGET` attempts are still `REJECT`, **bail the step** as a **process
failure** (the methodology could not satisfy the blind verifier within budget), recording
the **last rejection reason**.

`REVISE_BUDGET` (verdict axis) is **independent** of the supervisor's `VERI_STUCK_RETRIES`
(liveness axis): the first governs a leaf that finished with a bad verdict, the second a
leaf that never produced one. A `REJECT` is veri working as designed — the blind verifier
refusing to rubber-stamp — so the bounded revise is a *correction*, never an excuse to keep
hammering past the budget.

## Bailing

A **bail** terminally stops this issue while preserving progress (ADR-0011). Each bail has
a **cause token** that maps to a classification via `$S/classify-bail.sh <cause>`:

- `killed-stuck` — `supervise.sh` exited **2** for a developer leaf even after its
  stuck-retry budget → **system** failure (plumbing broke).
- `no-verdict` — `verify.sh` exited **2** (unparseable verdict, or the verifier leaf was
  killed) → **system** failure.
- `revise-exhausted` — a step spent its `REVISE_BUDGET` and the blind verifier still says
  `REJECT` → **process** failure (methodology spoke).

To bail:

1. **Revert only the half-done step.** Completed steps are committed; the failing step's
   test/code is still uncommitted (the cycle bailed before its atomic green commit). Drop
   exactly that half-done work — `git reset --hard HEAD` — which leaves every completed
   step's commit (and the ledger's checked steps) intact.
2. **Classify deterministically.** `classification="$($S/classify-bail.sh <cause>)"`
   (`<cause>` is one of the tokens above). This keeps the label consistent rather than
   ad-hoc; an unknown token makes it exit non-zero — pick the right token.
3. **Push the branch** so completed steps and the leaf logs are recoverable:
   `git push -u origin tdd/<n>-<slug>` (best-effort; note if it fails).
4. Post a `### ⛔ Bailed — <phase> (<classification> failure)` comment that names the phase,
   carries the last reason (rejection reason or kill cause), and points at the progress log
   (`.tdd/<phase>.log` or `.tdd/revise-<phase>-*.log`) for forensics.
5. **Open no PR.** The ledger's completed steps stay checked, so a re-run resumes from the
   failing step (see *Resume*).
6. Report to the user: the phase, the **classification** (system vs process), the reason,
   and the branch name.

## Resume

The committed ledger makes a run **resumable**: re-running `/solve-issue <n>` picks up
where a previous run stopped (a bail, an interruption, or a human pause), without redoing
finished steps.

On re-run, after re-creating/switching to the branch (step 1), the **resume check** finds
an existing `.tdd/issue-<n>.md`. When it does:

1. Do **not** re-plan — the ledger is the source of truth. Re-write only the blind spec
   file (`.tdd/issue-<n>-spec.md`) since it is run scratch, not committed.
2. `next-unchecked.sh < .tdd/issue-<n>.md` gives the **first unchecked step** — the cycle
   loop continues from exactly there. Already-checked steps (and their commits) are kept.
3. Post a `### ▶️ Resuming` comment naming that step, then run the cycle loop (step 3) as
   normal. When `next-unchecked.sh` exits 3, every step is done → go to the draft PR.

Because each step was checked off **atomically with its green commit**, the ledger and the
git history agree on exactly what is done — so resume never repeats or skips a step.

## Detecting the test command

Pick the first that applies, and prefer running only what is fast and complete:

- `package.json` with a `test` script → `npm test` (or `pnpm`/`yarn` if their lockfile is
  present).
- `pytest.ini` / `pyproject.toml` / `tests/` with pytest available → `pytest -q`.
- A `Makefile` with a `test` target → `make test`.
- Python stdlib only → `python3 -m unittest discover -q`.

If you cannot confidently determine the test command, **ask the user** rather than
guessing. Pass it into every developer-leaf prompt so the leaves run the same suite.

## Guardrails

- **You write no code.** Developer leaves write the test, the implementation, and the
  refactor; you orchestrate. Red and green are always performed by leaves **distinct from
  the verifier**.
- **Every leaf is launched through `supervise.sh`** — never `run-leaf.sh` or `claude`
  directly. The supervisor is the one place stuck-detection lives.
- One failing test, then minimum code, then the refactor loop — in that order, per step.
  Never production code before its failing test.
- **A test that passes against unmodified code is never sent to verify-red**; it is either
  a blind-verified pin or a bail — never a Green.
- **The committed ledger is the source of truth.** Loop the cycle over its steps until none
  remain; check each step off **atomically with its green commit**; the issue thread only
  **mirrors** the ledger. Never hand-edit the ledger — use `tick-ledger.sh`.
- **Generality comes only from triangulation.** Overfit code is flagged for a triangulating
  test, never hand-generalized in a refactor.
- Every phase is **blind-verified** before you proceed, and **every verdict is mirrored**
  to the issue thread.
- The full suite must be green before you commit and before you open the PR.
- The PR is always a **draft**, always carries `Closes #<n>`, and is **never merged** by
  you.
- On a `REJECT`, run the **bounded revise loop** (default 2 attempts, fresh leaf carrying
  the reason); if it exhausts, **bail** (process failure). On a **killed-stuck** leaf past
  its retry budget, or an unreadable verdict, **bail** (system failure). Always preserve
  commits and classify the cause. Never hand-fix the code yourself or loop past the budget.
