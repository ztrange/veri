### 📊 Metrics — issue 607

Wall time for the issue: 3661 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/609.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 9 | 3 | 6 | 1181 | 116624 | 27668 | 0.15 |
| red | 2 | 1 | 0 | 0 | 150 | 30 | 9 | 18 | 4060 | 391839 | 57841 | 0.35 |
| green | 6 | 1 | 2 | 0 | 1527 | 91 | 24 | 48 | 8084 | 1046337 | 88645 | 0.99 |
| refactor | 2 | 1 | 0 | 0 | 490 | 25 | 12 | 24 | 3281 | 557064 | 55225 | 0.37 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2068 | 1.60 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| wait-ci.test.sh's cases whose subject is the exit code for a check that never completes — the first case's pending rollup (exit 3), the legacy StatusContext PENDING and EXPECTED rows (exit 3), the legacy SUCCESS StatusContext beside a pending CheckRun (exit 3) and the all-SKIPPED rollup (exit 3) — each reach their 1800 s bound in at most 3 clock readings, by a larger clock step the case injects, never by a shorter bound ⟦criterion 2⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 146 | 45 | 90 | 15425 | 1995240 | 201711 | 1.70 | 2329 | 2/2 | 1/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| wait-ci.test.sh's cases whose subject is the exit code for a check that never completes — the first case's pending rollup (exit 3), the legacy StatusContext PENDING and EXPECTED rows (exit 3), the legacy SUCCESS StatusContext beside a pending CheckRun (exit 3) and the all-SKIPPED rollup (exit 3) — each reach their 1800 s bound in at most 3 clock readings, by a larger clock step the case injects, never by a shorter bound ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 490 | 0.37 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 0 | 0 | 416 |
| target | 55 | 0 | 16 |
| all | 441 | 432 |  |
| fast | 5 | 5 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 96 | 16606 | 2111864 | 229379 | 1.85 |
