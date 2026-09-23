# Plan for #431 — An apostrophe in a step title still breaks every launch line: #426 removed the nested bash -c, not the outer single quotes

- [x] A step title containing an apostrophe reaches a leaf intact through the documented launch mechanism, with no hand-written wrapper ⟦criterion 1⟧
- [x] SKILL.md states the step-title rule in one place and every documented launch line follows it ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The guard fails naming file and line when a SKILL.md launch line inlines an unescaped step title, against an exemption table carrying a reason per entry ⟦criterion 3⟧
