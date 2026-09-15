# Plan for #165 — A run executes the skill from the primary clone, so a merge and pull there changes scripts under a running conductor

- [ ] `pin-skill.sh` snapshots the skill's `scripts/` directory into `.tdd/skill/scripts/` and records the commit sha to `.tdd/skill-commit`; on resume reuses the existing snapshot; prints the snapshot scripts path on stdout
- [ ] SKILL.md integrates `pin-skill.sh` into preflight, re-exports `$S` to the snapshot, prescribes the plan comment and event log carrying the commit, and documents where `$S` points after preflight
