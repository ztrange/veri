# Plan for #1624 — ledger-steps.sh has-mark with no name crashes instead of exiting 2

- [x] `ledger-steps.sh has-mark` given no mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧
- [x] `ledger-steps.sh has-mark ''` given an empty mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ ⟂ refactor pending
- [ ] the usage line `ledger-steps.sh` prints on a bad argument lists every verb the script accepts: current, last-done, current-or-last-done, next-phase, criterion <k> and has-mark <name> ⟦criterion 1⟧
