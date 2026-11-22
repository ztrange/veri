# Plan for #4624 — test-quality.sh record refuses a finding whose case file is package-relative, so the test-quality step bails no-verdict

- [x] `test-quality.sh record` records a finding whose file is a package-relative path matching exactly one test file `.tdd/test-quality-files` lists, under that file's repo-relative path (exit 0) ⟦criterion 1⟧
- [x] `test-quality.sh record` refuses a finding whose package-relative path matches more than one test file `.tdd/test-quality-files` lists, exiting 2 when none survives ⟦criterion 1⟧
- [ ] the `$S/test-quality.sh` entry of `skills/tdd/SCRIPTS.md` says `record` resolves a package-relative path matching exactly one listed test file, and the entry is regraded
