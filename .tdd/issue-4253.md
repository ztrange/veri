# Plan for #4253 — PRD 026.10: recovery asks a question whose session never opened and acts on an answer it has not acted on

- [ ] status.sh --recover prints `Unasked questions` and `Answered questions` after `Questions`, `none` when empty ⟦criterion 1⟧
- [ ] each lane question file is listed in exactly one of Questions (## Asked, no ## Answer, or unreadable), Unasked questions (neither line) and Answered questions (## Answer) ⟦criterion 2⟧
- [ ] vdev SKILL.md step 3 appends `## Asked <session-id>` before the notification; step 1 tells asked from written-never-asked ⟦criterion 3⟧
- [ ] vdev SKILL.md *Answers* and *Recovery* act on the three recovery sections ⟦criterion 4⟧
- [ ] SCRIPTS.md status.sh entry names the two sections and the sorting rule ⟦criterion 5⟧
