{{SHARED}}

## Phase: develop-red-repair

Repair the one test case named below, which this step's Red wrote and which green reported wrong. Edit that case **only**: create **NO** suite, write **NO** new case and **NO** production code.

### The step (this cycle's criterion)

{{STEP}}

### The case to repair

{{CASE}}

Green reported this case wrong:

{{WRONG_TEST_REASON}}{{SUPERSEDED_CASES}}

Fix the defect that report names in this case, so it still pins the step's criterion; leave every
other case, and all production code, untouched.

{{INCLUDE:_develop-red-valid-test.md}}

{{INCLUDE:_develop-red-spec-and-testability.md}}
1. Read the suite the case belongs in and repair the case in that suite's own style,
   leaving its other cases untouched and green. Never create a suite.
{{INCLUDE:_develop-red-run-and-report.md}}
