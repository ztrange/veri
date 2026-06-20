# Branch per issue, draft PR on completion, human merges

The conductor works each issue on its own branch (`tdd/<issue>-slug`), lands every
green and refactor commit there, and on completion pushes the branch and opens a **draft**
pull request linked to the issue (`Closes #<n>`). The human reviews and merges; the
framework **never auto-merges**.

## Context

Work is GitHub-issue-driven and will go parallel, so isolation and a review surface both
matter. A branch per issue gives a clean PR for review and is exactly the seam v2 needs:
one git worktree per branch lets concurrent conductors work without colliding. Draft +
human-merge keeps the quality/control gate the user cares about — autonomous coding,
deliberate landing.

## Consequences

The framework now also depends on `gh` for PR creation and on push access. v2 parallel
uses `git worktree add` per `tdd/<n>` branch. The issue↔PR link is made automatically
(`Closes #<n>`) so merging the PR closes the issue. Never auto-merge is a hard limit, not
a default — landing is always a human act.
