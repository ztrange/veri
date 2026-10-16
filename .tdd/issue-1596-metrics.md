### 📊 Metrics — issue 1596

Wall time for the issue: 1749 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1608.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 37 | 28 | 4 | 8 | 2727 | 134573 | 88977 | 0.40 |
| red | 4 | 1 | 0 | 0 | 186 | 79 | 27 | 46 | 9608 | 1193860 | 207418 | 1.05 |
| green | 2 | 1 | 0 | 0 | 234 | 34 | 11 | 22 | 3693 | 527841 | 91166 | 0.45 |
| refactor | 2 | 1 | 0 | 0 | 158 | 36 | 13 | 24 | 3891 | 596550 | 92683 | 0.47 |
| pin | 2 | 2 | 0 | 0 | 98 | 28 | 9 | 18 | 2731 | 400734 | 89321 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 377 | 99 | 27 | 52 | 9770 | 1126882 | 312598 | 1.46 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 336 | 106 | 37 | 66 | 12880 | 1726676 | 256967 | 1.33 |

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
| For a single-case suite, a row whose named old case or replacement already fails with the mutation not applied reads `unproven`, and the output names which of the two failed unmutated ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 104 | 34 | 62 | 11451 | 1510070 | 286642 | 1.41 | 561 | unknown | 2/5 | nothing-structural |  |  | full |
| For a multi-case suite, a row whose named old case or replacement already fails with the mutation not applied reads `unproven`, and the output names which of the two failed unmutated (expected already satisfied by step 1's change, so a regression pin through verify-pin, not a Red/Green cycle) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 12 | 22 | 4433 | 537416 | 96103 | 0.48 | unknown | unknown | unknown | unknown |  |  | pin |
| Regression pin, test only, no production change (today's code already re-raises, so this is already satisfied and goes through verify-pin, not Red/Green): a suite with more than one case that dies before its count line under the mutation makes mutation-parity.sh end in an error, not print `owed` for that row, and the pinning case goes red when the multi-case re-raise in veri/mutation_parity.py is replaced by returning `owed` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 14 | 26 | 4039 | 671499 | 97843 | 0.50 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| For a single-case suite, a row whose named old case or replacement already fails with the mutation not applied reads `unproven`, and the output names which of the two failed unmutated ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 158 | 0.47 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 11 | 16 | 15 | 16 | 15 | 16 |
| fast | 64 | 64 | 62 |  |  |  |
| target | 16 | 17 | 16 | 16 | 16 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 64 | 118 | 22650 | 2853558 | 569565 | 2.79 |
