# Plan for #3750 — /vinstall links only the six skills the operator types; the rest are read on demand

- [x] install-links.sh on a fresh repository links exactly vcoord vdev vfile vgroom vhandoff vplan and lists exactly those six in .git/info/exclude ⟦criterion 1⟧
- [x] install-links.sh removes veri links to vready vreport vstatus vstop, names each on stdout, and drops their exclude lines ⟦criterion 2⟧
- [x] install-links.sh leaves untouched a .claude/skills entry that is not a symlink into veri's skills/ directory, whatever its name ⟦criterion 3⟧
- [x] each linked skill's .on-demand marker says /vinstall links it, and vready vreport vstatus vstop markers say they are not linked and are read by path when wanted ⟦added⟧ ⟦criterion 1⟧
- [x] skills/vinstall/SKILL.md reports linked, repaired or removed skills and loads vready by path, graded by VI1<reword> and VI4<reword> ⟦criterion 4⟧
- [ ] README's Install section names the six linked skills and says the rest are read on demand by path ⟦criterion 5⟧
