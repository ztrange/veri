### 📊 Metrics — issue 2148

Wall time for the issue: 1808 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2164.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.81 over 44 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86597 |
| 2 | $0.02 | 87138 |
| 3 | $0.02 | 87812 |
| 4 | $0.02 | 88186 |
| 5 | $0.03 | 90161 |
| 6 | $0.02 | 90580 |
| 7 | $0.02 | 90834 |
| 8 | $0.02 | 91083 |
| 9 | $0.02 | 91371 |
| 10 | $0.02 | 92169 |
| 11 | $0.02 | 92869 |
| 12 | $0.02 | 93393 |
| 13 | $0.05 | 97417 |
| 14 | $0.02 | 98083 |
| 15 | $0.02 | 98370 |
| 16 | $0.03 | 99048 |
| 17 | $0.02 | 99592 |
| 18 | $0.02 | 100162 |
| 19 | $0.02 | 100744 |
| 20 | $0.03 | 102083 |
| 21 | $0.03 | 103130 |
| 22 | $0.03 | 104433 |
| 23 | $0.03 | 105176 |
| 24 | $0.08 | 112408 |
| 25 | $0.03 | 113179 |
| 26 | $0.03 | 113775 |
| 27 | $0.04 | 115572 |
| 28 | $0.03 | 116459 |
| 29 | $0.03 | 116852 |
| 30 | $0.03 | 117515 |
| 31 | $0.03 | 118700 |
| 32 | $0.03 | 119529 |
| 33 | $0.03 | 120414 |
| 34 | $0.03 | 120751 |
| 35 | $0.03 | 121386 |
| 36 | $0.03 | 121798 |
| 37 | $0.03 | 122584 |
| 38 | $0.03 | 122864 |
| 39 | $0.03 | 123558 |
| 40 | $0.03 | 124349 |
| 41 | $0.03 | 124916 |
| 42 | $0.03 | 125615 |
| 43 | $0.03 | 126236 |
| 44 | $0.03 | 126873 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 1 | 2 | 538 | 0 | 29740 | 0.08 |
| red | 4 | 1 | 1 | 0 | 204 | 101 | 17 | 32 | 8877 | 423299 | 91339 | 0.50 |
| green | 2 | 1 | 0 | 0 | 240 | 36 | 9 | 18 | 1996 | 241632 | 27247 | 0.11 |
| refactor | 2 | 1 | 0 | 0 | 68 | 15 | 6 | 12 | 912 | 150718 | 27082 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 4 | 1 | 0 | 287 | 57 | 13 | 26 | 4097 | 307496 | 73045 | 0.25 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 123 | 68 | 11 | 20 | 6736 | 264234 | 75132 | 0.42 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 113 | 34 | 9 | 18 | 1490 | 243919 | 27231 | 0.11 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 204 | 0.50 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After an in-process leg (pytest_leg.main driven through run_cli, pytest.main faked) returns or raises, PYTEST_LEG_SERIAL_SEEN in os.environ is what it was before the leg started: a leg started with the variable unset leaves it unset, and a leg started with it set to a prior value leaves that value restored; pinned by small in-process cases in skills/tdd/scripts/tests/py/test_pytest_leg.py, each checking os.environ after the leg ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 152 | 32 | 62 | 11785 | 815649 | 145668 | 0.71 | 675 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After an in-process leg (pytest_leg.main driven through run_cli, pytest.main faked) returns or raises, PYTEST_LEG_SERIAL_SEEN in os.environ is what it was before the leg started: a leg started with the variable unset leaves it unset, and a leg started with it set to a prior value leaves that value restored; pinned by small in-process cases in skills/tdd/scripts/tests/py/test_pytest_leg.py, each checking os.environ after the leg ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 68 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 20 | 16 | 24 | 24 | 21 | 17 |
| fast | 17 | 43 | 27 |  |  |  |
| target | 51 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 33 | 64 | 12323 | 815649 | 175408 | 0.79 |
