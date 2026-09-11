# Plan for #30 — ensure-run-state-ignored.sh: reject a partial or mis-ordered rule instead of reporting it present

- [x] a .gitignore carrying only .tdd/issue-*-spec.md exits non-zero with a diagnostic and leaves the file byte-identical
- [x] a .gitignore carrying the three lines out of order exits non-zero with a diagnostic and leaves the file byte-identical
- [x] a .gitignore that already ends in a newline gains the block with no blank line before it and reports added
