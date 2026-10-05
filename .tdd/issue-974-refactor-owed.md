### `build-develop-prompt.sh diff <spec> <step> <test-cmd>` with the fast command left out exits 2 with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧
- test-only | the `"make unit"` fast-command literal repeated across the three diff cases in build-develop-prompt.test.sh could be one variable shared with `dd_fast`
