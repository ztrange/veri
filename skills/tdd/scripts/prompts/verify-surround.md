{{SHARED}}

## Phase: verify-surround

This is a **legacy** run. A developer agent has written **characterization tests** at
`{{TEST_PATH}}` (the target test is `{{TARGET_TEST}}`) around one **region** of code no test
covered: black-box cases meant to drive the region only through its **seam**, a command or
callable outside it, and to pin what the unmodified code does now. Judge whether they do.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **Every case passes on the unmodified code.** Run the cases at `{{TEST_PATH}}` yourself,
   through the wrapper {{INCLUDE:_timed-test-run.md}}:

       {{TIMED_TEST_RUN}} target '{{TEST_PATH}}' <the command that runs that test file>

   {{INCLUDE:_exit-status-back.md}} so a failing run stays red. REJECT, naming the case,
   when one fails, errors or is skipped.
2. **Only test files change.** List what changed since the branch point: `git diff --name-only
   {{BRANCH_BASE}}` and the untracked files `git status --porcelain` prints. REJECT, naming the
   file, when the change touches any file other than test files and the run's own `.tdd/` files:
   a characterization test is written around code it leaves alone.
3. **Each case is black-box.** REJECT, naming the case, when it:
   - **reaches inside the region**: it imports, calls, patches or reads anything inside the
     region other than the seam the step names, or
   - **asserts on internals**: it asserts on a value an outside caller of the seam could not
     observe (a private attribute, a helper's return value, an intermediate variable) rather than
     on what the seam returns, prints, exits with or writes.
4. **Never reject a case for its cost or its reach.** A characterization test drives real code
   from outside, so do **not** reject a case for being slow, for starting a process, or for
   depending on fixtures outside its own file. These are what such a test is.

PASS only if all four hold. Leave the working tree exactly as you found it.

You may add mutants of the region you judge the cases should catch, as further lines of your
reason after the `REASON:` line: one `MUTANT: <file> | <old> | <new>` line each, a literal
replacement inside the region. Do not run them: a script, not you, runs every row, yours and the
developer's, against the cases.
