# Plan for #1878 — A refused verifier's diff is silently lost when git diff fails, and depends on the user's diff config

- [x] When the `git diff` that `save_diff` runs exits non-zero (forced through git config: `diff.orderFile` naming a missing file), the refusal prints "diff could not be saved to .tdd/<leaf>.diff", writes no diff file, and still exits 2 ⟦criterion 1⟧
- [x] A `.tdd/<leaf>.diff` left by an earlier refusal is removed when a later refusal's diff could not be saved, so no file under `.tdd/` claims to be that refusal's evidence ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The saved diff ignores the user's prefix, context and abbreviation config: with `diff.noprefix=true`, `diff.context=0` and `core.abbrev=4` set, the refusal's saved `.tdd/<leaf>.diff` passes `git apply --check` (save_diff passes explicit `--src-prefix=a/ --dst-prefix=b/ -U3 --full-index` or equivalent) ⟦criterion 3⟧
