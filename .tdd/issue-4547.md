# Plan for #4547 — A step replaced by add-ledger-step.sh instead-of inherits the replaced step's rejected wait record and stops at REVISE_BUDGET

- [x] after `add-ledger-step.sh instead-of` replaces the open step with a same-text ⟦added⟧ step, run-step launches red-half, not revise ⟦criterion 1⟧
- [x] `add-ledger-step.sh instead-of` on the open step leaves no `.tdd/verdict-<phase>.exit` ⟦criterion 2⟧
- [x] `add-ledger-step.sh instead-of` on a step after the open one leaves the open step's `.tdd/verdict-<phase>.exit` in place
