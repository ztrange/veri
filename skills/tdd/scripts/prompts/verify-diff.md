{{SHARED}}

## Phase: verify-diff

The step under judgement is a criterion about this branch's own diff: something removed,
left unchanged, or confined to named lines. No test is its deliverable. The run branched
at `{{BASE_SHA}}`. Judge the step's criterion against `git diff {{BASE_SHA}}..HEAD` alone,
and do not read the range's commit messages: `git log` and `git show` on the range carry
the author's rationale.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

Run the fast command, `{{FAST_CMD}}`, then the suites `affected-suites.sh` prints for the
files the diff touched, each through the wrapper `{{TIMED_TEST_RUN}}`, which records what the run cost and names the tier it belongs to:

{{INCLUDE:_timed-test-run-fast-affected.md}}

The wrapper hands the command's own exit status straight back, so a red run stays red.

PASS if the diff satisfies the step's criterion. REJECT, naming where the diff falls short,
otherwise. REJECT, too, if the fast command or the affected suites are red. REJECT, too,
if the step's own commits add a test — those in
`git diff {{STEP_BASE_SHA}}..HEAD`, never a test an earlier step of the run added: a criterion
judged against the diff is never also pinned by a case left behind. End with `VERDICT: PASS` or `VERDICT: REJECT`.
