### 📊 Metrics — issue 1488

Wall time for the issue: 1509 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1685.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 6 | 1 | 2 | 571 | 12193 | 43363 | 0.18 |
| red | 2 | 1 | 0 | 0 | 45 | 32 | 10 | 20 | 3987 | 500598 | 101706 | 0.50 |
| green | 2 | 1 | 0 | 0 | 82 | 29 | 12 | 22 | 2954 | 536652 | 91568 | 0.45 |
| refactor | 2 | 1 | 0 | 0 | 43 | 16 | 7 | 14 | 1366 | 305755 | 90920 | 0.41 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 110 | 47 | 16 | 32 | 4816 | 725271 | 180579 | 0.84 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 70 | 36 | 14 | 26 | 4062 | 629927 | 146978 | 0.69 |

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
| status.sh's scope line and its --json scope `bailed` field count a run as bailed only when the run's standing end is a bail: a run that bailed, was resumed and bailed again counts bailed 1, and a run that bailed, was resumed and finished counts done 1 and bailed 0 — pinned by a case in tests/py/test_status.py ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 77 | 29 | 56 | 8307 | 1343005 | 284194 | 1.35 | 260 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| status.sh's scope line and its --json scope `bailed` field count a run as bailed only when the run's standing end is a bail: a run that bailed, was resumed and bailed again counts bailed 1, and a run that bailed, was resumed and finished counts done 1 and bailed 0 — pinned by a case in tests/py/test_status.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.41 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 2 | 9 | 1 |
| fast | 16 | 16 | 16 |  |  |  |
| target | 0 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 30 | 58 | 8878 | 1355198 | 327557 | 1.53 |
