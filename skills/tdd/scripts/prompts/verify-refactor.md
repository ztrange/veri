{{SHARED}}

## Phase: verify-refactor

A developer agent has finished the **refactor** pass for this cycle (the code and test
around `{{TEST_PATH}}`). The refactor is meant to be **behavior-preserving** tidy-up.
The step's green commit, where the refactor started, is `{{BASE_SHA}}`.
Review what the refactor changed with `git diff {{BASE_SHA}}..HEAD`, and do not read the
range's commit messages: `git log` and `git show` on the range carry the author's rationale.
Render one verdict on the settled result.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **Still green.** Run the fast command, `{{FAST_CMD}}` (`detect-test-command.sh --tier fast`
   prints it), then run the suites `affected-suites.sh` prints for the files the refactor
   touched yourself; both must be **green**. A refactor that changed observable behavior or
   broke any test is a REJECT. Make each of those two runs through the wrapper
   `{{TIMED_TEST_RUN}}`, which records what the run cost and names the tier it belongs to:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   The wrapper hands the command's own exit status straight back, so a red run stays red.
2. **Up to standard.** The settled code should be code you would approve: it follows the
   repository's **conventions**, uses sensible **typing**/structure where the project
   does, names things clearly, and is reasonably **robust**. It must not have smuggled in
   untested generality — generality is only earned through triangulation, not hand-written
   here.
3. **A missing case is a flag, not a REJECT.** An obvious unhandled edge case the spec
   implies is not by itself a REJECT: handling it changes behavior, which a
   behavior-preserving refactor may not do, so the REJECT would demand what no revise leaf
   can give you — the answer to a missing case is a new test, not tidier code. Report the
   unhandled edge case on a `FLAGS:` line instead, written before the final
   `VERDICT:`/`REASON:` pair, carrying the class it falls into: `FLAGS: overfit | <the
   code> | <the case that would force the general implementation>` when the code passes the
   step's test without implementing what the step's criterion states, `FLAGS:
   uncovered-spec | <the behaviour> | <the criterion or spec line requiring it>` when the
   spec requires a behaviour no step covers, or `FLAGS: beyond-spec | <what it names>` for
   anything the spec does not ask for. One finding per line.
4. **No assertion loosened.** A removed or weakened test assertion in the range is a REJECT,
   and the REJECT names that assertion: the suite stays green while it loosens, so the diff
   is the only place it shows.
5. **Cosmetic hunks.** A hunk that is only cosmetic (whitespace, reflowed prose, a rename
   with no other effect) is named in REASON: but is not a REJECT by itself, since a REJECT
   costs a revise leaf.
6. **Empty range.** An empty range, which a reset of the leaf's commits leaves, is not a
   REJECT by itself: judge the settled result as it stands.
7. **Out of scope.** A shortfall against a criterion outside the step under judgement is
   named in REASON: as out of scope and is not by itself a REJECT: a behavior-preserving
   refactor may not add another step's work, so demanding it here is a demand no revise
   leaf can satisfy.
8. **The cycle's files.** The files this cycle touched are the ones
   `git diff --name-only {{BASE_SHA}}^ {{BASE_SHA}}` names, and the refactor was confined to
   them; derive that list yourself, and read it as paths and nothing else. A changed file
   outside that list is a REJECT, unless its hunk removes duplication between that file and
   code in the list — the one reason a transform was allowed to leave the list for.
9. **Only the two allowed comments.** A comment the range adds is allowed only as a
   contract header (a usage line or exit-code table) or a succinct warning where the shell
   itself is the hazard (bash 3.2, BSD versus GNU flags, `set -u`'s exit status, a
   load-bearing `|| true`). REJECT any other rationale comment the range adds, and name
   it in REASON:.
   A contract header or a shell-hazard warning is never grounds for REJECT.

PASS if the suite is green and the code is up to standard. REJECT, naming the specific
weakness, if the tidy-up left the code below standard or altered behavior.
