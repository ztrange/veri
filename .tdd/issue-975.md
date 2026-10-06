# Plan for #975 — SKILL.md's Draft PR step: the branch's own full run comes before the rebase, a red rebased tip gets its own bail cause, and the branch is reset before that bail's push

- [x] classify-bail.sh rebased-tip-red prints process and exits 0, pinned in tests/py/test_classify_bail.py ⟦criterion 1⟧
- [x] SKILL.md's Draft PR step says the branch's own full run, and any ⟦suite-repair⟧ step it adds, finishes green before rebase-onto-default.sh runs ⟦criterion 2⟧
- [x] SKILL.md's Draft PR step no longer calls the branch's own full run the only full-suite run: the rebased-tip run is named as the extra run a rebase owes, not a replacement for it
- [ ] SKILL.md's bail on a red rebased tip, after a clean rebase and after a verified conflict resolution alike, names cause rebased-tip-red, not suite-red ⟦criterion 3⟧
- [ ] SKILL.md's bail on a red rebased tip runs git reset --hard <pre-rebase-sha> before Bailing's push ⟦criterion 3⟧
- [ ] Bailing's cause-token list names rebased-tip-red and classifies it as a process failure ⟦criterion 4⟧
