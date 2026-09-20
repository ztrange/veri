# Plan for #358 — Refactor may touch an untouched file to remove duplication with this cycle's code

- [x] The refactor developer prompt permits a transform in a file outside the touched-files list only when it removes duplication between that file and code this cycle wrote ⟦criterion 1⟧
- [x] The refactor developer prompt tells the leaf to run the suites covering every file a transform touched, the out-of-list file included ⟦criterion 2⟧
- [x] The refactor verifier prompt derives the cycle's files as `git diff --name-only <base-sha>^ <base-sha>` and REJECTs a changed file outside that list unless its hunk removes duplication with code in it ⟦criterion 3⟧
