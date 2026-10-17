### 📊 Metrics — issue 1440

Wall time for the issue: 1387 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1678.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 28 | 20 | 6 | 12 | 2052 | 248777 | 90035 | 0.41 |
| red | 1 | 0 | 0 | 0 | 63 | 27 | 8 | 16 | 3162 | 470675 | 57326 | 0.31 |
| pin | 1 | 1 | 0 | 0 | 17 | 10 | 3 | 6 | 1321 | 123411 | 45154 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 2 | 1 | 0 | 45 | 30 | 9 | 18 | 3373 | 372188 | 135189 | 0.61 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 63 | 27 | 8 | 16 | 3162 | 470675 | 57326 | 0.31 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Regression pin (test-only, the pin path — the behaviour already holds, so Red is expected to report AGAINST_UNMODIFIED: PASSES and verify-pin judges it): a case in tests/py/test_supervise.py showing a supervised leaf that never answers is launched the same number of times with VERI_NO_VERDICT_RETRIES set to a value larger than VERI_STUCK_RETRIES as without it, so the supervisor's retry count comes from VERI_STUCK_RETRIES alone; the case must go red when supervise.py reads VERI_NO_VERDICT_RETRIES as its retry count; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 22 | 4483 | 594086 | 102480 | 0.51 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 30 |  |
| target | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 17 | 34 | 6535 | 842863 | 192515 | 0.92 |
