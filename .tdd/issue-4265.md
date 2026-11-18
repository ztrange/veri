# Plan for #4265 — The fixture route and the prep answer bail step-add-refused without judging the exit 2

- [x] `skills/tdd/SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)`: the `fixture` route keeps an `add-ledger-step.sh` exit 2's stderr in `.tdd/add-ledger-step.err` and judges it through `adjudicate-step-add-refused` before it bails `step-add-refused`, new row CY404, regraded ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] `skills/tdd/REVISE.md`'s *The `prep` answer* (and the exhausted step-ahead `prep` that follows it) keeps an `add-ledger-step.sh` exit 2's stderr in `.tdd/add-ledger-step.err` and judges it through `adjudicate-step-add-refused` before it bails `step-add-refused`, row RV70 reworded, regraded ⟦skill-edit⟧ ⟦criterion 2⟧
- [x] `SKILL.md` stays at or under `SKILL_CEILING_3174` ⟦full-suite⟧ ⟦criterion 3⟧
