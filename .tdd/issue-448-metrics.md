### 📊 Metrics — issue 448

Wall time for the issue: 4011 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/470.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 10 | 1 | 2 | 1116 | 11207 | 34597 | 0.30 |
| red | 16 | 6 | 0 | 0 | 604 | 503 | 117 | 228 | 48860 | 5323196 | 688249 | 7.55 |
| green | 16 | 6 | 2 | 0 | 2055 | 489 | 120 | 240 | 45783 | 5396928 | 624698 | 6.99 |
| refactor | 12 | 6 | 0 | 0 | 465 | 295 | 74 | 148 | 26576 | 3225880 | 487372 | 5.08 |
| pin | 4 | 4 | 0 | 0 | 95 | 68 | 17 | 34 | 6621 | 661912 | 153157 | 1.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1684 | 3.53 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `step-cost.sh <step-text>` prints the summed `total_cost_usd` of that step's `usage` events to two decimals and exits 0, from a new unit-tier suite under `skills/tdd/scripts/tests/unit/` whose header states the fast-tier bar it clears (no git, no network, no servers, no real `sleep`, no nested suites) ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 254 | 58 | 114 | 22695 | 2581854 | 339888 | 3.69 | 1048 | 1/2 | 0/5 | nothing-left |
| `step-cost.sh <step-text>` for a step no `usage` event carries prints nothing and exits 3 ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 34 | 68 | 11458 | 1433351 | 236126 | 2.41 | 316 | unknown | 0/5 | nothing-left |
| `step-cost.sh --run` prints the summed `total_cost_usd` of every `usage` event in the log, including those carrying no step, to two decimals and exits 0 ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 152 | 40 | 80 | 14396 | 1748605 | 240724 | 2.56 | 245 | unknown | 1/5 | nothing-left |
| `step-cost.sh --run` against a log holding no `usage` event prints nothing and exits 3 ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 38 | 76 | 13080 | 1630628 | 240077 | 2.51 | 236 | unknown | 0/5 | nothing-left |
| `step-cost.sh --steps` prints one `<dollars> <leaves>` line per step that has a `usage` event, in the order the log first mentions each, and exits 0; with no `usage` event it prints nothing and exits 3 ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 42 | 84 | 17161 | 1879452 | 249533 | 2.72 | 273 | unknown | 2/5 | nothing-left |
| A `usage` event whose `total_cost_usd` is absent or empty contributes zero (while still counting as a leaf) rather than aborting the read ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 13 | 26 | 6146 | 578277 | 81834 | 0.89 | unknown | unknown | unknown | unknown |
| Events that are not `usage` events (a `verdict` or `test-run` line carrying a step) are ignored by all three calls, so they create no step and add no cost ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 13 | 26 | 5618 | 591095 | 82047 | 0.89 | unknown | unknown | unknown | unknown |
| No argument, an unknown argument, `--run` or `--steps` with a step text besides, and a missing `.tdd/events.jsonl` each exit 2 with a diagnostic on stderr and nothing on stdout ⟦criterion 8⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 250 | 59 | 116 | 24042 | 2653632 | 301567 | 3.42 | 1144 | 1/2 | 2/5 | nothing-left |
| The unit suite's header states the fast-tier bar and the suite passes under `make unit`'s shims (no git, gh, curl or python3 called for real) ⟦criterion 9⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 78 | 17 | 34 | 7780 | 912595 | 98270 | 1.12 | unknown | unknown | unknown | unknown |
| `step-cost.sh`'s own header says it reports leaf spend only — the conductor's own spending is in no `usage` event | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 14 | 26 | 5464 | 598427 | 83410 | 0.90 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 1 | 1 | 72 | 0 | 72 | 1 | 77 | 0 | 75 | 0 | 0 | 0 | 81 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 2 | 78 | 0 | 0 | 0 | 1 | 1 | 0 |
| fast | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 345 | 345 | 344 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 329 | 652 | 128956 | 14619123 | 1988073 | 21.41 |
