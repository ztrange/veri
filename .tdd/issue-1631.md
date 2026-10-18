# Plan for #1631 — add-ledger-step.sh instead-of counts the replacement against VERI_STEP_GROWTH before removing the replaced ⟦added⟧ step

- [x] An `add-ledger-step.sh … instead-of` replacing an `⟦added⟧` step with one text, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, exits 0 and replaces the step, leaving the `⟦added⟧` count unchanged and filing nothing under `## Owed steps` (a small pytest case driving the module in-process) ⟦criterion 1⟧ ⟂ refactor pending
