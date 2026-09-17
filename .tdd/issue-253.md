# Plan for #253 — run-conductor.sh's skill pin (#237) ships short: a silent fallback re-pin, a misplaced skill-repin event, and no docs

- [x] An unresolvable recorded skill commit refuses with exit 2 unless VERI_NEW_SKILL=1, which re-pins and records a skill-repin event
- [x] The skill-repin event lands in the run worktree's .tdd/wt/<n>/.tdd/events.jsonl, never the caller's .tdd/events.jsonl
- [x] run-conductor.sh hands the conductor the unpinned case in its environment, and SKILL.md's plan-comment step names that case
- [ ] SKILL.md documents the skill snapshot, VERI_NEW_SKILL and .tdd/issue-<n>-skill-commit, and CLAUDE.md cross-references it
