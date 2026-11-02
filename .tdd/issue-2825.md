# Plan for #2825 — tests-frozen rerecord-rebased crashes (KeyError) on a recorded case title renamed before its step's commit

- [ ] `tests-frozen.sh rerecord-rebased` given an earlier step's frozen record whose case title is missing at HEAD exits 2 with no traceback and no `KeyError`, its stderr naming the record file and the missing title, and rewrites no record ⟦criterion 1⟧
- [ ] When a case recorded by `tests-frozen.sh record --step` is renamed in the working tree before the step's commit and the step is recorded again, the step's record holds the case only under the title the step's commit holds, so the record names no title absent from that commit and a later `rerecord-rebased` on it does not fail on a missing title ⟦criterion 2⟧
