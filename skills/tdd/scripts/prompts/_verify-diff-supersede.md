This step is a supersede edit. Judge `git diff {{SUPERSEDE_BASE}}` instead of the range above: the
working tree against the snapshot taken before the red-supersede edit, so only the edits to the
named older cases. The step's own uncommitted implementation and its own recorded Red case are
outside the diff under judgement and are no reason to REJECT; the rule rejecting a test added by
the step's own commits does not apply to that Red case. A production file touched in that diff, or
an assertion removed in it, is still a REJECT.

