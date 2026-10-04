# Plan for #566 — a failed metrics.sh render is committed as the run's metrics report

- [x] SKILL.md's Draft PR step commits `.tdd/issue-<n>-metrics.md` only when `metrics.sh` exits 0; on a non-zero exit it makes no `metrics:` commit and the PR body carries a line naming the failed render and its exit code in place of the file's contents ⟦criterion 1⟧
- [x] SKILL.md's Draft PR step, on a non-zero `metrics.sh` exit, puts the same failed-render line with its exit code in the `### ✅ Done` comment in place of the `### 📊 Metrics` block
- [x] SKILL.md's Bailing sub-step 4 commits `.tdd/issue-<n>-metrics.md` only when `metrics.sh` exits 0; on a non-zero exit it makes no `metrics:` commit and the `### ⛔ Bailed` comment carries the failed-render line with its exit code in place of the `### 📊 Metrics` block ⟦criterion 2⟧
- [x] a non-zero `metrics.sh` exit in the Draft PR step does not bail or stop the run: the step goes on to its push and the PR body rewrite ⟦criterion 3⟧
- [x] a non-zero `metrics.sh` exit in Bailing sub-step 4 does not stop the bail: it goes on to sub-step 5's push and sub-step 6's comment ⟦criterion 3⟧
- [ ] every case `skill-metrics.test.sh` already holds passes with its assertions unchanged ⟦diff-checked⟧ ⟦criterion 4⟧
