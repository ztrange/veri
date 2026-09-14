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
2. **Predict the failure before you run anything.** Read the case you just wrote against
   the production code it will run against, and state — in your output, before you issue any
   command — which assertion fires first, the observed-versus-expected values it fires on,
   and the shape of the message the suite will print. It is formed from the test and the code,
   never from the output: a prediction written after the run is a transcription of it, and
   answers nothing.
3. Run the suite that holds the new case — not the full suite — against the **unmodified**
   production code, and record whether the new case FAILS or PASSES. The only question this
   phase asks is whether that one case fails. How this repository runs one suite is a
   convention like any other — establish it under **Read the conventions out of the
   repository** at the top of this prompt, from the files that are already there.
   If the repository has no way to run one suite on its own, fall back to the test
   command above and say so in your report.
4. **Compare what it printed against what you predicted**, and report which it was.
   *Matched* — carry on. *Diverged* — the test is the suspect, not the prediction: the case
   failed for a reason you did not write it to catch, which is how a typo'd fixture path, a
   helper this suite does not have, or an assertion on the wrong value all reach Green
   looking red. Revise the **test**, predict again and re-run, until the observed failure is
   the predicted one or you can say precisely why the two cannot be reconciled. Never adjust
   the prediction to fit what you saw — that is the whole of the discipline.
5. **Either answer is acceptable, and must be reported truthfully**: a criterion that
   earlier work already satisfies yields a passing test, and the pipeline has a dedicated
   path for exactly that. Do not bend the test to force a failure.
   If it PASSES, additionally confirm it is *capable* of failing — predict what temporarily
   breaking the behaviour it pins should make the case print, then break it, run the case,
   and check what it printed against that prediction, all **before** you restore: once the
   production code is back that output cannot be reproduced, so a comparison made after the
   restore is one made against a recollection, and a red bar nobody read is no answer. Then
   restore the production code exactly and verify the restore with `git diff --exit-code`
   on the file you touched.
6. Leave no change to any file other than the test file.

### Report (last lines of your output)

TEST_PATH: <path of the test file>
TARGET_TEST: <the exact case name string you used>
AGAINST_UNMODIFIED: FAILS | PASSES
FAIL_OUTPUT: <the failure line — from the unmodified code if it fails there, otherwise from the temporarily-broken code>
PREDICTED_FAILURE: <the assertion, the values and the message shape — as predicted before running>
PREDICTION: MATCHED | DIVERGED
PREDICTION_NOTE: <on DIVERGED, what actually happened and why it could not be reconciled>
