# Plan for #128 — solvable-issues.sh ignores a blocker written as a URL under ## Blocked by, so a blocked issue is taken early

- [x] a blocker written as `https://github.com/<owner>/<repo>/issues/<n>` under `## Blocked by` blocks exactly as `#<n>` does
- [x] a URL for another repository's issue is not read as a blocker in this one
- [x] the header comment of `solvable-issues.sh` names both spellings ⟂ refactor pending
