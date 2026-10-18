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
   {{INCLUDE:_timed-test-run-tier.md}}:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   {{INCLUDE:_exit-status-back.md}} so a red run stays red.
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
   {{INCLUDE:_flag-overfit.md}}` when the code passes the
   step's test without implementing what the step's criterion states, `FLAGS:
   {{INCLUDE:_flag-uncovered-spec.md}}` when the
   spec requires a behaviour no step covers, or `FLAGS: {{INCLUDE:_flag-beyond-spec.md}}` for
   anything the spec does not ask for. One finding per line.
4. **No assertion loosened.** A removed or weakened test assertion in the range is a REJECT,
   and the REJECT names that assertion: the suite stays green while it loosens, so the diff
   is the only place it shows.
5. **Cosmetic hunks.** Whitespace, reflowed prose or a pure rename: list it in REASON:, and
   don't REJECT for it alone — a REJECT spends a revise leaf.
6. **Nothing changed.** When the range holds no commits (the leaf's commits were reset),
   that alone earns no REJECT; judge whatever is settled.
7. **Out of scope.** A shortfall against a criterion outside the step under judgement is
   named in REASON: as out of scope and is not by itself a REJECT: a behavior-preserving
   refactor may not add another step's work, so demanding it here is a demand no revise
   leaf can satisfy.
8. **The cycle's files.** The files this cycle touched are the ones
   `git diff --name-only {{BASE_SHA}}^ {{BASE_SHA}}` names, and the refactor was confined to
   them; derive that list yourself, and read it as paths and nothing else. A changed file
   outside that list is a REJECT, unless its hunk removes duplication between that file and
   code in the list — the one reason a transform was allowed to leave the list for.
9. {{INCLUDE:_verify-comments-lead.md}} range {{INCLUDE:_verify-comments-allowed.md}} range {{INCLUDE:_verify-comments-never-reject.md}}

PASS if the suite is green and the code is up to standard. REJECT, naming the specific
weakness, if the tidy-up left the code below standard or altered behavior.
