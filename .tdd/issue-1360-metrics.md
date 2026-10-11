### 📊 Metrics — issue 1360

Wall time for the issue: 1683 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1484.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 911 | 12489 | 32765 | 0.14 |
| diff | 6 | 3 | 0 | 0 | 331 | 156 | 42 | 82 | 20428 | 1960068 | 272561 | 1.69 |
| expand | 2 | 1 | 0 | 0 | 84 | 27 | 13 | 20 | 3220 | 422132 | 79352 | 0.39 |
| migrate | 2 | 1 | 0 | 0 | 83 | 26 | 12 | 24 | 3285 | 524424 | 80434 | 0.41 |
| contract-a | 2 | 1 | 0 | 0 | 113 | 31 | 12 | 24 | 3884 | 544709 | 87806 | 0.44 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 284 | 107 | 37 | 72 | 12975 | 1558189 | 285856 | 1.43 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 240 | 103 | 30 | 54 | 15137 | 1315855 | 184167 | 1.02 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 95 | 36 | 13 | 26 | 3616 | 589778 | 82895 | 0.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 84 | 0.39 |
| migrate | 0 | 0.00 | 83 | 0.41 |
| contract-a | 0 | 0.00 | 113 | 0.44 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, every test in tests/py/test_run_affordable.py that pins step-budget.sh's or step-cost.sh's path, argv or exit status asserts run-affordable's own exit code and stdout instead, driven by VERI_STEP_BUDGET and VERI_RUN_BUDGET in the case's environment and a .tdd/events.jsonl written in its own scratch tree (an exit 2 from a refused budget, an exit 3 from a log with no step over two leaves), green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 14 | 26 | 11203 | 674438 | 103794 | 0.59 | 167 | n/a | n/a | n/a |  |  | full |
| run_affordable gives its full answer — exit code, stdout, stderr — when starting step-budget.sh as a process would fail, in a case that refuses that start at the process boundary, calling a function veri/step_budget.py exposes that returns the code and both budgets ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 13 | 20 | 3220 | 422132 | 79352 | 0.39 | unknown | unknown | unknown | unknown |  |  | full |
| run_affordable gives its full answer — exit code, stdout, stderr — when starting step-budget.sh as a process would fail, in a case that refuses that start at the process boundary, calling a function veri/step_budget.py exposes that returns the code and both budgets ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 12 | 24 | 3285 | 524424 | 80434 | 0.41 | unknown | unknown | unknown | unknown |  |  | full |
| run_affordable gives its full answer — exit code, stdout, stderr — when starting step-budget.sh as a process would fail, in a case that refuses that start at the process boundary, calling a function veri/step_budget.py exposes that returns the code and both budgets ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 12 | 24 | 3884 | 544709 | 87806 | 0.44 | unknown | unknown | unknown | unknown |  |  | full |
| No test of run_affordable fakes step-budget.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 83 | 28 | 56 | 9225 | 1285630 | 168767 | 1.10 | 258 | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 24 | 26 | 27 | 24 | 25 | 25 | 25 | 24 |  |  |  |  |
| affected | 2 | 26 | 0 | 0 | 25 | 0 | 2 | 25 | 1 | 2 | 2 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 80 | 152 | 31728 | 3463822 | 552918 | 3.08 |
