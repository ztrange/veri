### 📊 Metrics — issue 2075

Wall time for the issue: 0 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of unknown planned.
Outcome: the run bailed — needs-user, a process failure.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.15 over 17 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85784 |
| 2 | $0.03 | 87003 |
| 3 | $0.02 | 87831 |
| 4 | $0.03 | 89765 |
| 5 | $0.02 | 90069 |
| 6 | $0.02 | 90537 |
| 7 | $0.02 | 91137 |
| 8 | $0.02 | 91701 |
| 9 | $0.02 | 92324 |
| 10 | $0.02 | 92630 |
| 11 | $0.05 | 96138 |
| 12 | $0.08 | 103236 |
| 13 | $0.04 | 105937 |
| 14 | $0.03 | 107399 |
| 15 | $0.04 | 109777 |
| 16 | $0.08 | 117354 |
| 17 | $0.06 | 121772 |

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 0 | 0 | 0 | 0 | 0 | 0.00 |
