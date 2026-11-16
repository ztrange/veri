# Plan for #3934 — PRD 018.7: a resumed run skips verify-refactor when the run pinned it off

- [x] On a resume (a readable `.tdd/issue-<n>-skill-commit`, `VERI_NEW_SKILL` unset) with `refactor` pinned in `.tdd/issue-<n>-skip-verify` and `VERI_SKIP_VERIFY` unset, `run-conductor.sh` leaves the pin reading `refactor`, so the resumed conductor still skips verify-refactor ⟦criterion 3⟧
- [x] On a resume with an empty `.tdd/issue-<n>-skip-verify` and `VERI_SKIP_VERIFY=refactor`, `run-conductor.sh` leaves the pin empty, so the resumed conductor still launches verify-refactor ⟦criterion 3⟧
- [ ] skill-edit step for the unit `skills/tdd/RESUME.md`: reword RS20 and add RS38 under `## skills/tdd/RESUME.md`, amend sub-step 2 at "Run its **verify-refactor** after it" to take the cycle loop's *Refactor loop* step 5 **Switched off** branch when `refactor` is pinned, grade and sign ⟦skill-edit⟧ ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 4⟧
