# Plan for #4554 — A failed tests-frozen.sh rerecord-refactored leaves the frozen records rewritten, so the revert route skips every case

- [x] a rerecord-refactored whose closing check-earlier exits 1 leaves every frozen record byte-identical to before the call ⟦criterion 1⟧
