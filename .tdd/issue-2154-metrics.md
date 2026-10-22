### 📊 Metrics — issue 2154

Wall time for the issue: 1555 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2161.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.41 over 33 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86238 |
| 2 | $0.02 | 86752 |
| 3 | $0.03 | 88643 |
| 4 | $0.02 | 89421 |
| 5 | $0.02 | 89812 |
| 6 | $0.02 | 90171 |
| 7 | $0.02 | 90524 |
| 8 | $0.02 | 91103 |
| 9 | $0.03 | 92826 |
| 10 | $0.03 | 94187 |
| 11 | $0.02 | 94516 |
| 12 | $0.02 | 95197 |
| 13 | $0.02 | 95753 |
| 14 | $0.03 | 96526 |
| 15 | $0.04 | 98563 |
| 16 | $0.03 | 99472 |
| 17 | $0.03 | 100535 |
| 18 | $0.03 | 101325 |
| 19 | $0.03 | 102342 |
| 20 | $0.04 | 104724 |
| 21 | $0.03 | 105460 |
| 22 | $0.03 | 106307 |
| 23 | $0.03 | 107045 |
| 24 | $0.02 | 107469 |
| 25 | $0.03 | 108222 |
| 26 | $0.03 | 109375 |
| 27 | $0.03 | 109917 |
| 28 | $0.02 | 110208 |
| 29 | $0.02 | 110519 |
| 30 | $0.03 | 110903 |
| 31 | $0.03 | 111416 |
| 32 | $0.02 | 111729 |
| 33 | $0.03 | 112135 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 6 | 1 | 2 | 744 | 0 | 29869 | 0.08 |
| red | 2 | 1 | 0 | 0 | 90 | 58 | 9 | 16 | 4034 | 215743 | 53398 | 0.20 |
| green | 2 | 1 | 0 | 0 | 306 | 38 | 10 | 20 | 3540 | 283182 | 31461 | 0.14 |
| refactor | 2 | 1 | 0 | 0 | 65 | 16 | 7 | 12 | 1426 | 151036 | 28252 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 247 | 53 | 12 | 22 | 4507 | 257014 | 73541 | 0.25 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 225 | 65 | 15 | 28 | 5237 | 392947 | 69439 | 0.27 |

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
| A guard case, in a new unit-tier test file of its own (not test_recipe_one_pytest_process.py), reads every case in skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py that starts make and fails, naming the case, when its @pytest.mark.timeout (default 30 s, VERI_PYTEST_TIMEOUT, when unmarked) is below 60 s per make call it makes; Green raises the marks in that file so every such case meets it, the four-make two-worker case to at least 240 s with the reason stated beside the mark ⟦guard-subject: skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 26 | 48 | 9000 | 649961 | 113111 | 0.44 | 566 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A guard case, in a new unit-tier test file of its own (not test_recipe_one_pytest_process.py), reads every case in skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py that starts make and fails, naming the case, when its @pytest.mark.timeout (default 30 s, VERI_PYTEST_TIMEOUT, when unmarked) is below 60 s per make call it makes; Green raises the marks in that file so every such case meets it, the four-make two-worker case to at least 240 s with the reason stated beside the mark ⟦guard-subject: skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 65 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 10 | 43 | 46 | 11 |
| fast | 18 | 19 | 16 |  |  |
| target | 14 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 27 | 50 | 9744 | 649961 | 142980 | 0.52 |
