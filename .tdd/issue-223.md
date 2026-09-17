# Plan for #223 — A blind verify-refactor judges the whole spec, so a later criterion can be demanded from inside an earlier step and no revise can satisfy it

- [x] build-verify-prompt.sh accepts an optional --step '<STEP>' flag before the positionals and every verify-*.md prompt it builds shows that step and says the verdict is about that criterion only ⟦criterion 1⟧
- [x] verify.sh accepts --step '<STEP>' before its positionals and hands it to the verifier prompt, never reading ambient VERI_STEP into the prompt ⟦criterion 1⟧
- [x] build-verify-prompt.sh takes the step only from --step: a VERI_STEP in the environment with no flag leaves no step in the prompt, and it has no parameter for the developer's rationale ⟦criterion 2⟧
- [x] verify-refactor.md tells the verifier a shortfall against a criterion outside the step under judgement goes in REASON: as out of scope and is not by itself a REJECT ⟦criterion 3⟧
- [x] With no --step flag, build-verify-prompt.sh and verify.sh still build a valid verifier prompt for every phase with no unfilled step placeholder ⟦criterion 4⟧
- [ ] SKILL.md passes --step '<STEP>' on every verify.sh call the conductor makes (red, pin, green, refactor, revise re-verify, resume)
