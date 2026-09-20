# Plan for #267 — skill-metrics.test.sh's two record-level Draft PR checks can't fail after #266's line-level ones

- [x] skill-metrics.test.sh no longer contains the commit_line -gt pr_line comparison or the comment describing it, and the suite still passes ⟦criterion 1⟧
- [x] skill-metrics.test.sh no longer contains the gh pr create + 📊 metrics record-level presence probe, and the suite still passes ⟦criterion 2⟧
