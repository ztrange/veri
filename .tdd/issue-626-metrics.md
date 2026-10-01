### 📊 Metrics — issue 626

Wall time for the issue: 2115 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/639.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 3 | 6 | 1339 | 105200 | 38216 | 0.35 |
| red | 3 | 1 | 0 | 0 | 132 | 109 | 26 | 52 | 9986 | 1381110 | 149762 | 1.67 |
| green | 2 | 1 | 0 | 0 | 634 | 93 | 28 | 54 | 9038 | 1387140 | 95093 | 1.22 |
| refactor | 2 | 1 | 0 | 0 | 275 | 68 | 13 | 24 | 3844 | 518957 | 84639 | 0.86 |
| pin | 1 | 1 | 0 | 0 | 60 | 50 | 8 | 16 | 3517 | 361489 | 43112 | 0.49 |
| structural | 1 | 0 | 0 | 0 | 16 | 11 | 3 | 6 | 928 | 105575 | 36245 | 0.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a suite fails when SKILL.md's *Bailing* procedure has its metrics render step (`metrics.sh <n> > .tdd/issue-<n>-metrics.md`) before its `event.sh bail` step ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 219 | 56 | 108 | 18496 | 2672301 | 276150 | 3.11 | 1076 | unknown | 0/5 | nothing-left |  |  | full |
| the `event.sh bail` step that SKILL.md's *Bailing* procedure runs before rendering the metrics carries the bail's `cause=` and `classification=`, so the metrics committed and posted on a bail name the bail as the run's ending ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 101 | 19 | 38 | 7889 | 976395 | 96456 | 1.12 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a suite fails when SKILL.md's *Bailing* procedure has its metrics render step (`metrics.sh <n> > .tdd/issue-<n>-metrics.md`) before its `event.sh bail` step ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 275 | 0.86 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 152 | 148 | 181 | 181 | 0 | 1 |
| fast | 14 | 14 | 14 | 14 |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 158 | 28652 | 3859471 | 447067 | 4.92 |
