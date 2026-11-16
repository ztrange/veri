# Plan for #3938 — PRD 018.5: VERI_SKIP_VERIFY=pin pins an already-satisfied step without verify-pin

- [x] On a fresh launch with `VERI_SKIP_VERIFY=pin`, `run-conductor.sh` does not exit 2 over that word and writes `pin` to `.tdd/issue-<n>-skip-verify` ⟦criterion 1⟧
- [x] `metrics.sh` counts `verify-pin-skipped reason=switched-off` events as `pin <n>` on the `Verifiers switched off:` line, one `<phase> <n>` pair per phase with at least one switched-off skip, comma-separated ⟦criterion 12⟧
- [x] `comment.sh <n> verify-revised <phase>` posts `### 🔎 verify-<phase> (revised) — SKIPPED (switched off)` when `.tdd/verdict-<phase>.exit` reads `skipped` ⟦criterion 10⟧
- [x] `skills/tdd/JOURNAL.md`'s event table lists `verify-pin-skipped` with its `reason` field (`switched-off`) beside `verify-refactor-skipped` ⟦criterion 14⟧
- [ ] ADR-0033's Consequences bullet reads "PRD 018.1–018.5" ⟦criterion 15⟧
- [ ] skill-edit step for the unit `skills/tdd/PIN.md`: add PN25 and PN26 under `## skills/tdd/PIN.md`, amend the opening section with the switched-off skip and the go-red control exception, grade and sign ⟦skill-edit⟧ ⟦criterion 16⟧
- [ ] skill-edit step for the unit `skills/tdd/REVISE.md`: add RV68 under `## skills/tdd/REVISE.md`, amend step 5 (**Re-verify**), grade and sign ⟦skill-edit⟧ ⟦criterion 17⟧
