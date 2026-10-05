### 📊 Metrics — issue 899

Wall time for the issue: 1994 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/908.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 976 | 11866 | 30688 | 0.13 |
| red | 6 | 2 | 0 | 0 | 287 | 239 | 54 | 106 | 20788 | 3103486 | 329318 | 3.33 |
| green | 4 | 2 | 0 | 0 | 255 | 93 | 26 | 50 | 9229 | 1096981 | 162956 | 1.36 |
| refactor | 4 | 2 | 0 | 0 | 153 | 78 | 21 | 42 | 6840 | 890601 | 160456 | 1.27 |
| pin | 1 | 1 | 0 | 0 | 29 | 16 | 5 | 10 | 1750 | 205408 | 40123 | 0.22 |
| predicate | 1 | 0 | 0 | 0 | 24 | 21 | 4 | 8 | 1471 | 149035 | 35948 | 0.35 |
| structural | 1 | 0 | 0 | 0 | 31 | 23 | 6 | 12 | 2039 | 253823 | 38744 | 0.40 |
| transform | 1 | 1 | 0 | 0 | 34 | 13 | 5 | 10 | 1151 | 195770 | 36217 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 280 | 116 | 37 | 72 | 12549 | 1377986 | 338491 | 1.76 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 542 | 374 | 85 | 168 | 31695 | 4528984 | 495959 | 5.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 24 | 0.35 |
| structural | 0 | 0.00 | 31 | 0.40 |
| transform | 0 | 0.00 | 34 | 0.20 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| make unit UNIT_TESTS naming one shell suite runs that suite and starts no pytest case, and exits 0 for a passing suite even while a pytest case elsewhere under tests/py is red ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 146 | 39 | 74 | 12914 | 1852680 | 271073 | 2.30 | 336 | unknown | 0/5 | nothing-left |  |  | full |
| make unit UNIT_TESTS naming a set that includes a tests/py test_*.py file runs the pytest leg over that file only, not every test_*.py under tests/py | 7 | 3 | 0 | 0 | 0 | 0 | 213 | 51 | 102 | 19422 | 2473834 | 305133 | 2.81 | 447 | 1/2 | 1/5 | structural-owed |  |  | full |
| a plain make unit, with no UNIT_TESTS on the command line, still runs every suite under tests/unit and the full pytest leg, and exits non-zero when a pytest case under tests/py fails ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 16 | 32 | 6271 | 969962 | 116647 | 1.07 | unknown | unknown | unknown | unknown |  |  | pin |
| unit-tier.test.sh passes under the repository's full test command, every one of its nested make unit calls naming UNIT_TESTS so none runs the pytest leg ⟦full-suite⟧ ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 57 | 15 | 30 | 4661 | 598628 | 110909 | 0.94 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| make unit UNIT_TESTS naming one shell suite runs that suite and starts no pytest case, and exits 0 for a passing suite even while a pytest case elsewhere under tests/py is red ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 53 | 0.58 |
| make unit UNIT_TESTS naming a set that includes a tests/py test_*.py file runs the pytest leg over that file only, not every test_*.py under tests/py | 1 | 1/5 | structural-owed | PASS | 0 | 100 | 0.69 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 25 | 1 | 4 | 4 | 4 | 4 | 23 | 25 | 24 | 3 | 4 | 5 | 4 |
| fast | 14 | 16 | 16 | 16 | 14 | 14 |  |  |  |  |  |  |  |  |  |
| target | 4 | 4 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 122 | 240 | 44244 | 5906970 | 834450 | 7.26 |
