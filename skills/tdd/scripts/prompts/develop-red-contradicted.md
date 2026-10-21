{{SHARED}}

## Phase: develop-red

Update the expectation of the one existing test case named below to the step's criterion. Edit that case **only**: write **NO** new test and **NO** production code.

### The step (this cycle's criterion)

{{STEP}}

### The case to update

{{CASE}}

This existing case asserts the opposite of the criterion above, so a green that implements the
criterion would turn it red. Change its expectation so it pins the criterion instead; leave every
other case, and all production code, untouched.

{{INCLUDE:_develop-red-valid-test.md}}

{{INCLUDE:_develop-red-spec-and-testability.md}}
1. Read the existing suite the case belongs in and add it in that suite's own style,
   leaving its other cases untouched and green. If no suite fits, create one that matches
   the repository's testing idiom.
{{INCLUDE:_develop-red-run-and-report.md}}
