# Plan for #3935 — PRD 018.2: VERI_SKIP_VERIFY=green skips verify-green, its mechanical checks still running

- [x] On a fresh launch with `VERI_SKIP_VERIFY=green` (alone, or with `refactor`), `run-conductor.sh` does not exit 2 over that word and writes the list to `.tdd/issue-<n>-skip-verify`; a word it still cannot skip (`red`) still exits 2, naming it ⟦criterion 1⟧
- [x] `comment.sh <n> verify-green` posts `### 🔎 verify-green — SKIPPED (switched off)` when `.tdd/verdict-green.exit` reads `skipped`, never `PASS` ⟦criterion 5⟧
- [x] `metrics.sh` counts `verify-green-skipped reason=switched-off` events as `green <n>` on the `Verifiers switched off:` line, one `<phase> <n>` pair per phase, comma-separated ⟦criterion 12⟧
- [x] `skills/tdd/JOURNAL.md`'s event table lists `verify-green-skipped` with its `reason` field (`switched-off`) beside `verify-refactor-skipped` ⟦criterion 14⟧
- [ ] ADR-0033's Consequences say only the routes read from a verify-green reason (`missing`, `later`) are lost, and that `mutation-parity.sh` keeps running ⟦criterion 15⟧
- [ ] skill-edit step for the unit `skills/tdd/SKILL.md`: add CY148 and CY149 under `## skills/tdd/SKILL.md`, amend *Green* sub-steps 1 and 2 within the byte ceiling, grade and sign ⟦skill-edit⟧ ⟦criterion 16⟧
- [ ] skill-edit step for the unit `skills/tdd/REVISE.md`: check RV68 against step 5 with `green` skippable, add RV69 stating the skip event's command form, grade and sign ⟦skill-edit⟧ ⟦criterion 17⟧
- [ ] skill-edit step for the unit `skills/tdd/SCRIPTS.md`: add the issue's SC143 row as SC145, amend the `$S/metrics.sh` and `$S/comment.sh` entries, grade and sign ⟦skill-edit⟧ ⟦criterion 18⟧
