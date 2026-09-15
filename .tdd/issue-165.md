# Plan for #165 — Nothing records which skill commit a run used

- [x] event.sh reads VERI_SKILL_COMMIT from the environment and writes it as a fixed key on every line
- [x] supervise.sh resolves the skill commit at launch time and exports it for event.sh
- [x] The plan comment names the skill commit the run started on
- [x] An unresolvable commit is recorded as the literal string unknown, not an absent field
- [ ] SKILL.md documents that the skill may change under a running conductor and the event log records which commit each leaf used
