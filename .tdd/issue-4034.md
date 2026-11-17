# Plan for #4034 — PRD 027.12: the done comment is one call

- [x] `run-done.sh <n>` follows the port convention and refuses no argument and a missing preflight with exit 2 before any inner call ⟦criterion 8⟧
- [x] it asks `stop-requested.sh`, checks the tree, posts `comment.sh <n> done`, clears a reported stop request and settles, never merging and stopping at the first call that is not clean ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧ ⟦criterion 6⟧ ⟦criterion 7⟧
- [x] a guard fails when an inner call is a `$S/` script sub-step 4 does not name, and the done comment is posted and the stop request cleared for real against a stub `gh` ⟦criterion 9⟧
- [ ] docs: `DRAFT-PR.md` sub-step 4, `SCRIPTS.md`, rows and grades ⟦criterion 10⟧
