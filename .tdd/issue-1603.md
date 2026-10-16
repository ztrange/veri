# Plan for #1603 — verify.sh exits 2 after a green PASS when the step text names the replaces-case mark without a replaces clause

- [x] replaces_case.parse, given a step text that names the replaces-case mark but carries no replaces clause with a quoted case, returns None instead of raising AttributeError ⟦criterion 2⟧
- [x] verify.sh green, run with --step text that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 1⟧
- [ ] unreplaced-cases.sh, given a step that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, exits 0 and prints no case name, not exit 2 with a traceback ⟦criterion 3⟧
- [ ] replaces_case.parse, given a step with a quoted replaces clause naming a case but no in-suite-path clause after it, does not raise ⟦criterion 4⟧
- [ ] verify.sh green, run with --step text carrying a quoted replaces clause naming a case but no in-suite-path clause after it, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 4⟧
