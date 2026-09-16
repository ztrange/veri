# Plan for #230 — No conductor narration writes a refactor event mark, so the metrics report's refactor and stopped cells read unknown on every real run

- [ ] SKILL.md's Refactor phase writes an `event.sh refactor` mark carrying the transforms applied, the budget and why the loop stopped
- [ ] The refactor mark's transform count is the one `git rev-list --count` observed, and an overrun is recorded unclamped
- [ ] A run's metrics report shows real `refactor` and `stopped` cells for a step whose refactor mark is present, and still `unknown` for one whose mark is absent
