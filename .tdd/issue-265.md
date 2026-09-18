# Plan for #265 — run-conductor.sh's caller-log fallback and SKILL.md's stale $S paragraph

- [x] a VERI_NEW_SKILL=1 re-pin that runs before .tdd/wt/<n> exists writes its skill-repin event to the run worktree's .tdd/events.jsonl and never to the caller's ⟦criterion 1⟧
- [ ] SKILL.md's $S paragraph no longer says "Nothing here pins it" and states that the skill snapshot (VERI_SKILL_COMMIT, .tdd/issue-<n>-skill-commit) pins the commit a run executes under ⟦criterion 2⟧
