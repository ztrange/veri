# Plan for #2813 — verify-green runs only its named commands and never sets VERI_TEST_LOCK

- [ ] skill-edit step for the unit `skills/tdd/scripts/prompts/verify-green.md`: row VG19 joins its requirements list, and the run-the-tests check changes so the verifier runs only the commands the prompt names, never sets `VERI_TEST_LOCK`, and when a command gives no answer ends without a verdict rather than rerunning it another way ⟦skill-edit⟧ ⟦criterion 1⟧
