### 📊 Metrics — issue 1826

Wall time for the issue: 1097 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 428 | 17463 | 12490 | 0.04 |
| red | 4 | 1 | 0 | 0 | 67 | 55 | 20 | 40 | 5776 | 593968 | 67729 | 0.29 |
| green | 2 | 1 | 0 | 0 | 59 | 39 | 9 | 16 | 2212 | 215284 | 26810 | 0.11 |
| refactor | 2 | 1 | 0 | 0 | 38 | 27 | 6 | 10 | 968 | 123501 | 27063 | 0.09 |
| pin | 2 | 2 | 0 | 0 | 29 | 23 | 7 | 14 | 2329 | 181884 | 27773 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 99 | 68 | 18 | 36 | 5063 | 457920 | 80436 | 0.30 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 101 | 81 | 25 | 46 | 6650 | 674180 | 81429 | 0.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| unreplaced-cases.sh counts a bash case as replaced when its REPLACES: line names a parametrized pytest case `<path>::<test>[<param id>]` and `<path>` defines `def <test>` (exit 0, the case not printed) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 94 | 25 | 46 | 5442 | 633491 | 86457 | 0.33 | 222 | unknown | 0/5 | nothing-left |  |  | full |
| unreplaced-cases.sh still counts a bash case as unreplaced when its REPLACES: line names a parametrized node id `<path>::<test>[<param id>]` whose `def <test>` is absent from `<path>` (exit 1, the case printed) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 9 | 18 | 3250 | 255392 | 31721 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| unreplaced-cases.sh still counts a bash case as unreplaced when its REPLACES: line names a node id `<path>::<test>` with no `[…]` suffix whose `def <test>` is absent from `<path>` (exit 1, the case printed) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 8 | 16 | 2593 | 225754 | 31197 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| unreplaced-cases.sh counts a bash case as replaced when its REPLACES: line names a parametrized pytest case `<path>::<test>[<param id>]` and `<path>` defines `def <test>` (exit 0, the case not printed) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 38 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 3 | 3 | 1 | 0 | 1 | 1 |
| fast | 5 | 5 |  |  |  |  |  |  |
| target | 5 | 0 | 0 | 0 | 0 | 0 | 0 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 82 | 11713 | 1132100 | 161865 | 0.64 |
