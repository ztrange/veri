### 📊 Metrics — issue 2453

Wall time for the issue: 1699 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2492.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.95 over 46 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88651 tokens, largest 133405 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88651 |
| 2 | $0.03 | 90382 |
| 3 | $0.03 | 92307 |
| 4 | $0.02 | 92740 |
| 5 | $0.02 | 93033 |
| 6 | $0.02 | 93332 |
| 7 | $0.02 | 93621 |
| 8 | $0.02 | 94361 |
| 9 | $0.03 | 95647 |
| 10 | $0.03 | 96807 |
| 11 | $0.02 | 97489 |
| 12 | $0.02 | 98015 |
| 13 | $0.03 | 98860 |
| 14 | $0.03 | 100072 |
| 15 | $0.03 | 100786 |
| 16 | $0.02 | 101128 |
| 17 | $0.03 | 101804 |
| 18 | $0.03 | 102784 |
| 19 | $0.03 | 103770 |
| 20 | $0.03 | 104538 |
| 21 | $0.08 | 112369 |
| 22 | $0.04 | 114182 |
| 23 | $0.03 | 114927 |
| 24 | $0.03 | 115583 |
| 25 | $0.03 | 116546 |
| 26 | $0.03 | 117936 |
| 27 | $0.03 | 118654 |
| 28 | $0.03 | 119385 |
| 29 | $0.03 | 119803 |
| 30 | $0.03 | 120966 |
| 31 | $0.03 | 121685 |
| 32 | $0.04 | 123253 |
| 33 | $0.03 | 123888 |
| 34 | $0.03 | 125157 |
| 35 | $0.03 | 126146 |
| 36 | $0.04 | 127546 |
| 37 | $0.05 | 129988 |
| 38 | $0.03 | 130693 |
| 39 | $0.03 | 130930 |
| 40 | $0.03 | 131456 |
| 41 | $0.03 | 131910 |
| 42 | $0.03 | 132151 |
| 43 | $0.03 | 132364 |
| 44 | $0.03 | 132778 |
| 45 | $0.03 | 133121 |
| 46 | $0.03 | 133405 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 2 | 4 | 813 | 32794 | 33258 | 0.09 |
| red | 5 | 2 | 0 | 0 | 98 | 74 | 24 | 48 | 9093 | 770921 | 121176 | 0.47 |
| green | 6 | 2 | 1 | 0 | 239 | 65 | 25 | 48 | 5759 | 679358 | 96931 | 0.47 |
| refactor | 3 | 1 | 0 | 0 | 53 | 25 | 10 | 20 | 2344 | 282877 | 47676 | 0.17 |
| pin | 1 | 1 | 0 | 0 | 15 | 7 | 3 | 6 | 768 | 79403 | 15381 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 212 | 72 | 23 | 46 | 7258 | 605025 | 127914 | 0.45 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 131 | 84 | 32 | 62 | 9840 | 995916 | 138253 | 0.54 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 73 | 24 | 9 | 18 | 1679 | 244412 | 48255 | 0.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 169 | 0.35 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A `SUPERSEDED:` line whose case is one the step itself records (via `_recorded_cases`) makes `_superseded` write no "no defined test case resolves" line on stderr, while it still leaves that case out of the returned cases (a small unit case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py, fails on the current code) ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 93 | 32 | 64 | 9039 | 922024 | 155236 | 0.68 | 425 | 1/2 | 1/5 | nothing-left |  |  | full |
| A `SUPERSEDED:` line whose body yields no case name at all makes `_superseded` write a stderr line saying the line carried no case name, never "no defined test case resolves" (a small unit case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py) ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 55 | 22 | 42 | 6012 | 647638 | 89266 | 0.35 | 203 | unknown | 0/5 | nothing-left |  |  | full |
| A `SUPERSEDED:` line whose extracted case name resolves to no defined test case still makes `_superseded` write the "no defined test case resolves" line on stderr (a small unit pin case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py, no production change) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 16 | 2913 | 242897 | 36662 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A `SUPERSEDED:` line whose case is one the step itself records (via `_recorded_cases`) makes `_superseded` write no "no defined test case resolves" line on stderr, while it still leaves that case out of the returned cases (a small unit case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py, fails on the current code) ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 47 | 0.13 |
| A `SUPERSEDED:` line whose body yields no case name at all makes `_superseded` write a stderr line saying the line carried no case name, never "no defined test case resolves" (a small unit case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 2 | 2 | 1 | 3 | 2 | 2 | 1 | 2 | 2 | 2 | 2 |
| fast | 19 | 20 | 18 | 18 | 17 | 18 | 18 |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 64 | 126 | 18777 | 1845353 | 314422 | 1.26 |
