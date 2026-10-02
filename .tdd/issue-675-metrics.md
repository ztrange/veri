### 📊 Metrics — issue 675

Wall time for the issue: 2752 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/685.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 9 | 2 | 4 | 1011 | 58670 | 37296 | 0.33 |
| red | 5 | 2 | 0 | 0 | 248 | 204 | 46 | 90 | 19443 | 2397073 | 245010 | 2.83 |
| green | 6 | 2 | 1 | 0 | 505 | 227 | 56 | 112 | 22397 | 2700726 | 227407 | 2.81 |
| refactor | 6 | 2 | 1 | 0 | 420 | 172 | 40 | 80 | 17182 | 1807324 | 253989 | 2.74 |
| pin | 1 | 1 | 0 | 0 | 26 | 17 | 4 | 8 | 1718 | 158791 | 40825 | 0.39 |
| structural | 3 | 0 | 0 | 0 | 187 | 129 | 27 | 54 | 12364 | 1376034 | 142450 | 1.66 |
| transform | 2 | 1 | 1 | 0 | 125 | 100 | 14 | 28 | 7243 | 658831 | 90374 | 1.00 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 12 | 9 | 3 | 0 | 773 | 384 | 83 | 166 | 34973 | 3812026 | 475859 | 5.27 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 754 | 474 | 106 | 210 | 46385 | 5345423 | 561492 | 6.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 347 | 1.76 | 0 | 0.00 |
| refactor | 323 | 1.85 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| ledger_steps reports added=0 for a step whose text quotes ⟦added⟧ mid-text and does not end in it ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 253 | 64 | 126 | 24967 | 2984737 | 310352 | 3.58 | 628 | 1/2 | 0/5 | structural-owed |  |  | full |
| ledger_steps reports added=1 for a step whose text ends in ⟦added⟧ once a trailing ⟦criterion k⟧ and a trailing ⟂ refactor pending are stripped, done or open ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 278 | 66 | 132 | 26598 | 3200657 | 358090 | 4.04 | 687 | 1/2 | 2/5 | structural-owed |  |  | full |
| add-ledger-step.sh's is_added_step and ledger_steps' added column agree on every step line of add-ledger-step.test.sh's ledger fixtures ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 89 | 16 | 32 | 9175 | 878520 | 98789 | 1.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| ledger_steps reports added=0 for a step whose text quotes ⟦added⟧ mid-text and does not end in it ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 97 | 0.88 |
| ledger_steps reports added=1 for a step whose text ends in ⟦added⟧ once a trailing ⟦criterion k⟧ and a trailing ⟂ refactor pending are stripped, done or open ⟦criterion 1⟧ | 1 | 2/5 | structural-owed | PASS | 1 | 323 | 1.85 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 6 | 10 | 0 | 9 | 9 | 0 | 10 | 9 | 0 | 0 | 6 | 0 | 9 | 0 | 2 | 0 | 6 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 8 | 0 | 9 | 2 | 2 | 2 | 2 | 1 | 2 | 27 | 10 |
| fast | 27 | 27 | 27 | 27 | 27 | 25 | 25 | 27 | 24 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 189 | 376 | 81358 | 9157449 | 1037351 | 11.76 |
