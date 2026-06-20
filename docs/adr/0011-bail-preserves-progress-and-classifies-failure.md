# On bail: preserve progress, push the branch, classify the failure on the issue

When the conductor bails an issue mid-run it reverts only the half-done failing step
(restoring a clean tree), keeps all completed green/refactor commits, pushes the branch
so it is visible, posts a diagnostic comment on the issue, and stops. **No PR** is opened
— the work is incomplete. The bail comment must **classify** the failure:

- **System failure** — the plumbing broke: a leaf went stuck and the supervisor killed
  it, `gh`/git errored, a baseline precondition failed, infrastructure. → go fix the
  framework.
- **Process failure** — the methodology spoke: a verdict was `REJECT` past the attempt
  budget, green can't pass, overfit with no triangulating step. → go refine the
  issue/test/code.

## Context

Completed cycles are real, green, committed TDD progress; discarding them wastes work and
forces a from-zero re-run. The user wants the diagnosis on the issue thread, and
explicitly wants it to help debug "be it on the system or the process" — so the comment
separates a tooling failure from a methodology outcome, because they have different fixes.

## Consequences

A bailed issue leaves a pushed branch with valid partial progress and an issue comment
naming the failing step, the classification, and the reason. Re-running resumes from the
ledger's first unchecked step (ADR-0007). The system-vs-process tag is the single most
useful signal for the human triaging a stalled run.
