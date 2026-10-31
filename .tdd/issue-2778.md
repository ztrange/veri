# Plan for #2778 — vstatus: show times in the machine's local zone, keep stored state UTC

- [x] skills/veri-status/SKILL.md satisfies A8, every time shown is local and the report's first line names the zone once, graded PASS ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] skills/veri-status/SKILL.md satisfies A9, .tdd/status-last stays UTC ISO 8601 and the merged:>= search uses that value, graded PASS ⟦skill-edit⟧ ⟦criterion 2⟧
- [ ] skills/veri-status/SKILL.md satisfies A10, every source is converted to the same local zone and two zones never appear side by side, graded PASS ⟦skill-edit⟧ ⟦criterion 3⟧
