# Plan for #1603 — verify.sh exits 2 after a green PASS when the step text names the replaces-case mark without a replaces clause

- [x] replaces_case.parse, given a step text that names the replaces-case mark but carries no replaces clause with a quoted case, returns None instead of raising AttributeError ⟦criterion 2⟧
- [x] verify.sh green, run with --step text that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 1⟧
