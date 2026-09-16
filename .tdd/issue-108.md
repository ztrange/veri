# Plan for #108 — Per-issue metrics: a committed markdown summary beside the ledger and a 📊 block in the final comment and PR

- [x] metrics.sh renders a markdown table of per-phase attempts, verdicts PASS/REJECT and kills from the event log
- [x] the table carries a per-step section with the same counts, plus stuck retries used
- [x] the table reports revise attempts used of REVISE_BUDGET and refactor transforms used of VERI_REFACTOR_BUDGET, and whether the refactor loop stopped by budget
- [x] the table reports wall seconds and API seconds per phase and per step, and the issue's wall time from its first event to done or bail
- [x] the table reports turns, the four token counts and dollars per phase, per step and in total, with a line saying whether the conductor's own cost is included
- [x] a step recovered after a REJECT contributes its rejected attempts to rework per phase and nothing to waste
- [x] a bailed step contributes every attempt, PASS verdicts included, to waste per phase and nothing to rework
- [ ] the table reports steps done of planned and the issue's outcome, a bail split system or process
- [ ] a figure a missing conductor mark makes unreadable renders as unknown, never as zero
- [ ] SKILL.md has the conductor commit issue-<n>-metrics.md in one metrics: commit before the PR and append the 📊 Metrics block to the final comment and PR body, and on a bail commit it on the pushed branch with the block on the bail comment
