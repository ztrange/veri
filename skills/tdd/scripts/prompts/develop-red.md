{{SHARED}}

## Phase: develop-red

Add exactly **ONE** new failing test case, and write **NO** production code.

### The step to pin (this cycle's criterion — pin ONLY this)

{{STEP}}

Pin it as *observable behaviour*: what the code does when it is called, not how it is
written inside. One criterion, one case — no extra cases, and no generality the step does
not ask for.

### The issue's behavior spec (context only — pin only the step above)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Read the existing suite the case belongs in and add it in that suite's own style,
   leaving its other cases untouched and green. If no suite fits, create one that matches
   the repository's testing idiom.
2. Run it against the **unmodified** production code and record whether the new case FAILS
   or PASSES. Run the suite that holds the new case, not the full suite: the only question
   this phase asks is whether that one case fails, and rule 1 above covers how this
   repository runs a single suite — establish it by reading the files that are already
   there. If the repository has no way to run one suite on its own, fall back to the test
   command above and say so in your report. **Either answer is acceptable, and must be
   reported truthfully**: a criterion that earlier work already satisfies yields a passing
   test, and the pipeline has a dedicated path for exactly that. Do not bend the test to
   force a failure.
   If it PASSES, additionally confirm it is *capable* of failing — temporarily break the
   behaviour it pins, run the case and watch it go red, then restore the production code
   exactly and verify the restore with `git diff --exit-code` on the file you touched.
3. Leave no change to any file other than the test file.

### Report (last lines of your output)

TEST_PATH: <path of the test file>
TARGET_TEST: <the exact case name string you used>
AGAINST_UNMODIFIED: FAILS | PASSES
FAIL_OUTPUT: <the failure line — from the unmodified code if it fails there, otherwise from the temporarily-broken code>
