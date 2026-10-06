{{SHARED}}

## Phase: develop-red

Add exactly **ONE** new failing test case, and write **NO** production code.

### The step to pin (this cycle's criterion — pin ONLY this)

{{STEP}}

Pin it as *observable behaviour*: what the code does when it is called, not how it is
written inside. One criterion, one case — no extra cases, and no generality the step does
not ask for.

### What counts as a valid test

A case must hold all four of these, or it is not a test you may write:

1. **Behaviour, not mechanism.** It asserts the unit's output, exit code, the files or
   events it writes, or the error it names — never a process count, a fork count, or a
   timing across a suite run. Those are observed with `make profile` and reported in the PR
   body; a test never asserts on them. The one exception is a call count the criterion
   itself names as the behaviour (e.g. "the launcher is called once"): pin that with an
   **in-process spy** — replace the one wrapper function the code under test calls with a
   same-named function that records its calls, and assert on that record — never a `PATH`
   shim that counts real process launches across a suite run. A spy on one function call is
   behaviour; a shim counting real processes over a whole suite is the mechanism rule 2 and
   3 forbid.
2. **Lightweight.** It targets ~100ms. A costly dependency — network, a git remote, the
   `claude` binary, a real sleep or wait, a server — is replaced with a stub, a same-named
   fake, or the injected clock, unless the behaviour under test IS that dependency's real
   use, in which case one case may exercise it for real.
3. **Self-contained.** It never runs another test suite, whole or sliced, and never re-runs
   the suite it lives in.
4. **On-target.** It fails for the reason the criterion names, not an unrelated error.

If the step's criterion can only be pinned by a test that breaks 1–3 — e.g. "the suite
starts at most N processes" has no assertion that isn't a process count — **do not write
that test.** Skip straight to the report below with `AGAINST_UNMODIFIED: UNTESTABLE` and a
`WHY:` line naming which rule the only available test would break. Do not weaken the
criterion into something else it does not say, and do not write the costly or
implementation-pinning test anyway to force a pass.

{{BUG_REPRODUCTION}}
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
   the production code it will run against, and state — in your output, before you issue any
   command — which assertion fires first, the observed-versus-expected values it fires on,
   and the shape of the message the suite will print. It is formed from the test and the code,
   never from the output: a prediction written after the run is a transcription of it, and
   answers nothing.
3. Run the suites `affected-suites.sh HEAD` prints for your change — it reads `HEAD` to the
   working tree, untracked files included, so build no commit, stash or worktree to name a
   range — not the full suite, and not one suite picked by hand — against the **unmodified** production code, and record whether
   the new case FAILS or PASSES. The only question this phase asks is whether that one case
   fails; the suite holding the new case is among those it prints, and the others read the
   same files, and must stay green. Run one suite through
   `run-suite.sh <suite>` — the one invocation for a single suite, so that every leaf on this
   step runs it the same way and none of them is handed a suite that died partway and still
   exited 0. If that runner cannot run a suite in this repository, fall back to
   the test command above and say so in your report.
   Make that run through the wrapper `{{TIMED_TEST_RUN}}`, which records what the run cost
   and names the tier it belongs to:

       {{TIMED_TEST_RUN}} affected '<the suites affected-suites.sh printed>' <the command that runs them>

   The wrapper hands the command's own exit status straight back, so a red run stays red —
   and red is the answer this phase is after.
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
