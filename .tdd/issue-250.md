# Plan for #250 — SKILL.md's refactor event mark collapses refactor-triage.sh's two real answers into one stopped=triage value

- [x] SKILL.md's Refactor phase records stopped=nothing-structural for refactor-triage.sh exit 3 and stopped=structural-owed for exit 0, with no stopped=triage left, while stopped=malformed, stopped=nothing-left and stopped=budget stay unchanged ⟂ refactor pending
- [ ] A metrics.test.sh case feeds two refactor marks, one stopped=nothing-structural and one stopped=structural-owed, and asserts each step's row shows its own value
