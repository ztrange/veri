{{SHARED}}

## Phase: develop-diff

This step's criterion is a property of the branch's own diff: something removed, left
unchanged, or confined to named lines. A blind verifier judges it against the diff alone,
so no test is this step's deliverable.

### The step

{{STEP}}

{{INCLUDE:_develop-spec-context-only.md}}

1. Make the change the step's criterion names, and nothing else, then commit that change
   as its own commit, its subject ending in `(#<issue>)`.
2. When the criterion is that something stays unchanged, make no commit: leave the tree as
   you found it.
3. Add no test. A case that pins this criterion by reading another file's text or the git
   history is rejected.
4. {{INCLUDE:_develop-diff-run-fast-affected.md}}

### Report (last lines of your output)

DIFF: <the change committed, in one line, or NONE when the criterion is that something stays unchanged>
SUITE: GREEN | RED — <the final summary line of that run>
