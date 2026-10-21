### The issue's behavior spec (context only — pin only the step above)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

0. **Check testability first.** Before writing anything, hold the step's criterion against
   **What counts as a valid test** above. If no case can pin it without breaking rule 1, 2
   or 3, stop here and report `AGAINST_UNMODIFIED: UNTESTABLE` with `WHY:` — do not proceed
   to the steps below.
