# Plan for #3037 — wrong-test-route routes to a fixture only when it is defined in the step's own test file

- [x] wrong-test-route.sh prints no `fixture` route when a name in the `WRONG_TEST:` line matches `def <name>(` only in a test file other than the step's own test file (the file holding the step's Red case), so the router falls through to `repair <the step's own case>` or `revise` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] wrong-test-route.sh still prints `fixture <that file> <name>` when the named helper is defined in the step's own test file (the file holding the step's Red case), even when an unrelated test file also defines `def <name>(` ⟦criterion 2⟧
