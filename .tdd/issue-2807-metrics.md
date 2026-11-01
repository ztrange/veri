### 📊 Metrics — issue 2807

Wall time for the issue: 7851 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2811.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.98 over 65 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87288 tokens, largest 145119 tokens
Conductor context: first turn 87287 tokens, largest 162706 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87288 |
| 2 | $0.09 | 94290 |
| 3 | $0.04 | 95464 |
| 4 | $0.06 | 97467 |
| 5 | $0.04 | 98184 |
| 6 | $0.03 | 98600 |
| 7 | $0.04 | 98898 |
| 8 | $0.04 | 99168 |
| 9 | $0.09 | 106802 |
| 10 | $0.13 | 118414 |
| 11 | $0.07 | 121598 |
| 12 | $0.07 | 125723 |
| 13 | $0.05 | 126445 |
| 14 | $0.12 | 136320 |
| 15 | $0.06 | 138395 |
| 16 | $0.08 | 143251 |
| 17 | $0.06 | 145119 |
| 18 | $0.56 | 87287 |
| 19 | $0.07 | 94288 |
| 20 | $0.03 | 95389 |
| 21 | $0.04 | 97418 |
| 22 | $0.05 | 101528 |
| 23 | $0.08 | 109158 |
| 24 | $0.03 | 110062 |
| 25 | $0.03 | 111587 |
| 26 | $0.02 | 111911 |
| 27 | $0.03 | 112257 |
| 28 | $0.04 | 114503 |
| 29 | $0.04 | 116775 |
| 30 | $0.04 | 119275 |
| 31 | $0.03 | 119821 |
| 32 | $0.09 | 128224 |
| 33 | $0.04 | 130486 |
| 34 | $0.03 | 131184 |
| 35 | $0.04 | 132662 |
| 36 | $0.07 | 137579 |
| 37 | $0.04 | 138918 |
| 38 | $0.04 | 139950 |
| 39 | $0.04 | 141439 |
| 40 | $0.04 | 142973 |
| 41 | $0.05 | 145535 |
| 42 | $0.04 | 146683 |
| 43 | $0.04 | 148177 |
| 44 | $0.04 | 150025 |
| 45 | $0.04 | 151563 |
| 46 | $0.06 | 154756 |
| 47 | $0.04 | 156261 |
| 48 | $0.04 | 157238 |
| 49 | $0.04 | 158163 |
| 50 | $0.04 | 158832 |
| 51 | $0.03 | 159106 |
| 52 | $0.03 | 159400 |
| 53 | $0.04 | 159823 |
| 54 | $0.04 | 160444 |
| 55 | $0.03 | 160710 |
| 56 | $0.03 | 160977 |
| 57 | $0.03 | 161243 |
| 58 | $0.03 | 161531 |
| 59 | $0.03 | 161817 |
| 60 | $0.03 | 162080 |
| 61 | $0.04 | 162706 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 12 | 2 | 4 | 1526 | 32657 | 34582 | 0.10 |
| red | 13 | 3 | 0 | 0 | 553 | 245 | 74 | 134 | 29212 | 2260128 | 407599 | 1.97 |
| pin | 5 | 4 | 1 | 0 | 167 | 63 | 19 | 38 | 6504 | 534648 | 84617 | 0.33 |
| green | 11 | 4 | 2 | 0 | 995 | 126 | 54 | 90 | 15559 | 1320402 | 181113 | 0.94 |
| refactor | 3 | 0 | 0 | 0 | 24 | 11 | 6 | 12 | 964 | 111858 | 85451 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 12 | 3 | 0 | 981 | 162 | 54 | 108 | 18021 | 1495601 | 236947 | 0.92 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 438 | 205 | 69 | 120 | 25106 | 2058457 | 387861 | 1.71 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 335 | 90 | 32 | 50 | 10638 | 705635 | 168554 | 0.96 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 44 | 0.12 | 0 | 0.00 |
| green | 614 | 0.74 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A SUPERSEDED report naming `TestOther` defined as `func TestOther(t *testing.T)` only in a Go file not named `*_test.go` answers `revise`, exit 3 (a small in-process case in tests/py/unit/test_wrong_test_route.py, no production change expected) ⟦criterion 1⟧ | 5 | 1 | 1 | 0 | 0 | 0 | 117 | 28 | 50 | 12976 | 941657 | 177910 | 0.95 | unknown | 1/2 | unknown | unknown |  |  | pin |
| A SUPERSEDED report naming a case defined by `func TestOther(t *testing.T)` in a `*_test.go` file answers `red TestOther`, exit 0, instead of `revise` (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 63 | 29 | 50 | 7775 | 679931 | 162351 | 0.66 | 501 | 1/2 | 0/5 | nothing-left |  |  | full |
| A WRONG_TEST report naming, as a bare unquoted word, a case defined by `func TestOther(t *testing.T)` in a `*_test.go` file answers `red TestOther`, exit 0, instead of `revise` (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 69 | 27 | 48 | 8124 | 657852 | 142813 | 0.60 | 553 | 1/2 | 0/5 | nothing-left |  |  | full |
| A report with two SUPERSEDED lines naming two cases defined by `func Test<Name>(t *testing.T)` in `*_test.go` files answers `supersede` naming both, exit 0, as the same report does on Python (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 12 | 24 | 3797 | 394530 | 38712 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| A WRONG_TEST report naming only the step's own red case, defined by `func TestOwn(t *testing.T)` in a `*_test.go` file, answers `revise`, exit 3, never `fixture` (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 11 | 22 | 4337 | 367098 | 47451 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| A WRONG_TEST report naming in backticks a helper defined by `func newServer(t *testing.T)` in a `*_test.go` file answers `fixture <path> newServer`, exit 0, instead of `revise` (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 103 | 36 | 60 | 12100 | 884340 | 154089 | 0.75 | 790 | 1/2 | 0/5 | nothing-left |  |  | full |
| A WRONG_TEST report naming in backticks a helper defined by `func newServer(t *testing.T)` only in a Go file not named `*_test.go` answers `revise`, exit 3 (a small in-process case in tests/py/unit/test_wrong_test_route.py, no production change expected) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 10 | 20 | 3130 | 301628 | 35454 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A SUPERSEDED report naming a case defined by `func TestOther(t *testing.T)` in a `*_test.go` file answers `red TestOther`, exit 0, instead of `revise` (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.05 |
| A WRONG_TEST report naming, as a bare unquoted word, a case defined by `func TestOther(t *testing.T)` in a `*_test.go` file answers `red TestOther`, exit 0, instead of `revise` (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.10 |
| A WRONG_TEST report naming in backticks a helper defined by `func newServer(t *testing.T)` in a `*_test.go` file answers `fixture <path> newServer`, exit 0, instead of `revise` (a small in-process case in tests/py/unit/test_wrong_test_route.py) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 6 | 5 | 6 | 5 | 5 | 5 | 6 | 4 | 5 | 6 | 6 | 11 | 9 | 10 | 7 | 5 | 5 | 8 | 8 | 8 | 13 | 13 | 13 |  |  |  |  |  |  |  |
| target | 5 | 4 | 5 | 5 | 5 | 4 | 3 | 3 | 4 | 6 | 6 | 7 | 5 | 6 | 5 | 5 | 5 | 5 | 9 | 9 | 9 | 9 | 8 | 9 | 9 | 9 | 9 | 9 | 13 | 13 |
| fast | 34 | 36 | 36 | 35 | 35 | 41 | 54 | 52 | 46 | 65 | 60 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 155 | 278 | 53765 | 4259693 | 793362 | 7.57 (estimate) |
