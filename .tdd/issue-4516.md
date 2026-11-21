# Plan for #4516 — PRD 042.3: the budgets invariant becomes a table

- [x] `CLAUDE.md`'s budgets invariant is one count sentence and a knob/axis/default table whose knob set and defaults match `tunables.py`, pinned by a unit case ⟦criterion 1⟧
- [x] the root `REQUIREMENTS.md` rows CM35–CM39, CM83, CM176, CM250 and CM300 are rewritten as the issue gives them and its `CM<next>` row is added as CM310 ⟦criterion 3⟧
- [ ] ⟦skill-edit⟧ `CLAUDE.md` is graded PASS against its rewritten rows: no "never folded" sentence, ADR-0020's reason and the preflight check stated once, each budget's own-axis reason in its row, and `prose-owed.sh .` exits 0 ⟦criterion 2⟧
- [ ] the Commands table and every `veri:` line of `CLAUDE.md` are byte-identical to the branch base's, and `test_claude_md_commands.py` passes ⟦criterion 4⟧
- [ ] `wc -c CLAUDE.md` is below the branch base's 19576 ⟦criterion 5⟧
