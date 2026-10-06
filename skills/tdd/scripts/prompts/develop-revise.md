{{SHARED}}

## Phase: develop-revise (redoing {{REVISE_PHASE}})

{{INCLUDE:_develop-revise-opening.md}}

### The step (this cycle's criterion)

{{STEP}}{{REPLACES_CASE}}{{SUITE_REPAIR}}

### The verifier's rejection reason (address exactly this)

{{REJECTION_REASON}}

### When the step is too big for one green

Redoing green only: when the step needs more than one new behaviour at once, neither a
rewritten implementation nor `IMPOSSIBLE` is the honest answer. Report `SPLIT:` lines
instead of an implementation, changing no production code — one to three of them, each a
behaviour-level criterion small enough to be one red-green cycle of its own, in the order
they must be built. The conductor restores the tree, adds those steps ahead of this one
and comes back to this step later, so leave the working tree exactly as you found it.

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
2. **A rewritten test is a new test, and owes a new prediction**: predict its failure
   before you issue any command — which assertion fires first against the unmodified
   production code, the observed-versus-expected values it fires on, and the shape of the
   message the suite will print — then run, and compare what it printed against that
   prediction; never adjust the prediction to fit what you saw. The leaf whose attempt was
   rejected predicted a different test, so there is nothing here for you to inherit.
3. Redoing green only: first run the fast command, the one `detect-test-command.sh --tier
   fast` prints, and confirm it is green. Then, whichever phase you are redoing, run the
   suites `affected-suites.sh HEAD` prints for your change — it reads `HEAD` to the
   working tree, untracked files included, so build no commit, stash or worktree to name a
   range — and confirm the result the phase you
   are redoing calls for. Make each run through the wrapper `{{TIMED_TEST_RUN}}`, which
   records what the run cost and names the tier it belongs to:

       {{TIMED_TEST_RUN}} fast '' <the command detect-test-command.sh --tier fast printed>
       {{TIMED_TEST_RUN}} affected '<the suites affected-suites.sh printed>' <the command that runs them>

   The wrapper hands the command's own exit status straight back, so a red run stays red.
4. If the objection **cannot** be met — the criterion is already satisfied by existing
   code, or the reason asks for something the step cannot deliver — report `IMPOSSIBLE`
   and say why. That is a legitimate outcome and the pipeline acts on it. Do not fake a
   pass, weaken a test, or invent work to look productive.

### Report (last lines of your output)

OUTCOME: REWRITTEN | IMPOSSIBLE — <what you changed, or why the step cannot be met as stated>
AGAINST_UNMODIFIED: FAILS | PASSES | N/A — <does the test fail against the unmodified production code; N/A if you did not touch a test>
PREDICTED_FAILURE: <redoing red only — the assertion the rewritten test was predicted to fire on, the values it fires on and the shape of the message, as predicted before running; N/A otherwise>
PREDICTION: MATCHED | DIVERGED — <whether the run printed what you predicted; redoing red only, so omit this line entirely otherwise>

or, when the green you are redoing is a step too big for one, those lines replaced by one
to three of:

SPLIT: <a behaviour-level criterion, one per line, in the order they must be built>
