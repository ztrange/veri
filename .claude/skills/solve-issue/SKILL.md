---
name: solve-issue
description: >-
  Drive one GitHub issue through a single Red → Green → Refactor TDD pass,
  narrating each phase as a comment on the issue thread, and leave the result on
  a draft PR. Invoke as `/solve-issue <number>`. Use when the user names one
  GitHub issue to solve under TDD discipline.
---

# solve-issue — the veri conductor (walking skeleton)

You are the **conductor**. You drive exactly one GitHub issue end-to-end through a
single Red → Green → Refactor pass, narrating your progress to the issue thread, and
leave the result on a **draft PR** for a human to review and merge.

This is the v0 walking skeleton. It is deliberately crude but **usable and observable**.
The following are **out of scope** for this slice and must NOT be attempted here — they
arrive in later slices: independent (blind) verification, the supervisor / `claude -p`
leaves, retries / revise loops, the multi-step plan loop, and the committed ledger. You
do the red/green/refactor work **inline yourself**; do not spawn subprocesses.

## Inputs

- `$ARGUMENTS` (or whatever the user passed) contains the issue **number** `<n>`.
  If no number was given, ask the user for one and stop until they answer.

## Procedure

Work through these steps in order. If a **preflight** step fails, stop and tell the
user what is wrong — do not start a cycle on a poisoned baseline. Once the cycle is
underway, keep going to a draft PR.

### 0. Preflight

Run these checks before touching anything:

1. **Git repo & clean tree.** `git rev-parse --is-inside-work-tree` succeeds and
   `git status --porcelain` is empty. If the tree is dirty, stop and ask the user to
   commit or stash first.
2. **`gh` authenticated.** `gh auth status` succeeds.
3. **Suite is green at baseline.** Determine the project's test command (see
   *Detecting the test command* below) and run it. If the suite is already red, stop
   and report it — a cycle must not start on a red baseline.
4. **Default branch.** Capture it for the PR base:
   `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.

### 1. Read the issue and branch

1. Read the issue:
   `gh issue view <n> --json number,title,body,url`.
2. Identify the **single acceptance criterion** from the body. This slice expects a
   single-criterion issue; if you see several independent criteria, pick the first /
   primary one and note in your start comment that you are solving that one.
3. Derive a slug from the title — lowercase, non-alphanumerics to `-`, collapse and trim
   `-`, cap to ~6 words. Create and switch to the per-issue branch:
   `git switch -c tdd/<n>-<slug>` (off the default branch). If the branch already
   exists, switch to it instead.

### 2. Start comment

Post a comment on the issue announcing that veri has started, naming the branch and the
criterion you are solving. Keep it short. Use:

```
gh issue comment <n> --body "..."
```

### 3. Red — one failing test

Write **exactly one** failing test that pins the acceptance criterion to observable
behavior. Rules:

- Test observable external behavior, not implementation internals.
- **No production code in this step.** The test must fail because the behavior does not
  exist yet — not because of an import typo or syntax error.
- Run the test and confirm it **fails for the right reason** (e.g. assertion failure or
  missing symbol that the implementation will introduce — not an unrelated error).

Then narrate Red: post an issue comment with the test you wrote and the failing output
(trimmed). Label it clearly, e.g. `### 🔴 Red`.

### 4. Green — minimum implementation

Write the **minimum** production code that makes the failing test pass. Do not add
generality, options, or cases the test does not demand. Then:

- Run the **full test suite** (not just the new test) and confirm it is **green** with no
  regressions.
- Narrate Green: post an issue comment with the implementation and the green suite output
  (trimmed). Label it `### 🟢 Green`.
- **Commit the green state** before refactoring, so there is a clean revert point:
  `git add -A && git commit -m "feat: <criterion summary> (#<n>)"`.

### 5. Refactor — one tidy-up pass

Make **one** behavior-preserving tidy-up pass over the code (and test) you just wrote:
naming, duplication, clarity. Do **not** change observable behavior and do **not** add
untested generality — generality comes only from triangulation, which is a later slice;
if you notice missing generality, mention it in the narration rather than hand-writing
it. Then:

- Run the full suite again and confirm it is **still green**. If a refactor breaks the
  suite, revert that change.
- If there is genuinely nothing to tidy, say so in the narration — an explicit "no
  refactor warranted" is a valid pass.
- Narrate Refactor: post an issue comment describing what you changed (or that nothing
  was warranted) and the green suite output. Label it `### 🛠️ Refactor`.
- Commit the refactor (only if something changed):
  `git add -A && git commit -m "refactor: <what> (#<n>)"`.

### 6. Draft PR

The full suite must be green and the work committed before this step.

1. Push the branch: `git push -u origin tdd/<n>-<slug>`.
2. Open a **draft** PR linked to the issue. The body must contain `Closes #<n>`:
   ```
   gh pr create --draft --base <default-branch> \
     --title "<type>: <criterion summary> (#<n>)" \
     --body "Closes #<n>

   <one-paragraph summary of the R→G→R pass>"
   ```
3. **Never merge the PR.** Landing the code is always the human's deliberate act.
4. Post a final issue comment with the PR URL, e.g.
   `### ✅ Done — <pr-url>`.

Report back to the user with the branch name and the PR URL.

## Detecting the test command

Pick the first that applies, and prefer running only what is fast and complete:

- `package.json` with a `test` script → `npm test` (or `pnpm`/`yarn` if their lockfile is
  present).
- `pytest.ini` / `pyproject.toml` / `tests/` with pytest available → `pytest -q`.
- A `Makefile` with a `test` target → `make test`.
- Python stdlib only → `python3 -m unittest discover -q`.

If you cannot confidently determine the test command, **ask the user** rather than
guessing.

## Guardrails

- One failing test, then minimum code, then one tidy-up pass — in that order. Do not
  write production code before its failing test.
- The full suite must be green before you commit, and before you open the PR.
- The PR is always a **draft**, always carries `Closes #<n>`, and is **never merged** by
  you.
- Every phase (start, red, green, refactor, done) is mirrored to the issue thread — the
  issue is the human-facing record of the run.
- If you get stuck, stop and report to the user; do not loop or retry (that machinery
  arrives in a later slice).
