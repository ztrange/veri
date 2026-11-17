# Plan for #4102 — PRD 026.5: `vcoord` is removed and every unit speaks of one role

- [x] `skills/vcoord/` is removed from the tree ⟦criterion 1⟧
- [x] `install-links.sh` removes an existing `.claude/skills/vcoord` link, prints `removed vcoord`, links the rest ⟦criterion 2⟧
- [x] a guard case fails on `vcoord`/`coordinator` outside specs, docs/adr, .tdd, skills/tdd, but the README install sentence ⟦criterion 8⟧
- [x] the guard is watched red on `coordinator` in a skill file and `vcoord` in another README sentence ⟦criterion 9⟧
- [x] README's `/vinstall` paragraph names `LINKED` and lists `vcoord` among the removed links; README regraded ⟦criterion 3⟧
- [x] `skills/vdev/SKILL.md` names no coordinator; regraded ⟦criterion 4⟧
- [x] `operator/PRINCIPLES.md` names one operator role; regraded ⟦criterion 5⟧
- [x] vmerge, vfile, vbail, vplan, vreport, vjudge name `vdev` or the human; each changed unit regraded ⟦criterion 6⟧
- [x] `skills/vhandoff/` names no coordinator nor a `coord` argument; regraded ⟦criterion 7⟧
- [x] voutage names no coordinator; regraded
