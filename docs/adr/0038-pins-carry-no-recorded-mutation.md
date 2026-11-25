# Pins carry no recorded mutation

A pin's hand mutation is no longer recorded, and no later refactor replays it. `pin-recheck.sh`,
the `.tdd/issue-<n>-mutations.md` records, the re-pin step and `pin-reject-route.sh --recheck` are
removed (PRD 044, D4). verify-pin still demands that a pin test fail at the branch base under a hand
mutation; it records nothing. This supersedes ADR-0033's naming of `pin-recheck.sh` among the
mechanical checks a skipped verifier keeps.

## Context

A **pin** (CONTEXT.md) is a step whose criterion already holds at the branch base. verify-pin made
its test fail at the base under a hand mutation, and the probe recorded that mutation in
`.tdd/issue-<n>-mutations.md`. `pin-recheck.sh` replayed every recorded mutation over each later
refactor, so that a refactor could not quietly leave a pin test unable to fail. A finding became a
re-pin step or a `repin-failed` / `not-checked` bail.

The recorded mutations bind to literal source text, so a refactor that rewrites a pinned line owes
a re-pin or bails, whether or not the test still guards anything. Measured at `876b43e148`, with
the owner's counts at `3b33e78b00` (`specs/prd-044.md`, *Facts*):

- 2762 `test: pin` commits on `main`, against 2230 other `test: ` commits and 10815
  `feat`/`fix`/`refactor` commits.
- 350 committed `.tdd/issue-*-mutations.md` files, holding 621 file records.
- Ledgers hold 133 `⟂ retired unpinnable`, 21 `⟂ retired already` and 4 re-pin steps.
- No pin test or pin-recheck finding that caught a real regression was found. The two issues
  matching "pin-recheck" and "real regression" are #3323 (a deliberate supersede) and #3521 (a
  flake).
- Issue hits for pin-recheck: 152 in all, 2 open, 41 in a title, and all 41 title hits are
  plumbing bugs.

## Decision

- **Removed:** `pin-recheck.sh` and its module, the mutation records and their writer, the re-pin
  `⟦diff-checked⟧` step, `pin-reject-route.sh --recheck`, the `repin-failed` and `not-checked` bail
  causes, and the `.tdd/pin-recheck-ok` receipt the clear and the tick required.
- **The committed `.tdd/issue-*-mutations.md` files are deleted.** Git history keeps them.
- **verify-pin is unchanged except that it records nothing.** It still demands fail-at-base and a
  hand mutation; PRD 044.2 decides those separately.
- **A `⟦go-red⟧` step keeps its tick guard** by reading an untracked run-state receipt,
  `.tdd/go-red-probed`, instead of the record.
- **Supersedes ADR-0033 in part:** its *Consequences* named `pin-recheck.sh` among the mechanical
  checks that keep running when a verifier is switched off. There is no such check any more; the
  full suite and `mutation-parity.sh` still run.

## Considered options

- **Keep the recheck for existing records only**: rejected. The existing records bind to text that
  later refactors rewrite, so they carry the same re-pin and bail cost, and none caught a real
  regression.
- **Keep it as is**: rejected, for the facts above: plumbing bugs and re-pin work, no regression
  caught.

## Consequences

- A refactor that rewrites a pinned line no longer owes a re-pin step and no longer bails over a
  recorded mutation.
- A pin test can be weakened by a later refactor without a mechanical replay noticing.
  verify-refactor and the full suite are what remain to see it.
- `mutation-parity.sh` (ADR-0030) and the `legacy` kind's surround mutants are untouched.
