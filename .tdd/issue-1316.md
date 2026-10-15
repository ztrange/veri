# Plan for #1316 — PRD 009 C6-0: pytest prose tests read SKILL.md through one shared section helper, and affected-suites.sh selects them by section

- [x] A shared helper under tests/py/ returns, from a given SKILL.md, the text of the `##` or `###` section a pytest test names by its heading — that section only, ending where the next heading of the same or a higher level starts ⟦criterion 1⟧
- [x] The shared section helper fails the calling test, with a message naming the heading, when the given SKILL.md has no such heading, and never returns the whole file in its place ⟦criterion 1⟧
- [ ] Given a git range whose only change is inside one `##` section of skills/tdd/SKILL.md, affected-suites.sh prints the pytest files under tests/py/ that read that section through the shared helper, and does not print those that read only other sections through it ⟦criterion 2⟧
- [ ] Given a git range whose only change is inside one `##` section of skills/tdd/SKILL.md, affected-suites.sh prints a pytest file under tests/py/ that reads SKILL.md without the shared helper ⟦criterion 2⟧
