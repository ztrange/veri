### 📊 Metrics — issue 454

Wall time for the issue: 2678 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/528.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 10 | 2 | 4 | 995 | 57009 | 36263 | 0.32 |
| red | 9 | 3 | 0 | 0 | 525 | 394 | 88 | 168 | 39565 | 4360599 | 436385 | 5.16 |
| green | 6 | 3 | 0 | 0 | 362 | 193 | 56 | 112 | 17633 | 2598261 | 253627 | 2.90 |
| refactor | 8 | 3 | 1 | 0 | 856 | 236 | 68 | 134 | 23516 | 3097423 | 333400 | 3.76 |
| pin | 3 | 3 | 0 | 0 | 161 | 93 | 23 | 46 | 9517 | 1017350 | 128668 | 1.42 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 657 | 1.81 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `#### By step` carries a kind column whose cell reads `pin` for a step that wrote a `pin` mark and `full` for a step that ran Red → Green → Refactor ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 185 | 50 | 96 | 17921 | 2300411 | 265550 | 2.94 | 362 | unknown | 2/5 | nothing-left |  |  |
| The kind column reads `already-satisfied` for a step whose red leaf found the criterion already satisfied (a verify-pin verdict) but which carries no `pin` mark, and `full` for a full step ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 201 | 53 | 104 | 19509 | 2496570 | 263907 | 3.00 | 364 | unknown | 2/5 | nothing-structural |  |  |
| The kind is read off the step's own events: a step with a `pin` mark or a verify-pin verdict is short however many leaves it launched, and a full step with only two leaves in the log still reads `full` ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 88 | 19 | 38 | 8987 | 930958 | 93637 | 1.12 | unknown | unknown | unknown | unknown |  |  |
| A report over a log of only full steps still renders the kind column, reading `full` on every row ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 18 | 36 | 6648 | 853927 | 89744 | 1.02 | unknown | unknown | unknown | unknown |  |  |
| `#### By step` is followed by one line naming turns as the figure comparable across runs, dollars as the figure that is not, and `VERI_MODEL`, `VERI_MODEL_DEVELOPER` and `VERI_MODEL_VERIFIER` as the reason ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 242 | 72 | 142 | 23177 | 3282539 | 332670 | 3.78 | 965 | 1/2 | 0/5 | nothing-structural |  |  |
| Every By-step column that existed before, and every other section of the report, renders the same cells for an existing log as before the kind column was added ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 133 | 23 | 44 | 13989 | 1209228 | 106572 | 1.37 | unknown | unknown | unknown | unknown |  |  |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 6 | 5 | 6 | 5 | 0 | 5 | 5 | 5 | 5 | 5 | 0 | 6 | 0 | 5 | 6 | 5 | 5 | 5 | 6 | 5 | 5 | 6 | 0 | 6 | 5 | 6 | 6 | 6 | 6 | 5 |
| fast | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 6 | 5 | 5 | 5 | 5 | 6 | 6 | 5 | 6 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 474 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 237 | 464 | 91226 | 11130642 | 1188343 | 13.56 |
