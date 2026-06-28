---
name: solve-issue
description: >-
  Drive one GitHub issue through a single Red → Green → Refactor TDD pass in which a
  blind, independent verifier confirms each phase, narrating every phase and verdict as a
  comment on the issue thread, and leave the result on a draft PR. Invoke as
  `/solve-issue <number>`. Use when the user names one GitHub issue to solve under TDD.
---

# solve-issue — the veri conductor (retries slice)

You are the **conductor**. You drive exactly one GitHub issue end-to-end through a single
Red → Green → Refactor pass, but you **write no code yourself**. Each phase is performed
by a short-lived developer **leaf** (`claude -p` subprocess), and after each phase a
separate **blind independent verifier** leaf confirms the work. Every leaf — developer or
verifier — is launched **through the supervisor** (`supervise.sh`), never directly, so a
hung or runaway leaf is killed instead of stalling the whole run. You orchestrate the
leaves, branch on their verdicts, narrate every phase and verdict to the issue thread,
and leave the result on a **draft PR** for a human to review and merge.

This slice makes veri **self-correcting** by adding the two retry axes, on top of the
supervised-leaves slice:

- **Revise loop (verdict axis):** a `REJECT` no longer stops the run — the conductor spawns
  a **fresh** developer leaf carrying the rejection reason and re-verifies, up to a bounded
  **attempt budget** (default 2), then bails the step.
- **Stuck-retry (liveness axis):** the supervisor relaunches a killed-stuck leaf up to its
  own budget (`VERI_STUCK_RETRIES`, default 1) before reporting killed-stuck.

These two budgets are **independent**: one handles a leaf that finished with a bad verdict,
the other a leaf that never produced one. Still **out of scope** (later slices): the
**multi-step plan loop** and the **committed ledger** (#6). A step that exhausts its revise
budget, or a leaf that stays killed-stuck past the supervisor's budget, **bails** —
preserving progress and classifying the cause (process vs system).

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

Let `S=.claude/skills/solve-issue/scripts`. All leaf machinery lives there and is unit-
tested (`$S/tests/*.test.sh`):

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
- `$S/build-verify-prompt.sh <red|green|refactor> <spec-file> <test-path> [target]` —
  assemble the blind verifier prompt. Used by `verify.sh`; you rarely call it directly.
- `$S/verify.sh <red|green|refactor> <spec-file> <test-path> [target]` — the **verify
  verb**: build the blind prompt → launch the verifier leaf **through the supervisor** →
  parse the verdict. Prints the verifier's **reason** on stdout; **exit 0 = PASS, 1 =
  REJECT, 2 = malformed or killed-stuck**.
- `$S/parse-verdict.sh` — extracts `PASS|REJECT` + reason from a leaf's output (used by
  `verify.sh`).
- `$S/tick-issue-criterion.sh <n> '<substring>'` — tick a criterion checkbox in the
  issue body.

## Inputs

- `$ARGUMENTS` contains the issue **number** `<n>`. If no number was given, ask the user
  for one and stop until they answer.

## Procedure

Work through these steps in order. If a **preflight** step fails, stop and tell the user
what is wrong — do not start a cycle on a poisoned baseline. Once the cycle is underway,
drive it to a draft PR or to a clean stop on a `REJECT`.

### 0. Preflight

1. **Git repo & clean tree.** `git rev-parse --is-inside-work-tree` succeeds and
   `git status --porcelain` is empty. If dirty, stop and ask the user to commit or stash.
2. **`gh` authenticated.** `gh auth status` succeeds.
3. **Suite is green at baseline.** Determine the test command (see *Detecting the test
   command*) and run it. If already red, stop and report — a cycle must not start on a
   red baseline.
