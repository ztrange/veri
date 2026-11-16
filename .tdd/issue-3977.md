# Plan for #3977 — PRD 022.4: selection refuses an issue a stranger wrote

- [x] `github.trusted_author` says whether a REST record's `author_association` is one of the given set; `trusted_comment` decides through it
- [x] `solvable_issues.select` keeps an issue only when its author is `OWNER`, `MEMBER` or `COLLABORATOR`; today's fixtures gain `author_association: "OWNER"` ⟦criterion 1⟧ ⟦criterion 8⟧
- [ ] `VERI_AUTHOR_LABEL` (default `author-read`) takes a stranger's issue once read; set-but-empty is exit 2 ⟦criterion 2⟧
- [ ] a refused issue labelled `priority` and `bug` is not printed and the rest print in today's order ⟦criterion 3⟧
- [ ] a refused open issue still blocks the issues it names ⟦criterion 4⟧
- [ ] each opted-in issue the author rule alone removes gets one stderr skip line ⟦criterion 5⟧
- [ ] a record with no `author_association` is refused as `unknown` unless it carries the override label ⟦criterion 6⟧
- [ ] every otherwise-solvable issue refused exits 3 with empty stdout ⟦criterion 7⟧
- [ ] a ratchet: every module of veri/ listing issues to take decides their author through `github.trusted_author`
- [ ] the `solvable-issues.sh` entry of SCRIPTS.md states the author rule, `VERI_AUTHOR_LABEL` and the skip line ⟦criterion 9⟧
- [ ] the root CLAUDE.md's selection invariant adds the author rule to the filters before the bands ⟦criterion 10⟧
