# Plan for #4456 — PRD 036.10: a warning when test runs stretch past 2× their idle duration

- [x] test-ceiling.sh, on a ramp that found a ceiling, runs one registered `make unit` after the ramp and writes `idle all <seconds>` (the ceiling step's) and `idle fast <seconds>` after the step lines ⟦criterion 1⟧
- [x] a red `make unit` after the ramp is exit 2 naming it, and the record stays as it was ⟦criterion 2⟧
- [x] timed-test-run.sh writes a `test-stretch` event (tier, seconds, idle) after a `fast` or `all` run whose seconds exceed twice that tier's `idle` line; other tiers and a record without the line write none ⟦criterion 3⟧
- [x] a ceiling record timed-test-run.sh cannot read is no `test-stretch` event and leaves its exit code as the command's ⟦criterion 6⟧
- [x] the leg's T is line 1 of a record holding `idle` lines ⟦criterion 4⟧
- [ ] dispatch.sh prints `stretched <issue> <tier> <seconds>s, idle <idle>s` for a live run's first unreported `test-stretch` event, once per run and tier kept in `.tdd/dispatch-notified`, and exits 0 ⟦criterion 5⟧
- [ ] SCRIPTS.md, CLAUDE.md and vdev's SKILL.md name the `idle` lines, the `test-stretch` event and the `stretched` line, regraded ⟦criterion 7⟧
