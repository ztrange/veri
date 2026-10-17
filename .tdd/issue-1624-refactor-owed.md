### `ledger-steps.sh has-mark ''` given an empty mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧
- test-only | the two `has-mark` tests in `test_ledger_steps.py` (no name, empty name) repeat the same fake_stdin / assert block and could be one parametrized case
