### 📊 Metrics — issue 2275

Wall time for the issue: 1805 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2278.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.90 over 43 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89190 |
| 2 | $0.02 | 89593 |
| 3 | $0.03 | 90603 |
| 4 | $0.03 | 92556 |
| 5 | $0.02 | 92987 |
| 6 | $0.02 | 93415 |
| 7 | $0.02 | 93722 |
| 8 | $0.02 | 94041 |
| 9 | $0.02 | 94594 |
| 10 | $0.05 | 98163 |
| 11 | $0.03 | 100035 |
| 12 | $0.03 | 101744 |
| 13 | $0.03 | 102617 |
| 14 | $0.02 | 103078 |
| 15 | $0.03 | 103778 |
| 16 | $0.03 | 104334 |
| 17 | $0.03 | 104885 |
| 18 | $0.03 | 105448 |
| 19 | $0.03 | 106800 |
| 20 | $0.03 | 107805 |
| 21 | $0.03 | 109223 |
| 22 | $0.03 | 109996 |
| 23 | $0.08 | 117154 |
| 24 | $0.03 | 118070 |
| 25 | $0.04 | 120162 |
| 26 | $0.03 | 120921 |
| 27 | $0.03 | 121374 |
| 28 | $0.03 | 122007 |
| 29 | $0.03 | 122652 |
| 30 | $0.04 | 124217 |
| 31 | $0.05 | 126798 |
| 32 | $0.03 | 127537 |
| 33 | $0.03 | 128616 |
| 34 | $0.04 | 130497 |
| 35 | $0.03 | 131225 |
| 36 | $0.03 | 131551 |
| 37 | $0.03 | 132110 |
| 38 | $0.03 | 132680 |
| 39 | $0.03 | 132966 |
| 40 | $0.03 | 133239 |
| 41 | $0.03 | 133752 |
| 42 | $0.03 | 134472 |
| 43 | $0.03 | 134999 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 874 | 0 | 30699 | 0.09 |
| diff | 4 | 1 | 1 | 0 | 273 | 119 | 24 | 46 | 10101 | 680796 | 107579 | 0.62 |
| red | 2 | 0 | 0 | 0 | 226 | 72 | 17 | 34 | 7789 | 537147 | 79432 | 0.50 |
| pin | 2 | 1 | 1 | 0 | 106 | 27 | 10 | 20 | 3288 | 284120 | 17480 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 3 | 2 | 0 | 205 | 67 | 19 | 38 | 7485 | 495484 | 77362 | 0.32 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 410 | 159 | 33 | 64 | 14567 | 1006579 | 157828 | 0.99 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 273 | 0.62 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 106 | 0.11 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The three `tree_audit` cases in skills/tdd/scripts/tests/py/test_fast_tier_guard.py (`test_the_guard_with_the_real_exemption_table_finds_no_offence…`, `test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale…`, `test_every_guard_clean_pytest_file_lives_under_tests_py_unit…`) obtain every sweep of a real directory (tests/py/unit, tests/py) through one module-level wrapper in that file that calls `guard.offences` over each real directory at most once per pytest session and shares the result, while each case keeps asserting what it asserts today (the 1641 case's monkeypatched real-keyed exemption still reported stale by no case); tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 119 | 24 | 46 | 10101 | 680796 | 107579 | 0.62 | 421 | 1/2 | unknown | unknown |  |  | full |
| A small case (no tree_audit mark, no real-tree sweep) in skills/tdd/scripts/tests/py/test_fast_tier_guard.py replaces `guard.offences` with an in-process spy, drives the shared sweep wrapper as the three tree_audit cases do (each real directory requested more than once), and asserts the spy saw each directory swept exactly once; tests only, no production change ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 99 | 27 | 54 | 11077 | 821267 | 96912 | 0.60 | unknown | 1/2 | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 22 | 24 | 23 |  |  |  |
| affected | 16 | 15 | 14 | 14 | 16 | 13 |
| target | 16 | 12 | 2 | 10 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 52 | 102 | 22052 | 1502063 | 235190 | 1.31 |
