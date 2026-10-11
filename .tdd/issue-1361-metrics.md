### 📊 Metrics — issue 1361

Wall time for the issue: 1693 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1491.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 724 | 12489 | 32263 | 0.14 |
| expand | 2 | 1 | 0 | 0 | 87 | 29 | 10 | 20 | 3491 | 421373 | 79171 | 0.39 |
| migrate | 2 | 1 | 0 | 0 | 91 | 34 | 15 | 30 | 4136 | 688700 | 81107 | 0.43 |
| contract-a | 2 | 1 | 0 | 0 | 111 | 30 | 11 | 22 | 3598 | 481233 | 84830 | 0.42 |
| diff | 2 | 1 | 0 | 0 | 397 | 42 | 16 | 32 | 5109 | 754515 | 87123 | 0.48 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 188 | 68 | 24 | 48 | 7915 | 1007291 | 192424 | 0.95 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 505 | 72 | 29 | 58 | 9143 | 1351019 | 172070 | 0.91 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 87 | 0.39 |
| migrate | 0 | 0.00 | 91 | 0.43 |
| contract-a | 0 | 0.00 | 111 | 0.42 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| run_affordable gives its full answer — exit code, stdout, stderr, and the files and events step-cost.sh writes — when starting step-cost.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/step_cost.py gains that takes the working directory explicitly and returns the exit code and the step costs ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 3491 | 421373 | 79171 | 0.39 | unknown | unknown | unknown | unknown |  |  | full |
| run_affordable gives its full answer — exit code, stdout, stderr, and the files and events step-cost.sh writes — when starting step-cost.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/step_cost.py gains that takes the working directory explicitly and returns the exit code and the step costs ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 1⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 15 | 30 | 4136 | 688700 | 81107 | 0.43 | unknown | unknown | unknown | unknown |  |  | full |
| run_affordable gives its full answer — exit code, stdout, stderr, and the files and events step-cost.sh writes — when starting step-cost.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/step_cost.py gains that takes the working directory explicitly and returns the exit code and the step costs ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 1⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 11 | 22 | 3598 | 481233 | 84830 | 0.42 | unknown | unknown | unknown | unknown |  |  | full |
| No test of run_affordable fakes step-cost.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 16 | 32 | 5109 | 754515 | 87123 | 0.48 | 424 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 25 | 3 | 25 | 0 | 0 | 1 | 0 | 25 | 1 | 297 | 0 | 1 | 0 | 0 | 1 |
| fast | 26 | 24 | 25 | 25 | 25 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 53 | 106 | 17058 | 2358310 | 364494 | 1.86 |
