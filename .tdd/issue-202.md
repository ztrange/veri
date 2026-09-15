# Plan for #202 — The preamble every request is billed for

- [x] `## Draining a scope — the loop` and its `Loop *` sub-sections no longer sit in `skills/tdd/SKILL.md`; they live in a sibling file the conductor reads only on the scope branch, and `## Inputs` points at it, with `skill-identity.test.sh` cases 6 and 7 asserting the loop is reachable from `SKILL.md` rather than inside it
- [x] A `/tdd <n>` run's `SKILL.md` is ~1,676 tokens smaller and a `/tdd <scope>` run reaches the same procedure it always did, with the single-issue path untouched
- [ ] A new ADR records what a preamble token costs per night at the observed request volume, with the 2026-09-15 measurement
- [ ] Findings 2 and 3 of the step-1 table are recorded as declined, with the hazard that declines them, and that half of `SKILL.md` is closed
- [ ] Every rule that was in `CLAUDE.md` is still discoverable from it — stated, or stated in one sentence with a pointer to the ADR or issue now carrying the reasoning
- [ ] `make test` passes, with `claude-md-counts.test.sh`, `lane-rule-recorded.test.sh`, `count-line-guard.test.sh` and `docs-targets-refuse.test.sh` green against the edited `CLAUDE.md`
- [ ] No test asserts a maximum size for either file
