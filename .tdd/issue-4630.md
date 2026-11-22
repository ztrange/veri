# Plan for #4630 — pin_reject_route.py --recheck routes a pin-recheck 'not checked' reason to revise, spending REVISE_BUDGET on a leaf that cannot edit tests

- [x] `pin-reject-route.sh --recheck` on a reason holding `not checked: <file> (old text in no file of its package)` prints `not-checked <file>`, exits 1, and leaves the ledger and the added record untouched ⟦criterion 1⟧
- [ ] the same for `not checked: <file> (old text in more than one file of its package)` ⟦criterion 2⟧
- [ ] the conductor bails a `not-checked <file>` route with cause `needs-user` naming the pin, to re-record or retire it: SKILL.md Refactor loop, SCRIPTS.md, the shim header and requirement CY123 say so, regraded
