# A released issue's own draft PR is no claim

ADR-0024 made an open PR saying `Closes #<n>` the only claim, and a bailed run keeps its draft
PR open so its issue stays out of the pool. This narrows it: a PR on the issue's **own run
branch**, `tdd/<n>-…`, does not withhold the issue from `solvable-issues.sh`. Every other open
PR saying `Closes #<n>` still does.

## Context

Since ADR-0024 two GitHub labels came to mark a run too: the opt-in label comes off and
`taken:<lane>` goes on at the claim (`unlabel-issue.sh`), and selection skips any `taken:*`
issue. PL52 (#2030) says a human re-queues a claimed issue by restoring the opt-in label and
removing `taken:<lane>`. For an issue with a WIP draft PR, which is nearly every parked or
bailed one, that never worked: the PR still withheld it. Un-parking by hand was worse, removing
only `parked` and leaving the issue claimed, unlabelled and invisible to `dispatch.sh`. #3284
sat that way on 2026-11-08 after its blocker #3357 landed.

## Decision

- `release-issue.sh <n>` hands a parked or bailed issue back: it adds the opt-in label, removes
  this lane's `taken:<lane>`, then removes `parked` and `bailed`.
- Selection treats a PR on `tdd/<n>-…` as no claim on `<n>`. A bail is still not re-taken: it
  keeps `taken:<lane>` and lacks the opt-in label, so selection skips it before any PR is read.
  Only a deliberate release lets it through, and the resume continues the same branch and PR
  (ADR-0024: a resumed run edits the PR its branch already has).

### Rejected

- **Release closes the draft PR.** It discards the visible record a bail exists to leave
  (ADR-0024's own rejection).
- **Re-add the opt-in label whenever `parked` or `bailed` comes off.** The conductor removes
  `bailed` at every resume start, so live runs would be re-queued, and the label alone leaves
  `taken:<lane>`, which keeps the issue out anyway.

## Consequences

A PR a human opens by hand on another branch still claims its issue. Two machines could both
take a released issue inside the claim window ADR-0024 already accepts; the first claim's
`taken:<lane>` closes it as before.

## Amendment 2026-11-09: only while the PR is a draft (#3460)

A run that finished (Done) readies its own-branch PR, and its resume had never re-claimed the
issue, so the opt-in label stayed and dispatch relaunched the issue, wiping a reviewer's
worktree. Two changes: selection treats an own-run-branch PR as no claim **only while it is a
draft**; a readied one claims its issue like any other open `Closes #<n>` PR. And `event.sh
resume` (with `VERI_STATE_LABEL_ISSUE`) re-claims a released issue, adding `taken:<lane>` and
removing the opt-in label besides removing `bailed`. "Claims nothing" above reads as "while a draft".
