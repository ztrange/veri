### 📊 Metrics — issue 1457

Wall time for the issue: 958 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1466.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 2 | 1 | 2 | 336 | 12489 | 31006 | 0.13 |
| red | 2 | 1 | 0 | 0 | 75 | 44 | 12 | 22 | 4234 | 495418 | 86836 | 0.69 |
| green | 2 | 1 | 0 | 0 | 111 | 52 | 15 | 30 | 4464 | 691728 | 83466 | 0.70 |
| refactor | 2 | 1 | 0 | 0 | 77 | 43 | 13 | 26 | 4206 | 592830 | 83553 | 0.67 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 127 | 39 | 16 | 32 | 4681 | 634521 | 149979 | 0.71 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 142 | 102 | 25 | 48 | 8559 | 1157944 | 134882 | 1.48 |

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
| build-develop-prompt.sh revise with an unknown phase to revise exits 2 and its refusal names every phase it accepts to revise, the interface phases expand, migrate, contract-a and contract-b included ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 139 | 40 | 78 | 12904 | 1779976 | 253855 | 2.06 | 353 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| build-develop-prompt.sh revise with an unknown phase to revise exits 2 and its refusal names every phase it accepts to revise, the interface phases expand, migrate, contract-a and contract-b included ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 77 | 0.67 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 25 | 2 | 1 | 2 | 2 | 1 | 1 | 0 |
| fast | 24 | 24 | 23 |  |  |  |  |  |  |
| target | 1 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 41 | 80 | 13240 | 1792465 | 284861 | 2.19 |
