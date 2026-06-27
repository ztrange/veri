---
name: solve-issue
description: >-
  Drive one GitHub issue through a single Red → Green → Refactor TDD pass in which a
  blind, independent verifier confirms each phase, narrating every phase and verdict as a
  comment on the issue thread, and leave the result on a draft PR. Invoke as
  `/solve-issue <number>`. Use when the user names one GitHub issue to solve under TDD.
---

# solve-issue — the veri conductor (blind-verification slice)

You are the **conductor**. You drive exactly one GitHub issue end-to-end through a single
Red → Green → Refactor pass, but you **write no code yourself**. Each phase is performed
by a short-lived developer **leaf** (`claude -p` subprocess), and after each phase a
separate **blind independent verifier** leaf confirms the work. You orchestrate the
leaves, branch on their verdicts, narrate every phase and verdict to the issue thread,
and leave the result on a **draft PR** for a human to review and merge.

This slice adds blind verification on top of the v0 walking skeleton. The following are
still **out of scope** and must NOT be attempted here — they arrive in later slices: the
**supervisor** (heartbeat + hard timeout around each leaf — #4), **retries / the bounded
revise loop** on a `REJECT` (#5), the **multi-step plan loop** and the **committed
ledger** (#6). For now a `REJECT` simply **stops the run cleanly** — veri stays usable; it
just refuses to proceed on an unverified step.

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

- `$S/run-leaf.sh <name> <prompt-file|-> [claude args...]` — launch one leaf, teeing its
  output to `.tdd/<name>.log` for inspection. (`-` reads the prompt from stdin.)
- `$S/build-verify-prompt.sh <red|green|refactor> <spec-file> <test-path> [target]` —
  assemble the blind verifier prompt. Used by `verify.sh`; you rarely call it directly.
- `$S/verify.sh <red|green|refactor> <spec-file> <test-path> [target]` — the **verify
  verb**: build the blind prompt → launch the verifier leaf → parse the verdict. Prints
  the verifier's **reason** on stdout; **exit 0 = PASS, 1 = REJECT, 2 = malformed**.
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
   file/name. Write it to `.tdd/develop-red.prompt`, then launch the leaf:
   ```
   $S/run-leaf.sh develop-red .tdd/develop-red.prompt --permission-mode bypassPermissions
   ```
   The leaf writes the test to disk. Note the **test path** and **target test id** it used.
2. **Verify (blind).** Run the verifier against the on-disk test and spec:
   ```
   $S/verify.sh red .tdd/issue-<n>-spec.md <test-path> <target-test-id>
   ```
   Capture its **stdout (the reason)** and its **exit code**.
3. **Narrate + branch.** Post a `### 🔴 Red` comment with the test and the failing output,
   followed by a `### 🔎 verify-red — PASS|REJECT` comment carrying the verifier's reason.
   - **PASS (exit 0):** continue to Green.
   - **REJECT (exit 1) or malformed (exit 2):** **stop** — see *Stopping on a REJECT*.

### 4. Green — minimum implementation (developer leaf), then verify-green (blind)

1. **Develop.** Compose a developer-leaf prompt to write the **minimum** production code
   that makes the failing test pass — no generality, options, or cases the test does not
   demand — and to run the **full suite** and confirm green. Include the spec, the test
   command, and the target test. Write to `.tdd/develop-green.prompt` and launch:
   ```
   $S/run-leaf.sh develop-green .tdd/develop-green.prompt --permission-mode bypassPermissions
   ```
2. **Verify (blind).** `$S/verify.sh green .tdd/issue-<n>-spec.md <test-path> <target-test-id>`.
3. **Narrate + branch.** Post `### 🟢 Green` (implementation + green suite output) and
   `### 🔎 verify-green — PASS|REJECT` (the reason).
   - **PASS:** **commit the green state** before refactoring:
     `git add -A && git commit -m "feat: <criterion summary> (#<n>)"`. Continue to Refactor.
   - **REJECT / malformed:** **stop** — see *Stopping on a REJECT*.

### 5. Refactor — one tidy-up pass (developer leaf), then verify-refactor (blind, once)

1. **Develop.** Compose a developer-leaf prompt for **one behavior-preserving** tidy-up
   pass over the code and test just written (naming, duplication, clarity) — no change to
   observable behavior, no untested generality (generality comes only from triangulation,
   a later slice; if generality is missing, the leaf should *note* it, not hand-write it).
   The leaf must run the full suite and keep it green, reverting any change that breaks it.
   If nothing is worth tidying, the leaf should say so. Write to `.tdd/develop-refactor.prompt`
   and launch as above (`develop-refactor`).
2. **Verify (blind, once).** `$S/verify.sh refactor .tdd/issue-<n>-spec.md <test-path>` —
   one verdict on the settled result (suite still green, code up to standard).
3. **Narrate + branch.** Post `### 🛠️ Refactor` (what changed, or "no refactor warranted",
   + green suite output) and `### 🔎 verify-refactor — PASS|REJECT` (the reason).
   - **PASS:** commit the refactor **only if something changed**:
     `git add -A && git commit -m "refactor: <what> (#<n>)"`. Continue to step 6.
   - **REJECT / malformed:** **stop** — see *Stopping on a REJECT*. (The green commit
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

## Stopping on a REJECT

When `verify.sh` exits non-zero (`1` REJECT, `2` malformed), the run stops here — there is
no revise loop yet (that is #5). Stop **cleanly**:

1. Post a `### 🛑 Stopped — verify-<phase> REJECT` comment on the issue carrying the
   verifier's **reason** verbatim, so the next human (or the future revise loop) knows
   exactly what failed and why.
2. Leave any already-made commits in place (e.g. a green commit before a refactor REJECT);
   do **not** open a PR, and do **not** tick the criterion.
3. Report to the user: the phase that was rejected, the reason, and the branch name.

A `REJECT` is veri working as designed — the blind verifier refusing to rubber-stamp
unverified work — not an error to retry your way around.

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
- One failing test, then minimum code, then one tidy-up pass — in that order. Never
  production code before its failing test.
- Every phase is **blind-verified** before you proceed, and **every verdict is mirrored**
  to the issue thread.
- The full suite must be green before you commit and before you open the PR.
- The PR is always a **draft**, always carries `Closes #<n>`, and is **never merged** by
  you.
- On a `REJECT`, stop cleanly and report; do not loop, retry, or hand-fix (that machinery
  is #4/#5).
