### The rendered plan prompt for a spec carrying a ## Refactor section tells the verifier to REJECT a refactor-kind plan that holds a ⟦phases: …⟧ step ⟦criterion 2⟧
- the new `#1527` case in `test_build_verify_prompt.py` repeats the spec/ledger/render setup of the `#679 no-op` case; a shared helper would also edit that older case, which this cycle did not write
