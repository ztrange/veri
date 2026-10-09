{{SHARED}}

## Phase: verify-rebase

This run's branch was rebased onto `{{ONTO_SHA}}`, the default branch's tip, from
`{{PRE_REBASE_SHA}}`, where it stood before. The rebase stopped on conflicts, and a developer
agent resolved them: that resolution is new code no verifier has seen. Judge the rebased
branch at `HEAD`.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **The full test command is green on HEAD.** Run the project's full test command
   (`detect-test-command.sh` prints it) yourself, on `HEAD`, not the fast tier: a resolution
   can break a suite no single file's change would name. Make that run through the wrapper
   {{INCLUDE:_timed-test-run-tier.md}} —
   `all`, since the whole test command is what runs:

       {{TIMED_TEST_RUN}} all '' <the full test command>

   {{INCLUDE:_exit-status-back.md}} so a red run stays red.
   A red run is a REJECT.
2. **Both sides survive.** The branch's own changes — `git diff {{ONTO_SHA}}...{{PRE_REBASE_SHA}}`
   shows them — and the default branch's changes — `git diff {{PRE_REBASE_SHA}}...{{ONTO_SHA}}`
   shows them — must both be present in `HEAD`, with their behaviour intact. A resolution
   that drops or weakens either side's change is a REJECT even when the suite is green, and
   the REJECT names the file and the change that was lost.

PASS only if the full test command is green on HEAD and both the branch's changes and the
default branch's changes survived the resolution.
