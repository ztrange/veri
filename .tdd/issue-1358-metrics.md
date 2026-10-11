### 📊 Metrics — issue 1358

Wall time for the issue: 3147 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1477.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 983 | 12489 | 32509 | 0.14 |
| diff | 4 | 2 | 0 | 0 | 574 | 90 | 23 | 44 | 10126 | 995629 | 176440 | 0.91 |
| expand | 2 | 1 | 0 | 0 | 89 | 21 | 10 | 18 | 2834 | 365941 | 78379 | 0.38 |
| migrate | 2 | 1 | 0 | 0 | 375 | 33 | 15 | 28 | 3991 | 639449 | 82961 | 0.44 |
| contract-a | 2 | 1 | 0 | 0 | 358 | 27 | 12 | 24 | 3207 | 539550 | 84322 | 0.42 |
| red | 1 | 0 | 0 | 0 | 23 | 20 | 4 | 8 | 2647 | 173454 | 45749 | 0.23 |
| pin | 1 | 1 | 0 | 0 | 16 | 13 | 4 | 8 | 1621 | 159901 | 40208 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 295 | 108 | 32 | 64 | 11776 | 1339675 | 280655 | 1.37 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 1149 | 103 | 37 | 68 | 13633 | 1546738 | 259913 | 1.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 89 | 0.38 |
| migrate | 0 | 0.00 | 375 | 0.44 |
| contract-a | 0 | 0.00 | 358 | 0.42 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, the tests in tests/py/test_over_budget.py that pin time-budget.sh's path, argv, printed lines or exit status assert over-budget's own exit code and stdout under VERI_UNIT_BUDGET and VERI_TIME_WARN_RATIO set in the case's environment instead, an exit 2 driven by a refused tunable, the OSError-start case dropped, green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 13 | 24 | 6502 | 563583 | 92180 | 0.49 | 220 | n/a | n/a | n/a |  |  | full |
| over_budget gives its full answer — exit code, stdout and stderr — when starting time-budget.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/time_budget.py gains that returns the exit code and the two values ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 10 | 18 | 2834 | 365941 | 78379 | 0.38 | unknown | unknown | unknown | unknown |  |  | full |
| over_budget gives its full answer — exit code, stdout and stderr — when starting time-budget.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/time_budget.py gains that returns the exit code and the two values ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 15 | 28 | 3991 | 639449 | 82961 | 0.44 | unknown | unknown | unknown | unknown |  |  | full |
| over_budget gives its full answer — exit code, stdout and stderr — when starting time-budget.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/time_budget.py gains that returns the exit code and the two values ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 12 | 24 | 3207 | 539550 | 84322 | 0.42 | unknown | unknown | unknown | unknown |  |  | full |
| A case in tests/py/test_over_budget.py refuses any start of time-budget.sh at the process boundary and asserts over-budget's exit code, stdout and stderr under VERI_UNIT_BUDGET and VERI_TIME_WARN_RATIO — over budget, not over budget, and a refused tunable's exit 2 with time-budget's stderr line — are what they were when time-budget.sh ran as a process ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 8 | 16 | 4268 | 333355 | 85957 | 0.42 | unknown | unknown | unknown | unknown |  |  | pin |
| No test of over_budget fakes time-budget.sh at the process boundary any longer, each such test rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 10 | 20 | 3624 | 432046 | 84260 | 0.42 | 401 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 32 | 31 | 31 | 26 | 23 | 24 |  |  |  |
| affected | 30 | 29 | 0 | 309 | 1 | 301 | 1 | 0 | 297 |
| target | 0 | 1 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 69 | 132 | 25409 | 2886413 | 540568 | 2.71 |
