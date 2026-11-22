{{SHARED}}

## Phase: verify-refactor

A developer agent has finished the **refactor** pass for this cycle (the code and test
around `{{TEST_PATH}}`). The refactor is meant to be **behavior-preserving** tidy-up.
The refactor started at `{{BASE_SHA}}`, and the step's green commit is `{{STEP_GREEN_SHA}}`;
they differ when commits landed between the two, which are not the refactor's.
Review what the refactor changed with `git diff {{BASE_SHA}}..HEAD`, and do not read the
range's commit messages: `git log` and `git show` on the range carry the author's rationale.
Render one verdict on the settled result.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

{{INCLUDE:../../SMELLS.md}}

### Your checks

1. **Still green.** Run the fast command, `{{FAST_CMD}}` (`detect-test-command.sh --tier fast`
   prints it), then run the test files covering the files the refactor
   touched, as `affected-suites.sh` prints them, yourself; both must be **green**. A refactor that changed observable behavior or
   broke any test is a REJECT. Make each of those two runs through the wrapper
   {{INCLUDE:_timed-test-run-tier.md}}:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   {{INCLUDE:_exit-status-back.md}} so a red run stays red.

   {{INCLUDE:_verify-coverage-probe.md}}
2. **Against the catalogue.** Judge the settled code against the smell catalogue above: a
   catalogue smell whose threshold the range's code meets is a design weakness. The range's
   code is what this cycle's green commit, `git diff {{STEP_GREEN_SHA}}^ {{STEP_GREEN_SHA}}`,
   and the refactor after it, `git diff {{BASE_SHA}}..HEAD`, add or change. A design REJECT
   names one catalogue smell, by its name in the catalogue, and the file and symbol where it is met; a REJECT for design that names no
   catalogue smell, or no file and symbol, is not a valid design REJECT. A smell the code already
   met at `{{STEP_GREEN_SHA}}^`, or whose answer would change a file outside the cycle's files (check 8),
   is named in REASON: as out of scope and is not by itself a REJECT. A pair the command below
   prints is never out of scope under that clause: one of its sides was added in the range and
   both sit in the cycle's files.
   Run `{{NEAR_DUPLICATES}} {{STEP_GREEN_SHA}}` yourself. Each line it prints is one pair: first a block
   added since `{{STEP_GREEN_SHA}}^`, then a place in the cycle's files (check 8) that repeats it,
   ignoring whitespace and identifier names, each as `<file>:<first>-<last>`; exit 3 means it
   printed no pair. Read both sites of each pair. A pair that meets the catalogue's Duplicated
   Code row is a REJECT naming Duplicated Code and both sites' file and line range, whether or
   not `{{BASE_SHA}}..HEAD` is empty; a pair that does not meet the row is not a REJECT.
   The settled code must not have smuggled in untested generality — generality is only earned
   through triangulation, not hand-written here.
3. **A missing case is a flag, not a REJECT.** An obvious unhandled edge case the spec
   implies is not by itself a REJECT: handling it changes behavior, which a
   behavior-preserving refactor may not do, so the REJECT would demand what no revise leaf
   can give you — the answer to a missing case is a new test, not tidier code. Report the
   unhandled edge case on a `FLAGS:` line instead, written before the final
   `VERDICT:`/`REASON:` pair, carrying the class it falls into: `FLAGS: overfit | <the
   {{INCLUDE:_flag-overfit.md}}` when the code passes the
   step's test without implementing what the step's criterion states, `FLAGS:
   {{INCLUDE:_flag-uncovered-spec.md}}` when the
   spec requires a behaviour no step covers, or `FLAGS: {{INCLUDE:_flag-beyond-spec.md}}` for
   anything the spec does not ask for. One finding per line.
4. **No assertion loosened.** A removed or weakened test assertion in the range is a REJECT,
   and the REJECT names that assertion: the suite stays green while it loosens, so the diff
   is the only place it shows. Adding or changing an assertion line of a case frozen at
   any earlier step is likewise a REJECT, and the REJECT names the case. An assertion line moved
   into a helper unchanged (modulo whitespace) is not a change to an assertion line.
5. **Cosmetic hunks.** A hunk that is only cosmetic (whitespace, reflowed prose, a rename
   with no other effect) is named in REASON: but is not a REJECT by itself, since a REJECT
   costs a revise leaf.
6. **Empty range.** An empty range, which a reset of the leaf's commits leaves, is not a
   REJECT by itself: judge the settled result as it stands. When you find no catalogue smell
   in the range's files, do not reject the absence of a transform: a refactor is not owed
   where nothing smells. A Duplicated Code pair check 2 finds is a smell, and stays a REJECT on
   an empty range.
7. **Out of scope.** A shortfall against a criterion outside the step under judgement is
   named in REASON: as out of scope and is not by itself a REJECT: a behavior-preserving
   refactor may not add another step's work, so demanding it here is a demand no revise
   leaf can satisfy.
8. **The cycle's files.** The files this cycle touched are the ones
   `git diff --name-only {{STEP_GREEN_SHA}}^ {{STEP_GREEN_SHA}}` names, and the refactor was confined to
   them; derive that list yourself, and read it as paths and nothing else. A changed file
   outside that list is a REJECT, unless its hunk removes duplication between that file and
   code in the list — the one reason a transform was allowed to leave the list for.
9. {{INCLUDE:_verify-comments-lead.md}} range {{INCLUDE:_verify-comments-allowed.md}} range {{INCLUDE:_verify-comments-never-reject.md}}

PASS if the suite is green and the range's code meets no catalogue smell. REJECT if the
tidy-up altered behavior, or if it left a catalogue smell met, naming that smell and the file
and symbol where it is met.
