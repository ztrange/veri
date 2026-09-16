# Plan for #236 — metrics.sh runs before the done event is written, so every committed report reads Outcome and Wall time as unknown

- [x] SKILL.md's Draft PR step writes the run's `done` mark, carrying the opened PR's URL, before it renders the metrics report it commits — so a log holding exactly that one ended run renders a committed issue-<n>-metrics.md whose Outcome line names the landed PR
- [x] A log with exactly one run that ended in a `done` mark renders a Wall time line that is a number, not unknown
- [x] The report pasted into the PR body and into the closing `### ✅ Done` comment is the one rendered after `done` was written, and the committed file matches it
