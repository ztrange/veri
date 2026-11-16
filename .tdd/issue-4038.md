# Plan for #4038 — PRD 025.11: comment-class.sh is gone

- [x] the three unit/test_comment.py cases that classified posted headings keep their posting and metrics-family assertions without veri.comment_class, under names that do not hold comment_class ⟦criterion 2⟧
- [ ] comment-class.sh, veri/comment_class.py and their two test files are deleted, test_fast_tier_guard.py's placement case for test_comment_class.py goes, the entries leave veri/README.md, unit/test_emitted_text.py and unit/test_scripts_md_rows.py, and git grep comment-class|comment_class prints nothing ⟦criterion 1⟧
