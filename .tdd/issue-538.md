# Plan for #538 — affected-suites.sh: touching SKILL.md selects only the suites that check what the changed section prescribes

- [x] A range whose changed lines of skills/tdd/SKILL.md all lie inside one ## section selects the suites naming SKILL.md that read that section, and not a suite naming SKILL.md that reads only a different section ⟦criterion 1⟧
- [x] A range whose changed lines of skills/tdd/SKILL.md all lie inside one ## section still selects a suite that names SKILL.md and reads it without slicing it to any section ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A range whose changed lines of skills/tdd/SKILL.md all lie inside one ### subsection selects the suites reading that ### subsection and the suites reading the ## section enclosing it, and not a suite reading only a sibling section ⟦criterion 1⟧
- [ ] The working-tree form (no ".." in the argument) narrows an uncommitted edit lying inside one section of skills/tdd/SKILL.md the same way the range form does ⟦criterion 1⟧
- [ ] An edit to skills/tdd/SKILL.md that changes a ## or ### heading line selects every suite that names SKILL.md ⟦criterion 1⟧
- [ ] An edit to skills/tdd/SKILL.md whose changed lines span two sections selects every suite that names SKILL.md ⟦criterion 1⟧
- [ ] An edit to skills/tdd/SKILL.md that cannot be placed in a section (a changed line above the first ## heading, or a file added or deleted whole) selects every suite that names SKILL.md ⟦criterion 1⟧
- [ ] A change to CLAUDE.md, Makefile, a SKILL.md other than skills/tdd/SKILL.md, or a prompt under prompts/*.md selects the same suites it selected before this issue, file-wide ⟦criterion 2⟧
- [ ] The branch's diff deletes no suite naming skills/tdd/SKILL.md and leaves the Makefile's test recipe unchanged, so make test still runs every SKILL.md suite ⟦diff-checked⟧ ⟦criterion 2⟧
