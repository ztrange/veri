# Plan for #3936 — PRD 018.3: VERI_SKIP_VERIFY=red skips verify-red, prediction gate and frozen record kept

- [ ] On a fresh launch with `VERI_SKIP_VERIFY=red`, `run-conductor.sh` does not exit 2 over that word and pins it; a word it still cannot skip (`diff`; `pin` landed with #3938) still exits 2, naming it ⟦criterion 1⟧
- [ ] `comment.sh <n> verify-red` posts `### 🔎 verify-red — SKIPPED (switched off)` when `.tdd/verdict-red.exit` reads `skipped`, never `PASS`, and `verify-revised red` posts its revised SKIPPED heading ⟦criterion 6⟧
- [ ] `metrics.sh` counts `verify-red-skipped reason=switched-off` events as `red <n>` on the `Verifiers switched off:` line, one `<phase> <n>` pair per phase, comma-separated ⟦criterion 12⟧
- [ ] `skills/tdd/JOURNAL.md`'s event table lists `verify-red-skipped` with its `reason` field (`switched-off`) beside `verify-refactor-skipped` ⟦criterion 13⟧
- [ ] skill-edit step for the unit `skills/tdd/SKILL.md`: add CY150 and CY151 under `## skills/tdd/SKILL.md`, amend *Red* sub-step 2 and *Green* sub-step 1 within the byte ceiling, grade and sign ⟦skill-edit⟧ ⟦criterion 14⟧
- [ ] skill-edit step for the unit `skills/tdd/REVISE.md`: check RV68 and RV69 against step 5 with `red` skippable, name `verify-red-skipped`, grade and sign ⟦skill-edit⟧ ⟦criterion 15⟧
