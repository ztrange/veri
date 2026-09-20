# Plan for #362 — verify-refactor proposes an unhandled edge case as NEW_STEP: instead of rejecting

- [x] The refactor verifier prompt tells the verifier to report an unhandled edge case the spec implies as a NEW_STEP: line before VERDICT:, and no longer to REJECT for it ⟦criterion 1⟧
- [x] Every built verifier prompt's output contract allows NEW_STEP: lines before the final VERDICT:/REASON: pair ⟦criterion 2⟧
- [x] parse-verdict.sh returns the same verdict and reason for output carrying NEW_STEP: lines before the final pair as for one without ⟦criterion 3⟧
- [x] SKILL.md's Refactor section adds the passing verify-refactor output's NEW_STEP: values to the ledger after STEP, in the same add-ledger-step.sh call as the refactor leaf's ⟦criterion 4⟧
