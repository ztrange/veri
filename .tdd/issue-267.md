# Plan for #267 — skill-metrics.test.sh's two record-level Draft PR checks can't fail after #266's line-level ones

- [x] skill-metrics.test.sh no longer compares commit_line against pr_line at record level (the `commit_line -gt pr_line` check is gone), and the "lands BEFORE the PR is opened" comment that justified it is removed or corrected ⟦criterion 1⟧
- [x] skill-metrics.test.sh no longer asks the record-level presence probe first_record_line "$pr_records" 'gh pr create' '📊 metrics', and any comment describing it is corrected ⟦criterion 2⟧
- [x] the #266 line-level Draft PR checks in skill-metrics.test.sh still fail when SKILL.md's Draft PR command order is broken (gh pr create after the metrics: commit, or gh pr edit before it / without the 📊 block) ⟦criterion 3⟧
