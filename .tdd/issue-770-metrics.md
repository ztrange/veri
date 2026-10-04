### 📊 Metrics — issue 770

Wall time for the issue: 4112 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/833.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 39 | 34 | 2 | 4 | 3030 | 66575 | 48427 | 0.46 |
| red | 10 | 3 | 0 | 0 | 464 | 383 | 76 | 150 | 32099 | 3950017 | 493620 | 5.38 |
| pin | 4 | 4 | 0 | 0 | 114 | 87 | 18 | 36 | 8269 | 810277 | 181871 | 1.78 |
| green | 8 | 3 | 1 | 0 | 733 | 292 | 71 | 134 | 27333 | 3605354 | 361019 | 4.16 |
| refactor | 6 | 3 | 0 | 0 | 267 | 111 | 31 | 60 | 10238 | 1412407 | 277947 | 2.71 |
| diff | 6 | 3 | 0 | 0 | 194 | 102 | 28 | 56 | 9655 | 1306272 | 272214 | 2.63 |
| predicate | 1 | 0 | 0 | 0 | 12 | 8 | 3 | 6 | 600 | 118230 | 41649 | 0.37 |
| structural | 1 | 0 | 0 | 0 | 26 | 17 | 6 | 10 | 1595 | 229001 | 43782 | 0.43 |
| transform | 1 | 1 | 0 | 0 | 30 | 14 | 4 | 8 | 1505 | 170233 | 42545 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 19 | 18 | 1 | 0 | 949 | 468 | 102 | 200 | 44454 | 4813849 | 847100 | 8.63 |
| developer | claude-opus-5-5 | 19 | 0 | 0 | 0 | 930 | 580 | 137 | 264 | 49870 | 6854517 | 915974 | 9.70 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 438 | 2.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 30 | 0.40 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| time-budget.sh run with VERI_UNIT_BUDGET=ten exits 2 with nothing on stdout and stderr exactly the one line `time-budget: VERI_UNIT_BUDGET must be a number of seconds: ten` (a floor case in tests/time-budget.test.sh, written against the bash script before the port) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 15 | 30 | 5366 | 772020 | 94158 | 1.02 | unknown | unknown | unknown | unknown |  |  | pin |
| time-budget.sh, run through a symlink to the skill directory and from another working directory, prints the same stdout and stderr and exits with the same code as when run in place, for both tunables unset and for VERI_UNIT_BUDGET=ten (a case in tests/time-budget.test.sh) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 14 | 28 | 7208 | 733907 | 99408 | 1.09 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.time_budget.main(argv) returns 0 with `10` then `1.5` on stdout for `[]` and for `["--bogus"]` with both variables unset, and 2 with nothing on stdout and stderr exactly `time-budget: VERI_UNIT_BUDGET must be a number of seconds: ten` for `[]` with VERI_UNIT_BUDGET=ten (tests/py/test_time_budget.py, faking only the environment), and time-budget.sh is removed from migration slice 9's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 284 | 65 | 124 | 25028 | 3353949 | 359585 | 4.05 | 718 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.time_budget.main([]) with VERI_TIME_WARN_RATIO=1,5 returns 2 with nothing on stdout and stderr exactly `time-budget: VERI_TIME_WARN_RATIO must be a number: 1,5`; with both variables bad it prints only the VERI_UNIT_BUDGET line (tests/py/test_time_budget.py, faking only the environment, never patching a function of veri.time_budget) ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 185 | 42 | 78 | 14234 | 1910598 | 278149 | 2.89 | 389 | unknown | 1/5 | nothing-structural |  |  | full |
| veri.time_budget.main([]) treats a set-but-empty variable as unset (VERI_UNIT_BUDGET= prints `10`) and accepts exactly `^[0-9]+(\.[0-9]+)?$` over the whole value: `1.`, `-1`, `1,5` and a value with a trailing newline are refused with return 2, while `010` and `01.50` are accepted and printed as given, never normalised (tests/py/test_time_budget.py, faking only the environment, never patching a function of veri.time_budget) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 11 | 22 | 5236 | 526253 | 92476 | 0.95 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.time_budget.main([]) echoes both values byte for byte: a value holding a non-UTF-8 byte reaches stdout as that byte when accepted and the diagnostic on stderr as that byte when refused, never as `\udcff` (tests/py/test_time_budget.py, faking only the environment and the standard streams, never patching a function of veri.time_budget) ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 35 | 70 | 15840 | 1762941 | 295134 | 3.03 | 347 | unknown | 0/5 | structural-owed |  |  | full |
| veri.time_budget.main([]) with sys.stdout set to None, as Python leaves it when fd 1 is closed, raises out of main rather than returning 0 — no wrapper converts it to a return code — so the shim exits 1, as the bash script's failed echo does (tests/py/test_time_budget.py, faking only the standard streams, never patching a function of veri.time_budget) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 14 | 28 | 5027 | 718387 | 95547 | 1.01 | unknown | unknown | unknown | unknown |  |  | pin |
| time-budget.sh is a /bin/sh shim that execs python3 on veri/time_budget.py once per invocation, holding no Python source, carrying a lowercase `usage: time-budget.sh` line in its header and citing no issue number in any comment; veri/time_budget.py carries no wrapper turning an uncaught exception into exit 2; every case in tests/time-budget.test.sh passes with its assertions unmodified, in a commit that precedes any cut, whose diff, in the test suites, touches only copy lines and stub libs and changes no assertion ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 15 | 30 | 5646 | 778160 | 98670 | 1.06 | 130 | unknown | unknown | unknown |  |  | full |
| tests/time-budget.test.sh holds the survivors and the floor — its original case (exit 0 and exit 2), the exact VERI_UNIT_BUDGET=ten stderr case and the symlink case — with no pre-existing case's assertions changed; no case is cut ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 6 | 12 | 1687 | 238862 | 89046 | 0.79 | 52 | unknown | unknown | unknown |  |  | full |
| tests/over-budget.test.sh, tests/unit/comment-class.test.sh and tests/unit/exit-contract.test.sh are unchanged by the branch, and tests/unit/missing-argument-exit.test.sh is changed only by the removal of time-budget.sh from migration slice 9's list ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 7 | 14 | 2322 | 289250 | 84498 | 0.78 | 72 | unknown | unknown | unknown |  |  | full |
| make test is green, tests/time-budget.test.sh, tests/over-budget.test.sh, tests/unit/missing-argument-exit.test.sh, tests/unit/comment-class.test.sh and tests/unit/exit-contract.test.sh among its suites ⟦full-suite⟧ ⟦criterion 5⟧ | 1 | 1 | 0 | 0 | 0 | 0 | 14 | 4 | 8 | 1505 | 170233 | 42545 | 0.40 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.time_budget.main(argv) returns 0 with `10` then `1.5` on stdout for `[]` and for `["--bogus"]` with both variables unset, and 2 with nothing on stdout and stderr exactly `time-budget: VERI_UNIT_BUDGET must be a number of seconds: ten` for `[]` with VERI_UNIT_BUDGET=ten (tests/py/test_time_budget.py, faking only the environment), and time-budget.sh is removed from migration slice 9's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 108 | 0.90 |
| veri.time_budget.main([]) with VERI_TIME_WARN_RATIO=1,5 returns 2 with nothing on stdout and stderr exactly `time-budget: VERI_TIME_WARN_RATIO must be a number: 1,5`; with both variables bad it prints only the VERI_UNIT_BUDGET line (tests/py/test_time_budget.py, faking only the environment, never patching a function of veri.time_budget) ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 89 | 0.96 |
| veri.time_budget.main([]) echoes both values byte for byte: a value holding a non-UTF-8 byte reaches stdout as that byte when accepted and the diagnostic on stderr as that byte when refused, never as `\udcff` (tests/py/test_time_budget.py, faking only the environment and the standard streams, never patching a function of veri.time_budget) ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 70 | 0.85 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 7 | 5 | 0 | 0 | 8 | 8 | 8 | 6 | 8 | 9 | 0 | 0 | 1 | 5 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 14 | 1 | 14 | 4 | 10 |
| target | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 38 | 38 | 36 | 38 | 39 | 38 | 37 | 32 | 33 | 34 | 34 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 239 | 464 | 94324 | 11668366 | 1763074 | 18.33 |
