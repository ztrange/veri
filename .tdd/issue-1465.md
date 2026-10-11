# Plan for #1465 — A revise leaf can't run on a different model from the developer's first attempt (VERI_MODEL_REVISE)

- [x] With VERI_MODEL_REVISE and VERI_MODEL_DEVELOPER set to different models, leaf-model.sh prints VERI_MODEL_REVISE's model for a revise-* leaf name and for develop-exhausted, and VERI_MODEL_DEVELOPER's for a develop-* first-attempt name such as develop-red ⟦criterion 1⟧
- [x] With VERI_MODEL_REVISE unset, leaf-model.sh prints for revise-*, develop-exhausted and develop-* leaf names exactly the model it prints today: VERI_MODEL_DEVELOPER's, else VERI_MODEL's, else nothing ⟦criterion 1⟧
- [x] VERI_MODEL_REVISE set but empty makes leaf-model.sh exit 2 for a revise-* or develop-exhausted leaf name, with a stderr line naming VERI_MODEL_REVISE and nothing on stdout ⟦criterion 1⟧
- [x] VERI_MODEL_REVISE containing whitespace makes leaf-model.sh exit 2 for a revise-* or develop-exhausted leaf name, with nothing on stdout ⟦criterion 1⟧
- [x] A leaf launched through supervise.sh under a revise-* name runs with VERI_MODEL_REVISE's model, so the launch's recorded model and the claude --model flag it passes are that model ⟦criterion 1⟧
- [x] The metrics report's "Models requested" line lists VERI_MODEL_REVISE with its value, or unset, beside the other three model knobs ⟦criterion 2⟧ ⟂ refactor pending
- [ ] CLAUDE.md's model-knob invariant, SKILL.md's knob list under supervise.sh, and the leaf-model.sh usage header name VERI_MODEL_REVISE and say it governs revise-* and develop-exhausted leaves, and SKILL.md's preflight step 6 also asks leaf-model.sh about a revise leaf name so a bad VERI_MODEL_REVISE stops the run before any leaf launches ⟦diff-checked⟧ ⟦criterion 2⟧
