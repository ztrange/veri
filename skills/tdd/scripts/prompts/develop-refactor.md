{{SHARED}}

## Phase: develop-refactor

Apply behavior-preserving transformations to the code this cycle produced — or report that
nothing is left to tidy. The suites covering it stay green throughout.

### The step (this cycle's criterion)

{{STEP}}

### The files this cycle touched (the bounds of the tidy-up)

{{TOUCHED_FILES}}

Confine the transform to those files, with one exception: a transform may touch a file
outside that list only when it removes duplication between that file and code this cycle
wrote. Tidying code this cycle did not write is otherwise out of scope, however tempting.

### The issue's behavior spec (context — the behaviour that must not change)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### The four classes of candidate

What class a candidate falls into is decided by what the transform **changes**, never by
which file it sits in:

- **structural** — removes duplication, in code or in prose, extracts or inlines, deletes
  dead code, renames an identifier that misleads, narrows a scope that leaks, or moves
  logic to where it belongs.
- **cosmetic** — rewords, re-cites, reflows or re-comments, without removing duplication
  and without changing an identifier or a structure.
- **test-only** — any transform that would change only files under a `tests/` directory.
  Report it on a `CANDIDATES: test-only | <transform>` line, never on a `CANDIDATES: structural` one.
- **out-of-scope** — a structural transform outside the issue's bounds or ruled out by its spec.
  Report it on a `CANDIDATES: out-of-scope | <transform>` line instead of a `CANDIDATES: structural` one.

### The three classes of flag

A flag is something you found and must not fix here. Which class it falls into is decided
by what it names, and the class rides on the `FLAGS:` line so the conductor routes it from
your words rather than its own judgement:

- **overfit** — the code passes this step's test without implementing the behaviour the
  step's criterion states: it hard-codes the one tested case
- **uncovered-spec** — a behaviour the spec requires that no step of the plan covers
- **beyond-spec** — an input class or edge the spec does not ask for at all

### What to do

1. Triage the candidates you see in those files into the four classes above, then apply the
   structural ones, most valuable first, up to the budget of {{REFACTOR_BUDGET}} transforms
   you are given. Only a structural candidate qualifies for a transform, never a cosmetic
   one. Of those, apply only duplication removal against code this cycle wrote; apply no
   other structural transform here — extract a module, move behaviour, rename across files.
   Report every other structural candidate you see on its own `CANDIDATES: structural` line
   rather than apply it.
2. Commit each transform on its own, as `refactor: <what changed> (#<issue>)`, never a
   batch, so a break stays attributable to one change. That attribution is the whole of
   what a leaf per transform used to buy, and it is what has to survive several transforms
   sharing this one.
3. Run the suites `affected-suites.sh` prints for the files `refactor-touched.sh` printed —
   the ones listed above — after each transform, not the full suite: they answer what one transform could plausibly break, and answer it in a fraction of the
   time. Those suites must stay green; revert a transform that turns them red rather than
   leave a red suite behind, and carry on with the next candidate. Run one suite through
   `run-suite.sh <suite>` — the one invocation for a single suite, so that every leaf on this
   step runs it the same way and none of them is handed a suite that died partway and still
   exited 0. If that runner cannot run a suite in this repository, fall back to the test
   command above and say so in your report.
   Make each of those runs through the wrapper `{{TIMED_TEST_RUN}}`, which records what the
   run cost and names the tier it belongs to:

       {{TIMED_TEST_RUN}} affected '<the suites affected-suites.sh printed>' <the command that runs them>

   The wrapper hands the command's own exit status straight back, so a suite a transform
   turned red still reads as red. When a transform reached the one file outside that list
   the exception above allows, its suites run too: the suites follow every file the
   transform touched, so the one suite that could catch the break it did cause is never the
   one it skipped.
4. The full suite runs once per PR, before it is readied. The trade is that a break outside
   the affected set surfaces at that one full run, as the repair step a red result appends,
   rather than at the transform that caused it.
5. **No untested generality.** Generality is earned by triangulation — another test
   demanding it — never hand-written here. Do not add options, flags, parameters or
   abstraction no existing test requires.
6. Do **not** generalize overfit code yourself, and do not build anything the three
   classes above name. Report each finding as a `FLAGS:` line carrying its class, so the
   conductor can tell a triangulation this step owes from a step the plan is missing from
   a follow-up nobody is building in this run.
7. If no structural candidate is left under those rules, change nothing and report
   "nothing left to tidy" — even when cosmetic candidates remain, since none of them is
   worth a transform. That is a legitimate result, not a failure to find work.

### Report (last lines of your output)

RESULT: <"applied <the transform>, suites green" — one line per transform you applied, each on its own RESULT: line, in the order you applied them — or "nothing left to tidy" if you applied none>
CANDIDATES: <"structural | <transform>", "cosmetic | <transform>", "test-only | <transform>" or "out-of-scope | <transform>" — a transform you still see left in those files, carrying the class it falls into — one per line, each on its own CANDIDATES: line — or "none">
FLAGS: <"overfit | <the code> | <the case that would force the general implementation>", "uncovered-spec | <the behaviour> | <the criterion or spec line requiring it>" or "beyond-spec | <what it names>" — one finding per line, each on its own FLAGS: line, carrying the class it falls into — or "none">
