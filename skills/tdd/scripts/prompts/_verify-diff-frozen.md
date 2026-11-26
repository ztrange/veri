This step's green edited test cases verify-red already judged, after their red was frozen. Judge
`git diff {{FROZEN_EDIT}}~1 {{FROZEN_EDIT}}` instead of the range above: exactly those edits to the
step's frozen test files, nothing else. The step's uncommitted implementation is outside that diff
and is no reason to REJECT, and the rule rejecting a test added by the step's own commits does not
apply to the step's own Red case. The step's criterion is not the rule for this diff, and the
closing rule's "PASS if the diff satisfies the step's criterion" does not apply to it: what
verify-red judged is the bar. PASS only if every edit keeps or strengthens what each edited case
asserted when verify-red judged it, such as a fixture, an import or a helper moved, or an assertion
added or tightened. REJECT any edit that weakens it: an assertion loosened, removed or narrowed, an
expected value changed, a case skipped or marked expected to fail, or the inputs a case exercises
reduced. A production file in that diff is still a REJECT.
