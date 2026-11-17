# Plan for #4025 — PRD 027.3: planning's fixed tail is one call

- [x] `plan-publish.sh <n> <title-file>` follows the port convention: usage and exit 2 with no argument, a missing preflight file, ledger or title file exit 2 before any inner call ⟦criterion 14⟧
- [x] it runs the scope check, the tree-checked plan commit, the push, the draft PR when none exists, and the plan and start comments, in order, each printed, stopping at the first unclean call ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 11⟧ ⟦criterion 12⟧ ⟦criterion 13⟧
- [x] it refreshes the spec, launches `verdict-plan` under the stop check, waits, comments on a PASS and settles `.tdd/issue-<n>-plan-publish` ⟦criterion 5⟧ ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 10⟧
- [ ] called again after an exit 3 it repeats nothing but the wait, and its wait record names its conductor ⟦criterion 8⟧ ⟦criterion 9⟧
- [ ] a guard fails when an inner call is a `$S/` script `SKILL.md` steps 2, 2b and 2c do not name ⟦criterion 15⟧ ⟦criterion 16⟧
- [ ] docs: `SKILL.md` step 2, `SCRIPTS.md`, rows and grades ⟦criterion 17⟧
