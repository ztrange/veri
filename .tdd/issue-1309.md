# Plan for #1309 — PRD 009 C3-1: a phased step carries one ledger mark per phase, and a resumed run starts at its next unmarked phase

- [x] On an open ledger step whose line lists its phases (expand, migrate, contract (a), contract (b)), `tick-ledger.sh --phase expand <ledger> <matcher>` writes the expand phase's mark onto that same line in one write and exits 0, leaving the step unchecked and every other line unchanged ⟦criterion 1⟧
- [x] `ledger-steps.sh next-phase` prints, for the first phased step not yet finished, which of its phases is next — expand on a step with no phase marked, migrate once expand is marked — and exits 3 when no phased step is unfinished ⟦criterion 1⟧
- [x] Once `tick-ledger.sh --phase` has marked every phase a step lists, in the order expand, migrate, contract (a), contract (b), readers treat it as a finished step: `ledger-steps.sh` reports it done, `next-unchecked.sh` no longer answers it, and `ledger-steps.sh next-phase` moves on to the next unfinished phased step ⟦criterion 1⟧
- [x] For a phased step that lists only some phases (say expand and contract (b)), `ledger-steps.sh next-phase` never answers a phase the step does not list: after expand is marked it answers contract (b), not migrate ⟦criterion 2⟧
- [ ] `tick-ledger.sh --phase <phase>` naming a phase the matched step does not list exits 2 and leaves the ledger byte-identical ⟦criterion 2⟧
- [ ] `tick-ledger.sh --phase <phase>` naming a listed phase while an earlier phase the step lists is still unmarked (migrate before expand) exits 2 and leaves the ledger byte-identical ⟦criterion 2⟧
