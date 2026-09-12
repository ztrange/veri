# Plan for #105 — Rename the skill to /tdd: /tdd <n> solves one issue, /tdd [<scope>] drains a scope

- [x] the skill directory is skills/tdd/ and its frontmatter reads name: tdd
- [x] every path constant in the build and test plumbing spells skills/tdd, so make test is green on the new path with no skills/solve-issue/scripts reference left outside the two stubs
- [x] make docs-check is green on the new path, the walkthrough regenerated from skills/tdd/scripts
- [x] skills/solve-issue/SKILL.md and skills/solve-issues/SKILL.md remain as stubs whose body forwards the same arguments to /tdd
- [x] no file outside those two stubs mentions /solve-issue or /solve-issues except to describe the stubs
- [ ] skills/tdd/SKILL.md resolves its argument — an integer is the single-issue procedure, any other word is a scope, bare /tdd is /tdd plain — with the loop procedure folded in and no ../solve-issue/scripts sibling coupling left
- [ ] the scope's selection label is ready-for-agent for scope plain and ready-for-agent:<scope> otherwise, with VERI_LABEL still overriding it
- [ ] the committed docs/walkthrough.html matches a fresh build, so make docs-check is green end to end
