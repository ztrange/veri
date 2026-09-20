# Plan for #305 — run-conductor.test.sh reads ambient VERI_NEW_SKILL/VERI_SKILL_COMMIT, so every make test inside a re-pinned run is red

- [ ] run-conductor.test.sh is green when VERI_NEW_SKILL=1 and VERI_SKILL_COMMIT=<any sha> are set in the ambient environment ⟦criterion 1⟧
- [ ] hermetic-suites.test.sh fails, naming the suite, when a suite's answer changes with an ambient VERI_SKILL_COMMIT ⟦criterion 2⟧
