# Plan for #448 — `step-cost.sh`: what this step and this run have spent so far, read from the event log

- [x] `step-cost.sh <step-text>` prints the summed `total_cost_usd` of that step's `usage` events to two decimals and exits 0, from a new unit-tier suite under `skills/tdd/scripts/tests/unit/` whose header states the fast-tier bar it clears (no git, no network, no servers, no real `sleep`, no nested suites) ⟦criterion 1⟧
- [ ] `step-cost.sh <step-text>` for a step no `usage` event carries prints nothing and exits 3 ⟦criterion 2⟧
- [ ] `step-cost.sh --run` prints the summed `total_cost_usd` of every `usage` event in the log, including those carrying no step, to two decimals and exits 0 ⟦criterion 3⟧
- [ ] `step-cost.sh --run` against a log holding no `usage` event prints nothing and exits 3 ⟦criterion 4⟧
- [ ] `step-cost.sh --steps` prints one `<dollars> <leaves>` line per step that has a `usage` event, in the order the log first mentions each, and exits 0; with no `usage` event it prints nothing and exits 3 ⟦criterion 5⟧
- [ ] A `usage` event whose `total_cost_usd` is absent or empty contributes zero (while still counting as a leaf) rather than aborting the read ⟦criterion 6⟧
- [ ] Events that are not `usage` events (a `verdict` or `test-run` line carrying a step) are ignored by all three calls, so they create no step and add no cost ⟦criterion 7⟧
- [ ] No argument, an unknown argument, `--run` or `--steps` with a step text besides, and a missing `.tdd/events.jsonl` each exit 2 with a diagnostic on stderr and nothing on stdout ⟦criterion 8⟧
- [ ] The unit suite's header states the fast-tier bar and the suite passes under `make unit`'s shims (no git, gh, curl or python3 called for real) ⟦criterion 9⟧
- [ ] `step-cost.sh`'s own header says it reports leaf spend only — the conductor's own spending is in no `usage` event
