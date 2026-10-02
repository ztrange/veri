### 📊 Metrics — issue 635

Wall time for the issue: 4932 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/654.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 44 | 36 | 4 | 8 | 3576 | 113627 | 79241 | 0.73 |
| red | 8 | 3 | 0 | 0 | 558 | 362 | 71 | 138 | 35021 | 3685710 | 395503 | 4.60 |
| green | 10 | 3 | 2 | 0 | 2582 | 558 | 118 | 236 | 54308 | 6158968 | 459374 | 5.99 |
| refactor | 6 | 3 | 0 | 0 | 525 | 183 | 38 | 76 | 13918 | 1759395 | 264983 | 2.75 |
| pin | 2 | 2 | 0 | 0 | 134 | 47 | 11 | 22 | 4785 | 474934 | 83124 | 0.86 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 15 | 12 | 3 | 0 | 1967 | 547 | 113 | 226 | 49416 | 5402720 | 624515 | 7.07 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 1876 | 639 | 129 | 254 | 62192 | 6789914 | 657710 | 7.86 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3388 | 6.49 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| under `make test`, a suite under tests/unit/ that calls real git, python3, gh or curl fails, and the output names the command it called ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 490 | 107 | 214 | 49202 | 5633107 | 459038 | 5.78 | 2310 | 2/2 | 1/5 | structural-owed |  |  | full |
| under `make test`, a suite outside tests/unit/ that calls real git still passes — case 5's `run_make test TESTS=… UNIT_TESTS=` arm unchanged ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 82 | 19 | 36 | 7789 | 955964 | 99157 | 1.14 | unknown | unknown | unknown | unknown |  |  | pin |
| unit-tier.test.sh still checks, over the real tests/unit/ roster without running any suite, that every unit suite's header carries its `git <n>, python3 <n>, server <n>, sleep <n>` line, that no unit suite is still duplicated in tests/, and that at least 5 suites are under tests/unit/ — and a fixture tree with one header lacking that line proves the header check fails, naming the suite ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 222 | 44 | 88 | 17891 | 2169831 | 270862 | 2.96 | 432 | unknown | 1/5 | structural-owed |  |  | full |
| unit-tier.test.sh runs no nested `make unit` or `make test` over the real roster; every nested run names a fixture suite ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 86 | 15 | 30 | 8344 | 734754 | 89792 | 1.03 | unknown | unknown | unknown | unknown |  |  | pin |
| the Makefile's comment on the unit guard and CLAUDE.md's fast-tier paragraph say that `make test` applies the guard to the suites under tests/unit/ and to no other suite ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 270 | 53 | 104 | 24806 | 2585351 | 284135 | 3.29 | 922 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| under `make test`, a suite under tests/unit/ that calls real git, python3, gh or curl fails, and the output names the command it called ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 124 | 0.89 |
| unit-tier.test.sh still checks, over the real tests/unit/ roster without running any suite, that every unit suite's header carries its `git <n>, python3 <n>, server <n>, sleep <n>` line, that no unit suite is still duplicated in tests/, and that at least 5 suites are under tests/unit/ — and a fixture tree with one header lacking that line proves the header check fails, naming the suite ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 99 | 0.88 |
| the Makefile's comment on the unit guard and CLAUDE.md's fast-tier paragraph say that `make test` applies the guard to the suites under tests/unit/ and to no other suite ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 302 | 0.98 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 24 | 24 | 75 | 0 | 0 | 110 | 79 | 0 | 112 | 74 | 0 | 104 | 102 | 0 | 137 | 70 | 0 | 102 | 0 | 73 | 0 | 6 | 1 | 6 | 1 | 1 | 1 | 8 | 1 | 30 | 21 | 22 | 22 | 0 | 23 | 23 | 3 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 76 | 74 | 0 | 86 | 0 | 23 | 85 | 0 | 104 |
| fast | 23 | 23 | 23 | 22 | 21 | 20 | 20 | 21 | 21 | 21 | 21 | 23 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 25 | 0 | 24 | 23 | 23 | 25 | 2 | 2 | 24 | 2 | 0 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 242 | 480 | 111608 | 12192634 | 1282225 | 14.93 |
