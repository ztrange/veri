### 📊 Metrics — issue 3201

Wall time for the issue: 1177 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3209.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 648 | 0 | 18496 | 0.05 |
| red | 2 | 1 | 0 | 0 | 52 | 26 | 11 | 20 | 3074 | 176752 | 42747 | 0.16 |
| green | 2 | 1 | 0 | 0 | 103 | 20 | 7 | 12 | 1605 | 82026 | 26624 | 0.09 |
| refactor | 1 | 0 | 0 | 0 | 5 | 3 | 2 | 4 | 135 | 23752 | 12841 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 108 | 23 | 8 | 16 | 2374 | 100256 | 46792 | 0.15 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 60 | 31 | 13 | 22 | 3088 | 182274 | 53916 | 0.18 |

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
| With `VERI_SESSION_TRANSCRIPTS` naming a directory that holds a timestamped `/vcoord` transcript, and an event log with no timestamped event, `metrics.sh <n>` exits 0 and reports the coordinator session's turns, cache tokens read and $ counting that transcript's turns (a missing window start bounds nothing, as `until=None` already does) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 49 | 20 | 36 | 4814 | 282530 | 82212 | 0.28 | 264 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With `VERI_SESSION_TRANSCRIPTS` naming a directory that holds a timestamped `/vcoord` transcript, and an event log with no timestamped event, `metrics.sh <n>` exits 0 and reports the coordinator session's turns, cache tokens read and $ counting that transcript's turns (a missing window start bounds nothing, as `until=None` already does) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 2 |
| fast | 19 | 26 |  |  |
| target | 1 | 1 | 1 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 21 | 38 | 5462 | 282530 | 100708 | 0.33 |
