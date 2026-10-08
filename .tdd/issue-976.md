# Plan for #976 — SKILL.md: a resumed ⟦diff-checked⟧ step's verify-diff uses the step base from before the killed attempt's commit

- [x] SKILL.md states that a ⟦diff-checked⟧ step's step base sha, on a fresh run and on a resume alike, is the last commit that changed the ledger (git log -1 --format=%H -- .tdd/issue-<n>.md), never a HEAD taken after a killed attempt's commit — pinned by a text case in a skill-*.test.sh suite that goes red against today's text ⟦criterion 1⟧ ⟂ refactor pending
