{{SHARED}}

## Phase: develop-green

Write the **minimum** production code that makes the one failing test pass, and keep the
fast command and the affected suites green.

### The step (this cycle's criterion)

{{STEP}}

### The failing test

- Test file: `{{TEST_PATH}}`
- Target case: `{{TARGET_TEST}}`
- Test command: `{{TEST_CMD}}`

**Do not modify the test.** Not its assertions, not its inputs, not its name. Making the
bar easier to clear is not clearing it: a pass bought by weakening, skipping or deleting
the case is a rejected step. If the test itself looks wrong, say so in your report and
stop — do not edit it.{{REPLACES_CASE}}{{SUITE_REPAIR}}

### When the step is too big for one green

A step that needs more than one new behaviour at once has a third answer, and it is not a
weakened test or a half-written implementation. Report `SPLIT:` lines instead of an
{{INCLUDE:_develop-split.md}} a tree left carrying part of an implementation
nobody has written a test for would poison the first of them: leave the working tree
exactly as you found it.

### The issue's behavior spec (context — build only what the failing test demands)

{{ISSUE_SPEC}}

### What to do

0. **Check the step's size first.** If it needs more than one new behaviour at once, stop
   here and report `SPLIT:` lines as **When the step is too big for one green** above says
   — do not proceed to the steps below: with no implementation written, none of the runs
   they ask for has a question to answer.
1. Make the target case pass with the smallest change that genuinely implements the
   behaviour. No generality, options, flags or extra cases the test does not demand —
   later steps triangulate those.
2. Iterate against the suite that holds the target case, not the full suite: that one
   suite answers the only question each iteration asks, and answers it in a fraction of
   the time. Run one suite through {{INCLUDE:_run-suite-lead.md}}
   suite, {{INCLUDE:_run-suite-same-way.md}} the test command above and say so in your report.
3. Exactly once, immediately before you write the `SUITE:` report line, run the fast
   command, `{{FAST_CMD}}` (`detect-test-command.sh --tier fast` prints it), then run
   the suites that `affected-suites.sh` prints for your change, and confirm both runs are
   green. Make each of those two runs through the wrapper
   {{INCLUDE:_timed-test-run-tier.md}}:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   The wrapper hands the command's own exit status straight back, so a red run stays red.
   That pair
   replaces the full suite, and runs exactly once: the conductor runs the full command
   itself, before it readies the PR. A new pass bought with a broken sibling test is not a
   pass; fix it or revert.
4. Leave no change this step does not require.

### Report (last lines of your output)

IMPL_PATH: <comma-separated paths of the production files you created or changed>
SUITE: GREEN | RED — <the final summary line of that run>

or, when the step is too big for one green, those two lines replaced by one to three of:

SPLIT: <a behaviour-level criterion, one per line, in the order they must be built>
