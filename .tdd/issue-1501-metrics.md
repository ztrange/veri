### 📊 Metrics — issue 1501

Wall time for the issue: 1840 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1690.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 31 | 23 | 4 | 8 | 2663 | 136961 | 89458 | 0.40 |
| red | 3 | 1 | 0 | 0 | 208 | 172 | 39 | 78 | 21514 | 2484580 | 178870 | 1.18 |
| green | 2 | 1 | 0 | 0 | 112 | 31 | 13 | 20 | 3534 | 484250 | 93965 | 0.46 |
| refactor | 2 | 1 | 0 | 0 | 101 | 38 | 14 | 28 | 3569 | 724474 | 95205 | 0.49 |
| pin | 1 | 1 | 0 | 0 | 21 | 15 | 4 | 8 | 1687 | 176995 | 47098 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 190 | 90 | 24 | 46 | 9624 | 1031645 | 276439 | 1.31 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 283 | 189 | 50 | 96 | 23343 | 2975615 | 228157 | 1.44 |

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
| After mutation-parity.sh checks a row whose patch is a same-size edit to a module under skills/tdd/scripts/veri/, applied and reverted within one second, and whose bash suite imports that module under the mutation, no bytecode of the mutated source is left anywhere Python would load it: the row's own unmutated runs and an import of the module after the tool exits both run the current source (a medium pytest case marked @pytest.mark.process, since it starts a real bash suite and python3; red with failed_cases() given the inherited environment) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 43 | 80 | 15504 | 2153346 | 300081 | 1.57 | 387 | unknown | 1/5 | nothing-structural |  |  | full |
| Regression pin for the pytest half, already satisfied today by pytest() running with PYTHONDONTWRITEBYTECODE=1: when the row's suite is a pytest suite importing the mutated module, no mutated bytecode is left after the tool exits and the row's unmutated runs read the current source (a medium pytest case marked @pytest.mark.process; expected to pass against unmodified code and take the pin path, failing once that environment setting is removed) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 112 | 27 | 54 | 14800 | 1716953 | 115057 | 0.78 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After mutation-parity.sh checks a row whose patch is a same-size edit to a module under skills/tdd/scripts/veri/, applied and reverted within one second, and whose bash suite imports that module under the mutation, no bytecode of the mutated source is left anywhere Python would load it: the row's own unmutated runs and an import of the module after the tool exits both run the current source (a medium pytest case marked @pytest.mark.process, since it starts a real bash suite and python3; red with failed_cases() given the inherited environment) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 101 | 0.49 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 18 | 18 | 18 | 17 | 1 | 2 | 2 | 2 |
| fast | 16 | 16 | 16 |  |  |  |  |  |  |
| target | 1 | 2 | 1 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 74 | 142 | 32967 | 4007260 | 504596 | 2.75 |