4. **Default branch.** Capture it for the PR base:
   `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.

### 1. Read the issue, capture the spec, and branch

1. Read the issue: `gh issue view <n> --json number,title,body,url`.
2. Identify the **single acceptance criterion** from the body. This slice expects a
   single-criterion issue; if you see several independent criteria, pick the first /
   primary one and note in your start comment that you are solving that one.
3. **Write the behavior spec to a file** the verifier leaves will read:
   `mkdir -p .tdd && gh issue view <n> --json body -q .body > .tdd/issue-<n>-spec.md`.
   (The verifier is blind; this on-disk spec — never your narration — is what it sees.)
4. Derive a slug from the title — lowercase, non-alphanumerics to `-`, collapse and trim
   `-`, cap to ~6 words. Create and switch to the per-issue branch:
   `git switch -c tdd/<n>-<slug>` (off the default branch). If it already exists, switch.

### 2. Start comment

Post a short comment on the issue announcing veri has started, naming the branch and the
criterion you are solving, and noting that each phase will be blind-verified:
`gh issue comment <n> --body "..."`.

### 3. Red — one failing test (developer leaf), then verify-red (blind)

1. **Develop.** Compose a developer-leaf prompt that instructs it to write **exactly one**
   failing test pinning the criterion to **observable external behavior** (not internals),
   with **no production code**, and to run it and confirm it fails for the right reason.
   Include in the prompt: the issue's behavior spec, the test command, and the target test
   file/name. Write it to `.tdd/develop-red.prompt`, then launch the leaf **through the
   supervisor**:
   ```
   $S/supervise.sh develop-red $S/run-leaf.sh .tdd/develop-red.prompt --permission-mode bypassPermissions
   ```
   If `supervise.sh` exits **2 (killed-stuck)**, the leaf hung or ran away — **bail**
   cleanly (see *Bailing on a killed-stuck leaf*); do not retry. Otherwise the leaf wrote
   the test to disk — note the **test path** and **target test id** it used.
2. **Verify (blind).** Run the verifier against the on-disk test and spec:
   ```
   $S/verify.sh red .tdd/issue-<n>-spec.md <test-path> <target-test-id>
   ```
   Capture its **stdout (the reason)** and its **exit code**.
3. **Narrate + branch.** Post a `### 🔴 Red` comment with the test and the failing output,
   followed by a `### 🔎 verify-red — PASS|REJECT` comment carrying the verifier's reason.
   - **PASS (exit 0):** continue to Green.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. It
     returns either PASS (continue to Green) or budget-exhausted (**bail**, process failure).
   - **Malformed / killed-stuck (exit 2):** the verdict could not be obtained (unparseable
     or the verifier leaf was killed) — **bail** as a system failure (see *Bailing*), not a
     clean process stop.

### 4. Green — minimum implementation (developer leaf), then verify-green (blind)

1. **Develop.** Compose a developer-leaf prompt to write the **minimum** production code
   that makes the failing test pass — no generality, options, or cases the test does not
   demand — and to run the **full suite** and confirm green. Include the spec, the test
   command, and the target test. Write to `.tdd/develop-green.prompt` and launch **through
   the supervisor** (exit **2** → **bail**, see *Bailing on a killed-stuck leaf*):
   ```
   $S/supervise.sh develop-green $S/run-leaf.sh .tdd/develop-green.prompt --permission-mode bypassPermissions
   ```
2. **Verify (blind).** `$S/verify.sh green .tdd/issue-<n>-spec.md <test-path> <target-test-id>`.
3. **Narrate + branch.** Post `### 🟢 Green` (implementation + green suite output) and
   `### 🔎 verify-green — PASS|REJECT` (the reason).
   - **PASS:** **commit the green state** before refactoring:
     `git add -A && git commit -m "feat: <criterion summary> (#<n>)"`. Continue to Refactor.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. On a
     recovered PASS, commit the green state and continue; on budget-exhausted, **bail**.
   - **Malformed / killed-stuck (exit 2):** **bail** — see *Bailing*.

### 5. Refactor — one tidy-up pass (developer leaf), then verify-refactor (blind, once)

1. **Develop.** Compose a developer-leaf prompt for **one behavior-preserving** tidy-up
   pass over the code and test just written (naming, duplication, clarity) — no change to
   observable behavior, no untested generality (generality comes only from triangulation,
   a later slice; if generality is missing, the leaf should *note* it, not hand-write it).
   The leaf must run the full suite and keep it green, reverting any change that breaks it.
   If nothing is worth tidying, the leaf should say so. Write to `.tdd/develop-refactor.prompt`
   and launch **through the supervisor** as above (exit **2** → **bail**):
   ```
   $S/supervise.sh develop-refactor $S/run-leaf.sh .tdd/develop-refactor.prompt --permission-mode bypassPermissions
   ```
