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

If older committed cases the step's change legitimately supersedes are why the step could not
be satisfied, and they can be edited, with no production code, to hold both before and after
the step's change, one line per such case; the run then adds a test-only step ahead of this
one. Name only cases committed before this step, never a case this step's own Red wrote. Give
this answer instead of a split or a decision, never beside one:

STEP_AHEAD: <file>::<case>

If it is none of these — this step is one behaviour the attempts simply failed to satisfy —
print no SPLIT: line, no NEEDS_USER: line and no STEP_AHEAD: line; the run then bails.
Whichever answer you give, your STATEMENT: line comes with it.

REPORT-FORMAT exhausted | keys STATEMENT: SPLIT: NEEDS_USER: STEP_AHEAD: | suite exempt: the leaf changes nothing and answers in prose
