# Plan for #386 — stop-requested.sh: the conductor reads a stop request from .tdd/stop

- [x] stop-requested.sh prints the mode on stdout and exits 0 when .tdd/stop holds at-ledger, at-leaf or now ⟦criterion 1⟧ ⟂ refactor pending
- [ ] stop-requested.sh prints nothing and exits 3 when there is no .tdd/stop ⟦criterion 2⟧
- [ ] stop-requested.sh exits 2 with nothing on stdout and a diagnostic on stderr when .tdd/stop's first line is an unknown word or empty ⟦criterion 3⟧
- [ ] stop-requested.sh --clear removes .tdd/stop and exits 0, and exits 0 when there was no file to remove ⟦criterion 4⟧
- [ ] stop-requested.sh given any other argument exits 2 and leaves .tdd/stop as it was ⟦criterion 5⟧
- [ ] the stop-requested suite runs in the fast tier from tests/unit/ and its header states the bar it clears ⟦criterion 6⟧
