# The GitHub issue thread is the observability channel

The conductor narrates progress by posting comments to the GitHub issue it is solving —
the plan, the outcome of each TDD cycle, and the final result or bail (with its trail).
The issue thread is the primary place a human watches the run and reviews what happened,
in preference to (or alongside) a local progress log.

## Context

The user works out of the issue thread already and wants progress tracked there. Keeping
the work and its record in the same place is an XP-flavored fit: a bailed attempt leaves
a comment trail exactly where the next person looks. This replaces the reference suite's
`.tdd-progress.log` as the human-facing surface (a local log may still exist for
`tail -f` and supervisor heartbeat, but it is not the canonical record).

## Consequences

Progress posting costs GitHub API calls and can make the issue noisy, so updates are
posted at **meaningful milestones** — plan posted, per-cycle outcome, final result/bail —
not per leaf. Granularity is tunable. The framework now depends on `gh` for both intake
and observability, so an authenticated `gh` is a precondition.
