### 📊 Metrics — issue 1023

Wall time for the issue: 2475 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1052.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 3 | 6 | 1206 | 109568 | 41389 | 0.38 |
| red | 3 | 1 | 0 | 0 | 87 | 67 | 19 | 36 | 6427 | 874610 | 139223 | 1.42 |
| green | 2 | 1 | 0 | 0 | 145 | 47 | 15 | 28 | 3983 | 655959 | 86183 | 0.90 |
| refactor | 2 | 1 | 0 | 0 | 97 | 42 | 13 | 26 | 4149 | 618420 | 88210 | 0.91 |
| pin | 1 | 1 | 0 | 0 | 21 | 14 | 3 | 6 | 1455 | 113524 | 41281 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 5 | 5 | 0 | 0 | 195 | 81 | 25 | 48 | 7889 | 1043023 | 211252 | 2.06 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 171 | 101 | 28 | 54 | 9331 | 1329058 | 185034 | 1.93 |

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
| `refactor-owed.sh list` does not print a candidate the owed file records with an `applied | <sha> | <candidate>` line, while still printing the candidates not recorded as applied ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 130 | 40 | 78 | 12083 | 1855146 | 266231 | 2.74 | 382 | unknown | 1/5 | nothing-structural |  |  | full |
| `refactor-owed.sh list` exits 3 with empty stdout when every structural candidate in the owed file has an `applied | <sha> | <candidate>` record ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 10 | 18 | 3931 | 407367 | 88666 | 0.87 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `refactor-owed.sh list` does not print a candidate the owed file records with an `applied | <sha> | <candidate>` line, while still printing the candidates not recorded as applied ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 97 | 0.91 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 |
| fast | 40 | 41 | 40 |  |  |  |  |  |  |
| target | 1 | 1 | 0 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 53 | 102 | 17220 | 2372081 | 396286 | 3.99 |
