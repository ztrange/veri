{{SHARED}}

## Phase: develop-exhausted

This step's revise budget is spent: every attempt at it was rejected by the blind
verifier. {{INCLUDE:_develop-fresh-leaf.md}} those attempts, so the last rejection
reason below is the whole of what you have to reason from. {{INCLUDE:_develop-not-here.md}}
the step again. Answer in a `STATEMENT:` line.
Do not modify, revert or remove anything in the working tree: what is there is
the attempts' work, and the run keeps it.
A statement that the criterion already holds must cite a run of the test command
you were given, not a run of one case alone.

### The step (the criterion nothing could satisfy)

{{STEP}}

### The verifier's last rejection reason

{{REJECTION_REASON}}

{{INCLUDE:_develop-spec-cut-from.md}}

### Report (last lines of your output)

If the step is more than one behaviour, one to three lines, each a behaviour-level criterion
small enough to be one red-green cycle of its own, in the order they must be built:

SPLIT: <a behaviour-level criterion, one per line, in the order they must be built>

If it needs a decision this run has no authority to make, one line naming that decision:

NEEDS_USER: <the decision, stated so the user can answer it>

If it is neither — this step is one behaviour the attempts simply failed to satisfy — print no
SPLIT: line and no NEEDS_USER: line; the run then bails. Whichever answer you give, your
STATEMENT: line comes with it.

REPORT-FORMAT exhausted | keys STATEMENT: SPLIT: NEEDS_USER: | suite exempt: the leaf changes nothing and answers in prose
