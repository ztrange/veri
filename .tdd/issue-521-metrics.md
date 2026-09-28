### 📊 Metrics — issue 521

Wall time for the issue: 1226 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/545.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 9 | 2 | 4 | 721 | 56742 | 35018 | 0.31 |
| red | 2 | 1 | 0 | 0 | 110 | 96 | 23 | 44 | 8494 | 1146717 | 91238 | 1.13 |
| green | 2 | 1 | 0 | 0 | 102 | 73 | 18 | 36 | 6901 | 827679 | 85134 | 0.98 |
| refactor | 2 | 1 | 0 | 0 | 49 | 29 | 10 | 20 | 2647 | 414520 | 80154 | 0.78 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| step-cost.sh given a step title carrying an em dash and ⟦criterion k⟧ prints the dollars summed over that step's usage events, the same figure --steps prints for it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 51 | 100 | 18042 | 2388916 | 256526 | 2.89 | 355 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| step-cost.sh given a step title carrying an em dash and ⟦criterion k⟧ prints the dollars summed over that step's usage events, the same figure --steps prints for it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 49 | 0.78 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
