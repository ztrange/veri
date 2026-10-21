{{SHARED}}

## Phase: verify-transform

This is a **refactor** run. A developer agent has applied one named refactoring for this
step and committed it. The step's predicate record, the shell command stating the smell,
is `{{TEST_PATH}}`: false before the step, true after. The step started at `{{BASE_SHA}}`.
Review what the step changed with `git diff {{BASE_SHA}}..HEAD` — the whole range, not a
subset of files — and do not read the range's commit messages: `git log` and `git show` on
the range carry the author's rationale. Render one verdict on the settled result.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **The predicate holds.** Run the command in `{{TEST_PATH}}` yourself; it must succeed.
2. **Behaviour unchanged.** Run the suites covering the files the range touched, through
   the wrapper `{{TIMED_TEST_RUN}}`; they must be **green**:

       {{INCLUDE:_timed-test-run-affected.md}}

3. **One refactoring.** The range applies the refactoring the step names and nothing else.

4. **No observable change.** A range that changes observable behaviour is a REJECT.

PASS if the predicate holds, the suites are green, the range is that one refactoring and it
changes no observable behaviour.
REJECT, naming the specific problem, otherwise.
