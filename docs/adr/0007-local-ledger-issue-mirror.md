# Local file ledger is the source of truth; the issue mirrors it

The plan/loop state of record is a **local, committed ledger file**, one per issue
(parallel-safe naming, e.g. `.tdd/issue-<n>.md`), living in the target project's repo.
Each cycle checks off its step in the ledger and commits that change atomically with the
cycle's code, so git state and checklist state never diverge. The GitHub issue thread
receives progress comments that **mirror** the ledger for human visibility.

## Context

Robustness/resumability was chosen over the single-source elegance of treating the issue
comment as the ledger. A committed local file is trivially parseable (`- [ ]` / `- [x]`),
diffs cleanly, and is atomic with the code commit — so a crash leaves git and ledger
consistent. This refines ADR-0005: the issue is the canonical *human-facing* record; the
ledger is the canonical *resume* state. It is the reference suite's `TODO.md`, made
per-issue and mirrored to GitHub.

## Consequences

Two surfaces exist and must be kept in sync; the issue is a mirror that can lag without
breaking resumption (the ledger is authoritative). Resume = read the ledger, find the
first unchecked step, continue. Crash mid-cycle is caught by the baseline clean-tree
check (revert the half-done step, the ledger still shows it unchecked). Per-issue files
keep v2 parallel runs from colliding, especially under git worktrees.