2. **Verify (blind, once).** `$S/verify.sh refactor .tdd/issue-<n>-spec.md <test-path>` —
   one verdict on the settled result (suite still green, code up to standard).
3. **Narrate + branch.** Post `### 🛠️ Refactor` (what changed, or "no refactor warranted",
   + green suite output) and `### 🔎 verify-refactor — PASS|REJECT` (the reason).
   - **PASS:** commit the refactor **only if something changed**:
     `git add -A && git commit -m "refactor: <what> (#<n>)"`. Continue to step 6.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. On a
     recovered PASS, commit and continue; on budget-exhausted, **bail**. (The green commit
     from step 4 is preserved either way.)
   - **Malformed / killed-stuck (exit 2):** **bail** — see *Bailing*. (The green commit
     from step 4 is preserved.)

### 6. Check off the criterion

The cycle is complete and verified. Tick its checkbox in the issue body so progress-
against-spec is visible. Use the helper — do **not** hand-edit with `sed`:
```
$S/tick-issue-criterion.sh <n> '<distinctive substring of the criterion>'
```
It flips the first unchecked `- [ ]` containing that substring to `- [x]` and exits non-
zero if nothing matched — if it does, re-check the substring rather than editing by hand.

### 7. Draft PR

The full suite must be green and the work committed before this step.

1. Push the branch: `git push -u origin tdd/<n>-<slug>`.
2. Open a **draft** PR linked to the issue; the body must contain `Closes #<n>`:
   ```
   gh pr create --draft --base <default-branch> \
     --title "<type>: <criterion summary> (#<n>)" \
     --body "Closes #<n>

   <one-paragraph summary of the blind-verified R→G→R pass>"
   ```
3. **Never merge the PR.** Landing the code is always the human's deliberate act.
4. Post a final `### ✅ Done — <pr-url>` comment.

Report back to the user with the branch name and the PR URL.

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

A **bail** terminally stops this issue while preserving progress (ADR-0011). Two causes
reach it, and the bail comment must **classify which**:

- **System failure (plumbing broke).** `supervise.sh` exits **2 (killed-stuck)** for a
  developer leaf even after its stuck-retry budget, or `verify.sh` exits **2** (no readable
  verdict — unparseable, or the verifier leaf killed).
- **Process failure (methodology spoke).** A step exhausted its `REVISE_BUDGET` and the
  blind verifier still says `REJECT`.

To bail:

1. **Preserve completed commits.** Do not revert; any green commit already made stays.
2. **Push the branch** so the partial work and the leaf logs are recoverable:
   `git push -u origin tdd/<n>-<slug>` (best-effort; note if it fails).
3. Post a `### ⛔ Bailed — <phase> (<system|process> failure)` comment that **classifies the
   cause**, names the phase, carries the last reason (rejection reason or kill cause), and
   points at the progress log (`.tdd/<phase>.log` or `.tdd/revise-<phase>-*.log`) for
   forensics.
4. **Open no PR** and do **not** tick the criterion.
5. Report to the user: the phase, the **classification** (system vs process), the reason,
   and the branch name.

Re-running later resumes from where the commits left off (full resume is #6).

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
- One failing test, then minimum code, then one tidy-up pass — in that order. Never
  production code before its failing test.
- Every phase is **blind-verified** before you proceed, and **every verdict is mirrored**
  to the issue thread.
- The full suite must be green before you commit and before you open the PR.
- The PR is always a **draft**, always carries `Closes #<n>`, and is **never merged** by
  you.
- On a `REJECT`, run the **bounded revise loop** (default 2 attempts, fresh leaf carrying
  the reason); if it exhausts, **bail** (process failure). On a **killed-stuck** leaf past
  its retry budget, or an unreadable verdict, **bail** (system failure). Always preserve
  commits and classify the cause. Never hand-fix the code yourself or loop past the budget.
