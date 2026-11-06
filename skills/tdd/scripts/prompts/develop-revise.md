{{SHARED}}

## Phase: develop-revise (redoing {{REVISE_PHASE}})

{{INCLUDE:_develop-revise-opening.md}}

### The step (this cycle's criterion)

{{STEP}}{{RED_CASES}}{{REPLACES_CASE}}{{SUITE_REPAIR}}{{FIXTURE_REPAIR}}{{FREEZE_RULE}}

### The verifier's rejection reason (address exactly this)

{{REJECTION_REASON}}

### When the step is too big for one green

Redoing green only: when the step needs more than one new behaviour at once, neither a
rewritten implementation nor `IMPOSSIBLE` is the honest answer. Report `SPLIT:` lines
instead of an {{INCLUDE:_develop-split.md}} leave the working tree exactly as you found it.

### The issue's behavior spec (context — the criterion above is what is in scope)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

0. **Check the step's size first, when the phase you are redoing is green.** If it needs
   more than one new behaviour at once, stop here and report `SPLIT:` lines as **When the
   step is too big for one green** above says — do not proceed to the steps below: with no
   implementation written, the run they ask for has no question to answer.
1. Read what this step left on disk and rewrite it to answer that objection — and only
   that objection. Do not drift beyond what the criterion and the reason require: a fix
   that also changes something the verifier did not object to gives it new grounds to
   reject.
2. Edit a test only as the phase you are redoing allows. {{TEST_REWRITE}}
3. Redoing green only: first run the fast command, the one `detect-test-command.sh --tier
   fast` prints, and confirm it is green. Then, whichever phase you are redoing, run the
   suites {{INCLUDE:_affected-suites-working-tree.md}} — and confirm the result the phase you
   are redoing calls for. Make each run through the wrapper `{{TIMED_TEST_RUN}}`, which
   records what the run cost and names the tier it belongs to:

       {{TIMED_TEST_RUN}} fast '' <the command detect-test-command.sh --tier fast printed>
       {{INCLUDE:_timed-test-run-affected.md}}

   {{INCLUDE:_exit-status-back.md}} so a red run stays red.

   To confirm that earlier steps' frozen test records still hold, run exactly
   `tests-frozen.sh check-earlier .tdd/issue-{{ISSUE_NUMBER}}.md --step {{STEP_ARGUMENT}}` — the
   run's own ledger, `.tdd/issue-{{ISSUE_NUMBER}}.md`, and never `.tdd/plan-ledger.md`.

   Run one suite through {{INCLUDE:_run-suite-lead.md}} suite,
   {{INCLUDE:_run-suite-same-way.md}} the test command above and say so in your report.
4. If the objection **cannot** be met — the criterion is already satisfied by existing
   code, or the reason asks for something the step cannot deliver — report `IMPOSSIBLE`
   and say why. That is a legitimate outcome and the pipeline acts on it. Do not fake a
   pass, weaken a test, or invent work to look productive.
   Redoing green only: when the objection can only be met by a test the step lacks, edit
   no test — report `OUTCOME: IMPOSSIBLE` with one `MISSING_TEST: <behaviour>` line naming
   the behaviour to pin, before the `OUTCOME:` line.
   Redoing green on a `⟦suite-repair⟧` or `⟦ci-repair⟧` step only: you may edit the one
   failing test the full run or CI left red, only as far as the repair needs. Every other
   test stays frozen.

### Report (last lines of your output)

OUTCOME: REWRITTEN | IMPOSSIBLE — <what you changed, or why the step cannot be met as stated>
AGAINST_UNMODIFIED: FAILS | PASSES | N/A — <does the test fail against the unmodified production code; N/A if you did not touch a test>
PREDICTED_FAILURE: <redoing red only — the assertion the rewritten test was predicted to fire on and the observed and expected values it fires on, as predicted before running; you may add the shape of the message as a hint only — the run is not compared on it; N/A otherwise>
PREDICTION: MATCHED | DIVERGED — <redoing red only, so omit this line entirely otherwise. MATCHED when the same assertion fired on the same observed and expected values, whatever the message text; DIVERGED only for a different assertion, different values, or a different kind of failure (an error instead of an assertion failure, or a pass). A message-text-only difference is MATCHED>
FAIL_OUTPUT: <redoing red only — the failure line the run printed; omit this line entirely otherwise>
PREDICTION_NOTE: <redoing red only, and only on DIVERGED — what actually happened and why it could not be reconciled; omit this line entirely otherwise>

or, when the green you are redoing is a step too big for one, those lines replaced by one
to three of:

SPLIT: <a behaviour-level criterion, one per line, in the order they must be built>{{WRONG_TEST_REPORT}}

REPORT-FORMAT revise | keys OUTCOME: AGAINST_UNMODIFIED: PREDICTED_FAILURE: PREDICTION: FAIL_OUTPUT: PREDICTION_NOTE: | suite exempt: the redone phase may be red, where the suite is meant to fail

REPORT-FORMAT revise-split | keys SPLIT: | suite exempt: a too-big step changes no code and runs no suite{{WRONG_TEST_FORMAT}}
