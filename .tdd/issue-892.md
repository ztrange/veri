# Plan for #892 — SKILL.md's develop-rebase launch passes an empty step text at the Draft PR step, so the leaf dies at launch

- [x] The Draft PR step's develop-rebase block reads its step text — the build-develop-prompt.sh rebase argument and the leaf launch's VERI_STEP — as the open step or, when none is open, the last done step, the same fallback the verdict-rebase line spells ⟦criterion 1⟧
- [x] The develop-reconcile block of Reconciling a rejected push reads its step text — the build-develop-prompt.sh reconcile argument and the leaf launch's VERI_STEP — as the open step or, when none is open, the last done step ⟦criterion 2⟧
- [x] The revise loop of Revising on a REJECT reads its step text — the revise event mark's VERI_STEP, the build-develop-prompt.sh revise argument, the revise leaf launch's VERI_STEP and the re-verify launch's VERI_STEP — as the open step or, when none is open, the last done step ⟦criterion 3⟧
