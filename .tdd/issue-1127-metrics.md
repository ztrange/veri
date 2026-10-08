### 📊 Metrics — issue 1127

Wall time for the issue: 5317 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1179.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 1034 | 12385 | 31681 | 0.14 |
| red | 12 | 5 | 0 | 0 | 505 | 441 | 91 | 180 | 42727 | 4598566 | 555734 | 5.35 |
| green | 10 | 5 | 0 | 0 | 1167 | 204 | 63 | 126 | 19273 | 2780162 | 404487 | 3.31 |
| refactor | 10 | 5 | 0 | 0 | 801 | 173 | 53 | 104 | 15795 | 2193716 | 407120 | 3.10 |
| pin | 2 | 2 | 0 | 0 | 42 | 35 | 9 | 18 | 3273 | 365654 | 79410 | 0.42 |
| predicate | 3 | 0 | 0 | 0 | 55 | 45 | 9 | 18 | 3689 | 309894 | 110888 | 1.02 |
| structural | 2 | 0 | 0 | 0 | 92 | 60 | 16 | 28 | 4357 | 614005 | 79083 | 0.84 |
| transform | 2 | 2 | 0 | 0 | 483 | 44 | 15 | 30 | 5063 | 663170 | 78362 | 0.50 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 20 | 20 | 0 | 0 | 2064 | 352 | 112 | 222 | 35896 | 4715050 | 786922 | 4.45 |
| developer | claude-opus-5-5 | 22 | 0 | 0 | 0 | 1093 | 658 | 145 | 284 | 59315 | 6822502 | 959843 | 10.23 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| orchestrate.sh with VERI_CONDUCTOR_CTX_BUDGET=0100000 reads the budget as decimal 100000: a conductor whose context is 50000 after its step-done call is not stopped, and one whose context is 100001 is; the octal 0100000 assertion in test_orchestrate.py's leading-zero test is replaced by this one ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 33 | 66 | 11521 | 1408153 | 244445 | 1.94 | 299 | unknown | 0/5 | nothing-left |  |  | full |
| orchestrate.sh with VERI_CONDUCTOR_CTX_BUDGET=08 stops a conductor once its context is over 8 tokens after its step-done call, with no "value too great for base" line on stderr; the 08/09 never-stopping assertions in test_orchestrate.py's leading-zero test are replaced by this one ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 108 | 30 | 60 | 9812 | 1266098 | 242549 | 1.88 | 314 | unknown | 0/5 | structural-owed |  |  | full |
| parallel-conductors.sh with VERI_CONDUCTOR_CTX_BUDGET=0100000 reads the budget as decimal 100000: a conductor whose context is 50000 after its step-done call is neither stopped nor relaunched; the 0100000-is-octal-32768 case in test_parallel_conductors.py is replaced by this one ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 37 | 74 | 12441 | 1638247 | 251038 | 2.04 | 443 | unknown | 0/5 | structural-owed |  |  | full |
| parallel-conductors.sh with VERI_CONDUCTOR_CTX_BUDGET=08 stops and relaunches a conductor once its context is over 8 tokens after its step-done call, with no "value too great for base" line on stderr; the 08-never-stops and 09-never-stops cases in test_parallel_conductors.py are replaced by this one ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 37 | 74 | 12826 | 1662358 | 254467 | 2.09 | 415 | unknown | 0/5 | nothing-structural |  |  | full |
| parallel-conductors.sh with VERI_CONDUCTOR_CTX_BUDGET=09 stops and relaunches a conductor once its context is over 9 tokens after its step-done call, with no "value too great for base" line on stderr ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 13 | 26 | 5579 | 585728 | 81608 | 0.71 | unknown | unknown | unknown | unknown |  |  | pin |
| with VERI_CONDUCTOR_CTX_BUDGET=100000, and with it unset (default 120000), orchestrate.sh and parallel-conductors.sh stop a conductor exactly when its context after a step-done call is over that number, as today ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 15 | 28 | 7673 | 692321 | 95350 | 0.87 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_parallel_conductors.py — FAILED test_veri_conductor_ctx_budget_of_100000_or_unset_stops_a_conductor_exactly_when_its_context_is_over_it_1127[unset-over-120000-#1127]: AssertionError at test_parallel_conductors.py:695, At index 0 diff: [] != [(424242, <Signals.SIGTERM: 15>)] (passes under make unit, fails under make test) ⟦suite-repair⟧ ⟦criterion 3⟧ | 13 | 5 | 0 | 0 | 0 | 0 | 374 | 91 | 176 | 34325 | 4272262 | 545627 | 5.01 | 1275 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| orchestrate.sh with VERI_CONDUCTOR_CTX_BUDGET=0100000 reads the budget as decimal 100000: a conductor whose context is 50000 after its step-done call is not stopped, and one whose context is 100001 is; the octal 0100000 assertion in test_orchestrate.py's leading-zero test is replaced by this one ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 66 | 0.63 |
| orchestrate.sh with VERI_CONDUCTOR_CTX_BUDGET=08 stops a conductor once its context is over 8 tokens after its step-done call, with no "value too great for base" line on stderr; the 08/09 never-stopping assertions in test_orchestrate.py's leading-zero test are replaced by this one ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 82 | 0.56 |
| parallel-conductors.sh with VERI_CONDUCTOR_CTX_BUDGET=0100000 reads the budget as decimal 100000: a conductor whose context is 50000 after its step-done call is neither stopped nor relaunched; the 0100000-is-octal-32768 case in test_parallel_conductors.py is replaced by this one ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 100 | 0.68 |
| parallel-conductors.sh with VERI_CONDUCTOR_CTX_BUDGET=08 stops and relaunches a conductor once its context is over 8 tokens after its step-done call, with no "value too great for base" line on stderr; the 08-never-stops and 09-never-stops cases in test_parallel_conductors.py are replaced by this one ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 62 | 0.60 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_parallel_conductors.py — FAILED test_veri_conductor_ctx_budget_of_100000_or_unset_stops_a_conductor_exactly_when_its_context_is_over_it_1127[unset-over-120000-#1127]: AssertionError at test_parallel_conductors.py:695, At index 0 diff: [] != [(424242, <Signals.SIGTERM: 15>)] (passes under make unit, fails under make test) ⟦suite-repair⟧ ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 491 | 0.63 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 9 | 8 | 0 | 0 | 8 | 1 | 1 | 8 | 8 | 8 | 21 | 8 | 0 | 0 | 1 | 34 | 0 | 34 | 0 | 0 | 34 | 0 | 1 | 34 | 0 | 35 | 1 | 1 | 0 | 5 | 0 | 5 | 35 | 0 | 0 | 0 | 415 | 9 | 415 | 19 | 6 | 4 | 6 |
| fast | 22 | 22 | 21 | 20 | 21 | 20 | 21 | 21 | 22 | 21 | 21 | 22 | 22 | 412 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 21 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 257 | 506 | 95211 | 11537552 | 1746765 | 14.68 |
