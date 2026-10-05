# Plan for #907 — SKILL.md: remaining step-text spellings read only ledger-steps.sh current, so they go empty after the last step is done

- [x] The Draft PR step's verdict-rebase launch reads its VERI_STEP as the open step or, when none is open, the last done step, the same fallback its --step argument already spells
- [x] The revise diff prompt line of Revising on a REJECT reads its build-develop-prompt.sh step argument as the open step or, when none is open, the last done step
- [x] The revise-exhausted path reads its step text — the build-develop-prompt.sh exhausted argument, the develop-exhausted launch's VERI_STEP and the step-escalated mark's step — as the open step or, when none is open, the last done step
- [x] Bailing reads its step text — the preserve-attempt.sh step argument and the bail mark's VERI_STEP — as the open step or, when none is open, the last done step
- [x] Stopping's stop mark reads its VERI_STEP as the open step or, when none is open, the last done step
- [x] Resume's resume mark reads its VERI_STEP as the open step or, when none is open, the last done step
