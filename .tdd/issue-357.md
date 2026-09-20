# Plan for #357 — verify-green rejects production code no test requires

- [x] The green verifier prompt REJECTs production code no test requires — a branch, option, flag or parameter whose removal leaves every test green — and names that code in `REASON:` ⟦criterion 1⟧
- [x] The green verifier prompt tells the verifier to establish that by removing the code and running the suite, then restoring the tree and confirming with `git diff --exit-code` before reporting ⟦criterion 2⟧
