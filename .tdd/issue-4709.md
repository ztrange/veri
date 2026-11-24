# Plan for #4709 — A Red/Green step whose prose quotes a kind mark (`⟦diff-checked⟧`) is routed to that kind, since red_half.refused tests by substring

- [x] `red_half.refused` returns no kind for a step that only quotes a `red_half.REFUSED` mark in backticked prose, and still returns it from the step's trailing marker run, one case per mark ⟦criterion 1⟧
- [x] `run-step.sh` routes a step that only quotes `⟦diff-checked⟧` in its prose to `red-half.sh`, not `diff-step.sh` ⟦criterion 2⟧
- [x] `red_half.refused` and `ledger.ledger_steps` agree on the kind of every step of a fixture ledger mixing quoted and trailing marks ⟦criterion 3⟧
- [x] `ledger.has_kind`, one shared helper, reads a kind mark from a step's trailing marker run plus exactly two leading forms (a leading `⟦skill-edit⟧`, and a step starting `ledger.REPIN_STEP` for `⟦diff-checked⟧`); `red_half.refused` reads through it, so a step that only starts with another REFUSED mark gets no kind ⟦criterion 1⟧
- [x] `run_step`, `green_half`, `step_tick`, `verify_branch`, `suite_red_resume`, `diff_step` and `pr_checks` read kind marks through `ledger.has_kind`, so a mark only quoted in a step's prose counts for none of them, one case per reader ⟦criterion 2⟧
- [x] the mixed fixture ledger holds a step starting `ledger.REPIN_STEP`, and `ledger.ledger_steps` and `red_half.refused` agree on its kind ⟦criterion 3⟧
- [x] `ledger_growth` (the skill-edit check of `change` and `counted_steps`), `prose_owed.waive`, `scope_check.skill_edit_refused` and `add_ledger_step`'s bare diff-checked refusal read kind marks through `ledger.has_kind`, so a mark only quoted in a step's prose counts for none of them, one case per site ⟦criterion 2⟧
- [ ] `diff_step.run`'s open-step guard and `build_verify_prompt`'s green paragraphs read kind marks through `ledger.has_kind`, so a step only quoting `⟦diff-checked⟧` or `⟦fixture-repair⟧` in its prose is not of that kind, one case per site ⟦criterion 2⟧
