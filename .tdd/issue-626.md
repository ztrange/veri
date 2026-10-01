# Plan for #626 — the bail procedure renders metrics before it marks the bail, so a literal run's bail metrics say Outcome: unknown

- [x] a suite fails when SKILL.md's *Bailing* procedure has its metrics render step (`metrics.sh <n> > .tdd/issue-<n>-metrics.md`) before its `event.sh bail` step ⟦criterion 2⟧
- [ ] the `event.sh bail` step that SKILL.md's *Bailing* procedure runs before rendering the metrics carries the bail's `cause=` and `classification=`, so the metrics committed and posted on a bail name the bail as the run's ending ⟦criterion 1⟧
