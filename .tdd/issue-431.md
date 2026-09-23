# Plan for #431 — An apostrophe in a step title still breaks every launch line: #426 removed the nested bash -c, not the outer single quotes

- [x] A step title containing an apostrophe reaches a leaf intact through the documented launch mechanism, with no hand-written wrapper ⟦criterion 1⟧
- [x] SKILL.md states the step-title rule in one place and every documented launch line follows it ⟦criterion 2⟧
- [ ] Every documented command line carrying text taken from the step's title follows the step-title rule — including the four lines that pass a fragment of it, tick-ledger.sh and clear-refactor-pending.sh and tick-issue-criterion.sh — and a test fails the run naming a line that single-quotes one ⟦added⟧ ⟦criterion 2⟧
- [ ] The guard fails naming file and line when a SKILL.md launch line inlines an unescaped step title, against an exemption table carrying a reason per entry ⟦criterion 3⟧
