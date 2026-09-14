{{SHARED}}

## Phase: develop-refactor

Apply **one** behavior-preserving transformation to the code this cycle produced — or
report that nothing is left to tidy. The suites covering it stay green throughout.

### The step (this cycle's criterion)

{{STEP}}

### The files this cycle touched (the bounds of the tidy-up)

{{TOUCHED_FILES}}

Confine the transform to those files. Tidying code this cycle did not write is out of
scope, however tempting.

### The issue's behavior spec (context — the behaviour that must not change)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### The two classes of candidate

What class a candidate falls into is decided by what the transform **changes**, never by
which file it sits in:

- **structural** — removes duplication, in code or in prose, extracts or inlines, deletes
  dead code, renames an identifier that misleads, narrows a scope that leaks, or moves
  logic to where it belongs.
- **cosmetic** — rewords, re-cites, reflows or re-comments, without removing duplication
  and without changing an identifier or a structure.

### What to do

1. Pick **one** transformation that makes the code clearer and apply it — only a structural
   candidate qualifies, never a cosmetic one. Not a batch: one, so a break is attributable.
2. Run the suites covering the files you touched, not the full suite: they answer what one
   transform could plausibly break, and answer it in a fraction of the time. Those suites
   must stay green; revert the transform rather than leave a red suite behind. How this
   repository runs one suite is a convention like any other — establish it under **Read the
   conventions out of the repository** at the top of this prompt, from the files that are
   already there.
3. The full suite runs at verify-refactor, on the settled result. The trade is that a break
   in an untouched suite surfaces there, as a REJECT the revise loop answers, rather than
   at the transform that caused it.
4. **No untested generality.** Generality is earned by triangulation — another test
   demanding it — never hand-written here. Do not add options, flags, parameters or
   abstraction no existing test requires.
5. If the code is **overfit** — it hard-codes the one tested case rather than implementing
   the behaviour — do **not** generalize it yourself. Flag it as needing a triangulating
   test, and say which case would force the generality.
6. If no structural candidate is left under those rules, change nothing and report
   "nothing left to tidy" — even when cosmetic candidates remain, since none of them is
   worth a transform. That is a legitimate result, not a failure to find work.
7. Leave your transform **uncommitted** in the working tree — do not run `git commit`; the
   conductor commits, because the commit is its atomic tick-and-commit.

### Report (last lines of your output)

RESULT: <"applied <the transform>, suite green" | "nothing left to tidy">
FLAGS: <overfit code needing a triangulating test, and the case that would force it — or "none">
CANDIDATES: <"structural | <transform>" or "cosmetic | <transform>" — a transform you still see left in those files, carrying the class it falls into — one per line, each on its own CANDIDATES: line — or "none">
