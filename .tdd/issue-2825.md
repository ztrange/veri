# Plan for #2825 — tests-frozen rerecord-rebased crashes (KeyError) on a recorded case title renamed before its step's commit

- [x] `tests-frozen.sh rerecord-rebased`, given a ticked earlier step's frozen record naming a case title that the recorded test file at HEAD does not hold, exits 2 with a stderr line naming that record file and the missing title, and no `KeyError` traceback ⟦criterion 1⟧
- [ ] When a step is ticked green with `tick-ledger.sh --refactor-pending`, its frozen record names each case by the title its test file holds at the tick (the title the step's green commit carries), so a case renamed after the step's `tests-frozen.sh record --step` and before its green commit is recorded under its renamed title, not the pre-rename one ⟦criterion 2⟧
