# Plan for #3171 — /vgroom sets a missing GitHub parent on PRD children

- [x] skill-edit step for the unit `skills/vgroom/SKILL.md`: during triage `/vgroom` finds every open or closed issue titled `PRD <nnn>.<k>: …` with no GitHub parent, sets its parent to the issue titled `PRD <nnn>: …` through the sub-issues API and reports each one it set, reports and leaves an issue whose parent is a different issue, and reports a PRD number with no PRD issue and sets nothing, meeting requirement GR12 ⟦skill-edit⟧ ⟦criterion 1⟧
