### 📊 Metrics — issue 1754

Wall time for the issue: 1279 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1762.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 558 | 0 | 29898 | 0.08 |
| red | 2 | 1 | 0 | 0 | 121 | 42 | 14 | 28 | 4386 | 475882 | 66742 | 0.26 |
| green | 2 | 1 | 0 | 0 | 179 | 31 | 14 | 28 | 3057 | 412575 | 31950 | 0.15 |
| refactor | 2 | 1 | 0 | 0 | 79 | 19 | 9 | 18 | 1823 | 249975 | 29346 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 208 | 50 | 17 | 34 | 5020 | 450117 | 75322 | 0.28 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 179 | 48 | 21 | 42 | 4804 | 688315 | 82614 | 0.32 |

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
| A develop-green launch supervise.sh refuses for a step with no verify-red PASS after its latest red leaf, run detached through detach-leaf.sh, records exit 2 where wait-leaf.sh reads it: wait-leaf.sh develop-green returns 2, not 3, and no leaf is started ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 92 | 37 | 74 | 9266 | 1138432 | 128038 | 0.53 | 501 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A develop-green launch supervise.sh refuses for a step with no verify-red PASS after its latest red leaf, run detached through detach-leaf.sh, records exit 2 where wait-leaf.sh reads it: wait-leaf.sh develop-green returns 2, not 3, and no leaf is started ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 79 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 36 | 37 | 35 | 36 | 0 | 36 |
| fast | 16 | 16 | 17 |  |  |  |
| target | 1 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 38 | 76 | 9824 | 1138432 | 157936 | 0.61 |
