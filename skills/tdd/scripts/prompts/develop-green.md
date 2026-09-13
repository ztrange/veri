{{SHARED}}

## Phase: develop-green

Write the **minimum** production code that makes the one failing test pass, and keep the
full suite green.

### The step (this cycle's criterion)

{{STEP}}

### The failing test

- Test file: `{{TEST_PATH}}`
- Target case: `{{TARGET_TEST}}`
- Test command: `{{TEST_CMD}}`

**Do not modify the test.** Not its assertions, not its inputs, not its name. Making the
bar easier to clear is not clearing it: a pass bought by weakening, skipping or deleting
the case is a rejected step. If the test itself looks wrong, say so in your report and
stop — do not edit it.

### The issue's behavior spec (context — build only what the failing test demands)

{{ISSUE_SPEC}}

### What to do

1. Make the target case pass with the smallest change that genuinely implements the
   behaviour. No generality, options, flags or extra cases the test does not demand —
   later steps triangulate those.
2. Iterate against the suite that holds the target case, not the full suite: that one
   suite answers the only question each iteration asks, and answers it in a fraction of
   the time. How this repository runs one suite is a convention like any other —
   establish it under **Read the conventions out of the repository** at the top of this
   prompt, from the files that are already there.
3. Run the **full suite** exactly once, immediately before you write the `SUITE:` report
   line, and confirm it is green. A new pass bought with a broken sibling test is not a
   pass; fix it or revert.
4. Leave no change this step does not require.

### Report (last lines of your output)

IMPL_PATH: <comma-separated paths of the production files you created or changed>
SUITE: GREEN | RED — <the suite's final summary line>
