# Plan for #4384 — PRD 037.6: prose-owed.sh refuses a prompt file with no rows

- [x] `prose-owed.sh <root>` prints `skills/tdd/scripts/prompts/<file> (no rows)` and exits 1 for a prompt file no tracked `REQUIREMENTS.md` lists ⟦criterion 1⟧
- [x] `prose-owed.sh <root>` adds nothing for a repository with no `skills/tdd/scripts/prompts/` directory ⟦criterion 2⟧
- [ ] `prose-owed.sh <root>` adds nothing for `skills/tdd/scripts/prompts/REQUIREMENTS.md` itself ⟦criterion 2⟧
- [ ] the rowless-fragment case goes red with the scan broken on purpose, then the break is restored ⟦criterion 3⟧
- [ ] `CLAUDE.md` `## Graded prose` and the `skills/tdd/SCRIPTS.md` `prose-owed.sh` entry say so, rows CM304 and SC583 added and graded, `prose-owed.sh` exits 0 ⟦criterion 4⟧
