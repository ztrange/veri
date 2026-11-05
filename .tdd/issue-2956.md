# Plan for #2956 — REQUIREMENTS.md PF7 says a red full tier stops the run, though its wait carries `--alone`

- [ ] Requirement row PF7 of skills/tdd/PREFLIGHT.md states the alone-rerun exception for a red full tier (stops the run unless every red test file passes alone, as for the baseline in PF4: a flake with a `suite-flake` event; a red output naming no file or any file still red alone stops it), the rest of the row unchanged, and grade-prose.sh passes the unit ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] skills/tdd/GRADED carries a regraded entry for skills/tdd/PREFLIGHT.md, the repo's GRADED-signature case staying green ⟦full-suite⟧ ⟦criterion 2⟧
