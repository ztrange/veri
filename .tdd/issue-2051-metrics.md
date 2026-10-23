### 📊 Metrics — issue 2051

Wall time for the issue: 1379 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2210.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.72 over 40 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87197 |
| 2 | $0.02 | 87562 |
| 3 | $0.02 | 88359 |
| 4 | $0.02 | 88746 |
| 5 | $0.03 | 90624 |
| 6 | $0.02 | 90990 |
| 7 | $0.02 | 91463 |
| 8 | $0.02 | 91956 |
| 9 | $0.02 | 92517 |
| 10 | $0.03 | 93368 |
| 11 | $0.03 | 95181 |
| 12 | $0.03 | 96577 |
| 13 | $0.07 | 102975 |
| 14 | $0.03 | 104646 |
| 15 | $0.03 | 105583 |
| 16 | $0.03 | 106281 |
| 17 | $0.03 | 107240 |
| 18 | $0.03 | 108603 |
| 19 | $0.03 | 109452 |
| 20 | $0.03 | 110075 |
| 21 | $0.05 | 113506 |
| 22 | $0.03 | 114464 |
| 23 | $0.02 | 114682 |
| 24 | $0.03 | 115267 |
| 25 | $0.03 | 115835 |
| 26 | $0.03 | 116758 |
| 27 | $0.03 | 117317 |
| 28 | $0.03 | 118150 |
| 29 | $0.03 | 118796 |
| 30 | $0.03 | 119415 |
| 31 | $0.03 | 119721 |
| 32 | $0.03 | 120300 |
| 33 | $0.04 | 121678 |
| 34 | $0.03 | 122181 |
| 35 | $0.03 | 122666 |
| 36 | $0.03 | 123366 |
| 37 | $0.03 | 124558 |
| 38 | $0.03 | 124852 |
| 39 | $0.03 | 125141 |
| 40 | $0.03 | 125448 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 2 | 4 | 910 | 30235 | 30890 | 0.09 |
| red | 1 | 0 | 0 | 0 | 82 | 35 | 6 | 12 | 3621 | 189524 | 43173 | 0.16 |
| pin | 1 | 1 | 0 | 0 | 49 | 22 | 4 | 8 | 1205 | 104411 | 13503 | 0.06 |
| diff | 2 | 1 | 0 | 0 | 129 | 53 | 11 | 22 | 3260 | 303893 | 28846 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 114 | 45 | 9 | 18 | 2913 | 209784 | 58353 | 0.20 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 158 | 73 | 14 | 28 | 6083 | 418279 | 58059 | 0.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A case running the real pytest_leg.py as a child over a planted tests tree (so the child gets pytest_leg.py's own PYTEST_PLUGINS wiring) asserts that a planted case's tmp_path is the one private_tmp_path creates — a directory of mode 0700 directly under the run's veri-pytest-* basetemp, named by private_tmp_path's make_tmp_path (the case's name, an underscore, then mkdtemp's random suffix), not stock pytest's numbered tmp_path — so that removing private_tmp_path from PYTEST_PLUGINS in pytest_leg.py turns the case red (a medium case in tests/py/test_pytest_leg.py, carrying a process mark; no production change) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 10 | 20 | 4826 | 293935 | 56676 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| The existing case test_each_case_gets_a_private_empty_tmp_path_that_exists_and_a_file_left_in_one_is_absent_from_the_next in tests/py/test_conftest.py loads private_tmp_path in its child pytest session, so the tmp_path it pins is private_tmp_path's and not stock pytest's; if loading it there is not possible, the case is renamed instead to say it pins stock pytest's tmp_path (a test-only change; no production change) ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 11 | 22 | 3260 | 303893 | 28846 | 0.14 | 204 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 13 | 16 | 16 | 16 |
| target | 13 | 9 |  |  |
| fast | 17 | 17 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 23 | 46 | 8996 | 628063 | 116412 | 0.44 |
