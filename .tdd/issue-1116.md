# Plan for #1116 — A ledger step carrying two ⟦criterion k⟧ tags is refused, exit 2, rather than silently serving only the first

- [x] criterion-finished.sh <k>, for any k, on a ledger in which any step line carries two criterion tags exits 2 with a stderr line naming that step's text and saying one step serves one criterion, while ledgers with at most one tag per step keep their exit codes ⟦criterion 1⟧ ⟂ refactor pending
- [ ] add-ledger-step.sh on a ledger in which any step line carries two criterion tags — the anchor or another step — exits 2 with a stderr line naming that step's text and saying one step serves one criterion, and leaves the ledger file byte-for-byte unchanged ⟦criterion 1⟧
- [ ] the two-tag case is watched to fail on today's code before the fix lands — criterion-finished.sh 2 exits 3 and criterion-finished.sh 1 exits 0 there — recorded from the first step's Red failing output ⟦human-owed⟧ ⟦criterion 2⟧
