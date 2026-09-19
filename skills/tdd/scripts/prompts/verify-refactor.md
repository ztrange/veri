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
   broke any test is a REJECT.
2. **Up to standard.** The settled code should be code you would approve: it follows the
   repository's **conventions**, uses sensible **typing**/structure where the project
   does, names things clearly, and is reasonably **robust** (no obvious unhandled edge
   case the spec implies). It must not have smuggled in untested generality — generality
   is only earned through triangulation, not hand-written here.
3. **No assertion loosened.** A removed or weakened test assertion in the range is a REJECT,
   and the REJECT names that assertion: the suite stays green while it loosens, so the diff
   is the only place it shows.
4. **Cosmetic hunks.** A hunk that is only cosmetic (whitespace, reflowed prose, a rename
   with no other effect) is named in REASON: but is not a REJECT by itself, since a REJECT
   costs a revise leaf.
5. **Empty range.** An empty range, which a reset of the leaf's commits leaves, is not a
   REJECT by itself: judge the settled result as it stands.
6. **Out of scope.** A shortfall against a criterion outside the step under judgement is
   named in REASON: as out of scope and is not by itself a REJECT: a behavior-preserving
   refactor may not add another step's work, so demanding it here is a demand no revise
   leaf can satisfy.

PASS if the suite is green and the code is up to standard. REJECT, naming the specific
weakness, if the tidy-up left the code below standard or altered behavior.
