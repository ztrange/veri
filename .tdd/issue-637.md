# Plan for #637 — skill-leaf-env.test.sh builds a stage by linking the scripts, not by copying all 69 per launch line

- [x] stage_recorder copies no script: every script a stage does not replace is reached by a link to the script under test, never by cp ⟦criterion 1⟧
- [x] each distinct recorder stub (the detach-leaf.sh recorder and every stage_title_recorders stub) is written once per suite run and a stage reaches it by link, the per-stage difference coming only from $SEEN in the environment ⟦criterion 2⟧
- [x] a recorder replaces a stage's link rather than writing through it, so running skill-leaf-env.test.sh leaves every script under skills/tdd/scripts byte-identical and git status clean ⟦criterion 3⟧
- [ ] the suite still pins, for every SKILL.md launch line, the environment each leaf launch receives (VERI_STEP and --step included), and was watched going red on a planted SKILL.md whose launch line drops a pinned variable, then put back ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] no case is removed and no case's name or assertion changes: skill-leaf-env.test.sh ends on the same count line as before and the full suite is green ⟦full-suite⟧ ⟦criterion 5⟧
