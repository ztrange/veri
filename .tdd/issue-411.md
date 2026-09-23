# Plan for #411 — skill-refactor-pending.test.sh: the clear-refactor-pending.sh 'names a removal verb' probe is satisfied by the script's own filename, so it cannot fail

- [ ] the removal-verb probe reports a problem naming the clear-refactor-pending.sh entry when that entry names no removal verb in prose though the filename supplies one ⟦criterion 1⟧
- [ ] against SKILL.md as committed the removal-verb probe reports no problem, so a true entry stays green ⟦criterion 2⟧
- [ ] every other probe of the script reference list case still reports its problem when the entry it reads carries none of what it asks for ⟦criterion 3⟧
