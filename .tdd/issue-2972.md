# Plan for #2972 — A step is ticked only after its pin-recheck exits 0

- [x] `pin-recheck.sh <base-sha>` exiting 0 or 3 leaves a receipt `.tdd/pin-recheck-ok` (relative to the working directory it runs in) holding the HEAD sha (`git rev-parse HEAD`) on one line ⟦criterion 1⟧
- [x] `pin-recheck.sh <base-sha>` exiting 1 or 2 leaves no `.tdd/pin-recheck-ok`: a receipt an earlier run left is removed at the start of every run, before any record is read ⟦criterion 1⟧
- [x] Every existing case that expects `clear-refactor-pending.sh` (or `veri/clear_refactor_pending.py`) to clear a mark, or `tick-ledger.sh` (or `veri/tick_ledger.py`) to tick a `⟦diff-checked⟧` step, first leaves a valid receipt: a `pin-recheck-ok` file in the ledger's own directory holding a sha, with HEAD answering that sha and no path changed since it (in-process cases fake the git boundary, `veri/git.py`'s `git()`; process cases use a real repository); no production change, every such case still passing ⟦diff-checked⟧
- [ ] `clear-refactor-pending.sh`, when it would clear a step's mark and the receipt `pin-recheck-ok` in the ledger's directory (`.tdd/pin-recheck-ok` for `.tdd/issue-<n>.md`) is absent, exits 2 with a stderr message naming `pin-recheck.sh` and leaves the ledger byte-identical ⟦criterion 2⟧
- [ ] `clear-refactor-pending.sh` with no receipt present and a matcher no marked step matches still exits 3, leaving the ledger byte-identical ⟦criterion 2⟧
- [ ] `clear-refactor-pending.sh`, when it would clear a mark and a path outside `.tdd/` differs between the receipt's sha and HEAD, exits 2 with a stderr message naming `pin-recheck.sh` and leaves the ledger byte-identical ⟦criterion 2⟧
- [ ] `clear-refactor-pending.sh` clears the mark, exit 0, when the only paths differing between the receipt's sha and HEAD are under `.tdd/` ⟦criterion 2⟧
- [ ] `clear-refactor-pending.sh` refuses, exit 2 naming `pin-recheck.sh` with the ledger byte-identical, a receipt whose sha git cannot resolve ⟦criterion 2⟧
- [ ] With a valid receipt (its sha equal to HEAD) `clear-refactor-pending.sh` clears the mark as today, exit 0, leaving every other ledger line unchanged ⟦criterion 2⟧
- [ ] `tick-ledger.sh` ticking a `⟦diff-checked⟧` step with the receipt absent exits 2 with a stderr message naming `pin-recheck.sh` and leaves the ledger byte-identical ⟦criterion 3⟧
- [ ] `tick-ledger.sh` ticking a `⟦diff-checked⟧` step when a path outside `.tdd/` differs between the receipt's sha and HEAD exits 2 naming `pin-recheck.sh` and leaves the ledger byte-identical ⟦criterion 3⟧
- [ ] `tick-ledger.sh` ticks of steps not marked `⟦diff-checked⟧` (a plain tick, `--refactor-pending`, `--phase`) succeed with no receipt present, unchanged from today ⟦criterion 3⟧
- [ ] Go-red control: with the receipt check removed from `clear_refactor_pending.py`, the absent-receipt refusal case goes red, then the check is restored ⟦human-owed⟧ ⟦criterion 4⟧
