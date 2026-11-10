# Plan for #3543 — wrong-test-route counts backticked non-case values in a WRONG_TEST line as named cases, so a repair routes revise

- [x] A `WRONG_TEST:` line that backticks a defined test case other than the step's own red case, beside backticked non-case values, still routes as it does today (the resolving case is honoured, not dropped as prose) ⟦criterion 1⟧
- [x] A `WRONG_TEST:` line whose only backticked or quoted spans are values that resolve to no defined test case (such as `zq7marker` and `command`), and which names no case, routes `repair <own red case>` and not `revise` ⟦criterion 1⟧
