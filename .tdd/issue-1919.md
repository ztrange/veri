# Plan for #1919 — Prompt builders read a repair marker anywhere in the step, the freeze gate only in its trailing markers

- [x] build-develop-prompt.sh green, for a step that names the suite-repair marker mid-sentence but does not end in it, renders the ordinary frozen-test freeze rule, not the repair test-edit grant (the repair check that sets FREEZE_RULE) ⟦criterion 1⟧
- [ ] build-develop-prompt.sh green, for a step that names the ci-repair marker mid-sentence but does not end in it, renders the ordinary frozen-test freeze rule, not the repair test-edit grant ⟦criterion 1⟧
- [ ] build-develop-prompt.sh green, for a step that names the suite-repair marker mid-sentence but does not end in it, renders no suite-repair green paragraph ⟦criterion 1⟧
- [ ] build-develop-prompt.sh red, for a step that names the ci-repair marker mid-sentence but does not end in it, renders no ci-repair red paragraph ⟦criterion 1⟧
- [ ] build-verify-prompt.sh green, for a step that names the suite-repair marker mid-sentence but does not end in it, renders no suite-repair verify-green paragraph ⟦criterion 1⟧
- [ ] build-verify-prompt.sh green, for a step that names the ci-repair marker mid-sentence but does not end in it, renders no ci-repair verify-green paragraph ⟦criterion 1⟧
- [ ] A step whose trailing markers include the suite-repair or ci-repair marker still gets the permissive prompts: the existing cases stay green ⟦full-suite⟧ ⟦criterion 2⟧
