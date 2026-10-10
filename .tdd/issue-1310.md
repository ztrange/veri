# Plan for #1310 — PRD 009 C3-2: a production-frozen check for contract (a), and a no-product-caller check that gates contract

- [x] Given a base sha, the production-frozen check exits 1 and names each path changed in `<base>..HEAD` that is not a test file by `transform-touches-tests.sh`'s rule ⟦criterion 1⟧
- [x] The production-frozen check exits 0, printing no path, when every path changed in `<base>..HEAD` is a test file by that same rule (under a `tests/` directory or named `*.test.*`) ⟦criterion 1⟧
- [x] The production-frozen check exits 2 when the base does not resolve to a commit ⟦criterion 1⟧
- [x] Given an old script interface `<name>.sh`, the no-product-caller check exits 1 printing `file:line` for a line in `skills/tdd/SKILL.md` that names it ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The no-product-caller check also reports `file:line` for a line naming the interface in `skills/tdd-fix/SKILL.md`, `skills/tdd-candidates/SKILL.md`, the `Makefile`, a file under `docs/hooks/` and a file under `skills/tdd/scripts/veri/` ⟦criterion 2⟧
- [ ] The no-product-caller check exits 0, printing nothing, when no line of those product files names the interface ⟦criterion 2⟧
- [ ] The no-product-caller check does not report a line under any `tests/` directory that names the interface ⟦criterion 2⟧
- [ ] Given an old module-function interface `<module>.<function>`, the no-product-caller check reports a product line naming it and does not report its own definition (`def <function>` in `skills/tdd/scripts/veri/<module>.py`) ⟦criterion 2⟧
