# Plan for #4630 — pin_reject_route.py --recheck routes a pin-recheck 'not checked' reason to revise, spending REVISE_BUDGET on a leaf that cannot edit tests

- [x] `pin-reject-route.sh --recheck` on a reason holding `not checked: <file> (old text in no file of its package)` prints `not-checked <file>`, exits 1, and leaves the ledger and the added record untouched ⟦criterion 1⟧
- [x] the same for `not checked: <file> (old text in more than one file of its package)` ⟦criterion 2⟧
- [x] `pin-reject-route.sh --recheck` on a reason with neither a `pin stayed green` nor a `not checked` line prints `revise-impossible`, exits 1, ledger untouched, when no `.tdd/issue-<n>-refactor-half-rejected-wait` record names the matched step (a step-close recheck, verify-refactor passed or skipped), since `revise.sh <n> refactor` exits 2 without that record; with such a record it still prints `revise`
- [ ] the conductor bails a `not-checked <file>` route with cause `needs-user` naming the pin, to re-record or retire it, and a `revise-impossible` route with cause `revise-impossible`: SKILL.md Refactor loop, SCRIPTS.md, the shim header and requirement CY123 say so, regraded
