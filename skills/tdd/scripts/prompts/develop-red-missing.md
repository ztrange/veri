{{SHARED}}

## Phase: develop-red-missing

Add exactly **ONE** new failing test case that pins the behaviour named below, and write **NO** production code. Never edit another case.

### The step (this cycle's criterion)

{{STEP}}

### The behaviour no test pins

A rejection of this step's green found that no test pins a line the step needs. Its reason, verbatim:

{{REJECTION_REASON}}

Pin the behaviour its `MISSING_TEST:` line names, in one case, as observable behaviour: what the
code does when it is called, not how it is written inside. Leave every other case, and all
production code, untouched.

{{INCLUDE:_develop-red-valid-test.md}}

### The issue's behavior spec (context only — pin only the step above)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

0. **Check testability first.** Before writing anything, hold the step's criterion against
   **What counts as a valid test** above. If no case can pin it without breaking rule 1, 2
   or 3, stop here and report `AGAINST_UNMODIFIED: UNTESTABLE` with `WHY:` — do not proceed
   to the steps below.
1. Read the existing suite the case belongs in and add it in that suite's own style,
   leaving its other cases untouched and green. If no suite fits, create one that matches
   the repository's testing idiom.
2. **Predict the failure before you run anything.** Read the case you just wrote against
   the production code it will run against, and write — to `.tdd/red-prediction.md`, before
   you run any suite — which assertion fires first, the observed-versus-expected values it fires on,
   and the shape of the message the suite will print. It is formed from the test and the code,
   never from the output: a prediction written after the run is a transcription of it, and
   answers nothing.
3. Run the suites {{INCLUDE:_affected-suites-working-tree.md}} — not the full suite, and not one suite picked by hand — against the **unmodified** production code, and record whether
   the new case FAILS or PASSES. The only question this phase asks is whether that one case
   fails; the suite holding the new case is among those it prints, and the others read the
   same files, and must stay green. Run one suite through
   {{INCLUDE:_run-suite-lead.md}} suite, {{INCLUDE:_develop-run-suite-same-way.md}}
   the test command above and say so in your report.
   Make that run through the wrapper {{INCLUDE:_timed-test-run.md}}
   and names the tier it belongs to:

       {{INCLUDE:_timed-test-run-affected.md}}

   {{INCLUDE:_exit-status-back.md}} so a red run stays red —
   and red is the answer this phase is after.
   Save that run's output to `.tdd/red-run-output.txt`, the file `red-divergence.sh` dates your
   prediction file against.
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

TEST_PATH: <path of the test file, or NONE on UNTESTABLE>
TARGET_TEST: <the exact case name string you used, or NONE on UNTESTABLE>
AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE
WHY: <UNTESTABLE only — which rule (1, 2 or 3) the only available test would break, and why>
FAIL_OUTPUT: <the failure line — from the unmodified code if it fails there, otherwise from the temporarily-broken code>
PREDICTED_FAILURE: <the missing name, when the predicted failure is an error on the name the step introduces rather than an assertion; otherwise the assertion, the values and the message shape — as predicted before running>
PREDICTION: MATCHED | DIVERGED
PREDICTION_NOTE: <on DIVERGED, what actually happened and why it could not be reconciled>

REPORT-FORMAT red | keys TEST_PATH: TARGET_TEST: AGAINST_UNMODIFIED: WHY: FAIL_OUTPUT: PREDICTED_FAILURE: PREDICTION: PREDICTION_NOTE: | suite exempt: a red step's test is meant to fail
