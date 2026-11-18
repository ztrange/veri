{{SHARED}}

## Phase: verify-break

This is a **legacy** run. The step's region is code no test covers, and its seam did not reach it,
so a developer agent has applied one dependency-breaking edit to make the region reachable and
committed it. The step started at `{{BASE_SHA}}`. Review what the step changed with
`git diff {{BASE_SHA}}..HEAD` — the whole range, not a subset of files — and do not read the
range's commit messages: `git log` and `git show` on the range carry the author's rationale.
Render one verdict on the settled result.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### The catalogue

The range may apply exactly one of these edits, and nothing else:

- **`sprout`**: the region's code moved, unchanged, into a new function or class that the old code
  now calls and a test can call directly.
- **`extract and override`**: one dependency call the region makes extracted into a method a test
  may override.

### Your checks

1. **Exactly one catalogued edit.** The range is one `sprout` or one `extract and override` of the
   step's region, and nothing else: no second edit, no other refactoring, no new test and no
   edit to a test file. A range that is not exactly one catalogued edit is a REJECT, naming what
   is not.
2. **No behaviour change at the callers.** Every existing caller of the region sees what it saw
   at `{{BASE_SHA}}`: the same signatures, arguments, return values, output, errors and side
   effects. Code moved by a `sprout` is moved unchanged. A range that changes any behaviour
   observable at the region's existing callers is a REJECT, naming the caller and the change.
3. **Still green.** Run the fast command, `{{FAST_CMD}}`, then the test files covering
   the files the range touched, as `affected-suites.sh` prints them, each through the wrapper
   {{INCLUDE:_timed-test-run-tier.md}}:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   {{INCLUDE:_exit-status-back.md}} so a red run stays red. Either run red is a REJECT.

PASS if the range is exactly one catalogued edit, it changes no behaviour observable at the
region's existing callers, and both runs are green.
REJECT, naming the specific problem, otherwise.
