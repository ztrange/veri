### 📊 Metrics — issue 3007

Wall time for the issue: 626 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 9 planned.
Outcome: the run bailed — report-missing, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $6.89 over 121 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89710 tokens, largest 214908 tokens
Conductor context: first turn 89727 tokens, largest 134189 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89710 |
| 2 | $0.08 | 96690 |
| 3 | $0.06 | 99327 |
| 4 | $0.04 | 100960 |
| 5 | $0.04 | 101625 |
| 6 | $0.03 | 102022 |
| 7 | $0.04 | 102320 |
| 8 | $0.03 | 102614 |
| 9 | $0.03 | 102871 |
| 10 | $0.04 | 103511 |
| 11 | $0.03 | 103805 |
| 12 | $0.07 | 108345 |
| 13 | $0.07 | 113063 |
| 14 | $0.07 | 116530 |
| 15 | $0.04 | 118197 |
| 16 | $0.05 | 119751 |
| 17 | $0.05 | 121012 |
| 18 | $0.05 | 123951 |
| 19 | $0.05 | 125140 |
| 20 | $0.06 | 128640 |
| 21 | $0.06 | 130382 |
| 22 | $0.04 | 130704 |
| 23 | $0.04 | 131613 |
| 24 | $0.04 | 132044 |
| 25 | $0.08 | 137770 |
| 26 | $0.05 | 138308 |
| 27 | $0.04 | 138828 |
| 28 | $0.15 | 153148 |
| 29 | $0.05 | 153527 |
| 30 | $0.05 | 154262 |
| 31 | $0.04 | 154857 |
| 32 | $0.06 | 156106 |
| 33 | $0.05 | 157159 |
| 34 | $0.05 | 158322 |
| 35 | $0.05 | 159323 |
| 36 | $0.05 | 159641 |
| 37 | $0.05 | 160467 |
| 38 | $0.07 | 163680 |
| 39 | $0.04 | 164077 |
| 40 | $0.05 | 164375 |
| 41 | $0.05 | 165595 |
| 42 | $0.07 | 168289 |
| 43 | $0.05 | 168615 |
| 44 | $0.04 | 169010 |
| 45 | $0.05 | 169202 |
| 46 | $0.05 | 169542 |
| 47 | $0.05 | 169697 |
| 48 | $0.05 | 170367 |
| 49 | $0.05 | 171106 |
| 50 | $0.05 | 172541 |
| 51 | $0.06 | 173341 |
| 52 | $0.05 | 174058 |
| 53 | $0.05 | 174354 |
| 54 | $0.04 | 174533 |
| 55 | $0.06 | 175454 |
| 56 | $0.05 | 176579 |
| 57 | $0.06 | 177445 |
| 58 | $0.05 | 178309 |
| 59 | $0.06 | 179871 |
| 60 | $0.06 | 181210 |
| 61 | $0.05 | 182011 |
| 62 | $0.06 | 183120 |
| 63 | $0.05 | 184031 |
| 64 | $0.06 | 184700 |
| 65 | $0.06 | 186150 |
| 66 | $0.06 | 188069 |
| 67 | $0.06 | 188963 |
| 68 | $0.05 | 189872 |
| 69 | $0.06 | 191079 |
| 70 | $0.09 | 196025 |
| 71 | $0.06 | 197201 |
| 72 | $0.06 | 198390 |
| 73 | $0.06 | 199468 |
| 74 | $0.06 | 199970 |
| 75 | $0.06 | 201851 |
| 76 | $0.07 | 203411 |
| 77 | $0.06 | 204591 |
| 78 | $0.05 | 205115 |
| 79 | $0.06 | 205860 |
| 80 | $0.06 | 206556 |
| 81 | $0.07 | 208282 |
| 82 | $0.09 | 212884 |
| 83 | $0.06 | 213651 |
| 84 | $0.06 | 214908 |
| 85 | $0.58 | 89727 |
| 86 | $0.07 | 96712 |
| 87 | $0.04 | 99383 |
| 88 | $0.04 | 101290 |
| 89 | $0.04 | 103219 |
| 90 | $0.03 | 104279 |
| 91 | $0.03 | 104816 |
| 92 | $0.02 | 105198 |
| 93 | $0.03 | 105981 |
| 94 | $0.02 | 106433 |
| 95 | $0.02 | 106717 |
| 96 | $0.02 | 107055 |
| 97 | $0.02 | 107338 |
| 98 | $0.02 | 107579 |
| 99 | $0.03 | 108035 |
| 100 | $0.02 | 108341 |
| 101 | $0.02 | 108687 |
| 102 | $0.03 | 109372 |
| 103 | $0.05 | 113447 |
| 104 | $0.05 | 116623 |
| 105 | $0.03 | 117521 |
| 106 | $0.03 | 118093 |
| 107 | $0.03 | 118760 |
| 108 | $0.03 | 120070 |
| 109 | $0.03 | 120520 |
| 110 | $0.03 | 121872 |
| 111 | $0.03 | 122234 |
| 112 | $0.03 | 122882 |
| 113 | $0.03 | 123595 |
| 114 | $0.03 | 123912 |
| 115 | $0.03 | 124596 |
| 116 | $0.03 | 125225 |
| 117 | $0.04 | 127322 |
| 118 | $0.04 | 128543 |
| 119 | $0.03 | 129305 |
| 120 | $0.06 | 134189 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 15 | 1 | 2 | 1804 | 0 | 33943 | 0.10 |
| red | 10 | 3 | 1 | 0 | 699 | 219 | 50 | 98 | 17883 | 1502790 | 312478 | 1.37 |
| green | 4 | 1 | 0 | 0 | 998 | 132 | 22 | 42 | 12212 | 709059 | 94087 | 0.43 |
| refactor | 1 | 0 | 0 | 0 | 9 | 5 | 2 | 4 | 204 | 49907 | 15764 | 0.05 |
| diff | 5 | 2 | 1 | 0 | 920 | 224 | 40 | 80 | 19867 | 1476485 | 222980 | 1.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 7 | 2 | 0 | 870 | 155 | 29 | 58 | 9008 | 700570 | 256735 | 0.80 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 1374 | 342 | 67 | 130 | 33780 | 2278885 | 347567 | 1.63 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 401 | 98 | 19 | 38 | 9182 | 758786 | 74950 | 0.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 557 | 1.16 |
| green | 0 | 0.00 | 702 | 0.30 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 582 | 0.78 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `wrong-test-route.sh` prints `red <case>` for a green report carrying a `CONTRADICTS: <case>` line that names an existing test case other than the step's own, beside a `WRONG_TEST:` line whose prose names no case ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 87 | 19 | 36 | 5553 | 519312 | 109864 | 0.38 | 2016 | unknown | 0/5 | nothing-left |  |  | full |
| every existing case in `skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py`, `unit/test_wrong_test_route_prose.py` and `test_wrong_test_route_process.py` whose expected output relies on a case named on a `WRONG_TEST:` line being taken as the contradicted case also carries a `CONTRADICTS:` line naming that case in the same spelling and quoting; test files only, no production change, every suite stays green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 109 | 17 | 34 | 10210 | 649362 | 100447 | 0.42 | 947 | n/a | n/a | n/a |  |  | full |
| `wrong-test-route.sh` prints `repair <the step's own case>`, and never `red`, for a green report whose `WRONG_TEST:` line names an existing test case other than the step's own and which carries no `CONTRADICTS:` line ⟦criterion 1⟧ | 13 | 3 | 2 | 0 | 0 | 0 | 384 | 78 | 154 | 34403 | 2569567 | 434998 | 2.24 | unknown | diff 1/2, red 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `wrong-test-route.sh` prints `red <case>` for a green report carrying a `CONTRADICTS: <case>` line that names an existing test case other than the step's own, beside a `WRONG_TEST:` line whose prose names no case ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 11 | 12 | 19 | 15 | 11 | 11 | 11 | 44 | 18 | 23 | 16 | 10 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 89 | 96 | 70 | 64 | 86 | 86 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 7 | 7 | 6 | 6 | 7 | 5 | 6 | 7 | 7 | 7 | 7 | 7 | 6 | 6 | 6 | 6 | 6 | 8 | 9 | 9 | 10 | 10 | 9 | 8 | 9 | 9 | 10 | 11 | 8 | 8 | 8 | 12 | 9 | 8 | 10 | 7 | 8 | 12 | 11 | 11 | 10 | 8 | 11 | 10 | 8 | 9 | 9 | 12 | 18 | 14 | 14 | 11 | 9 | 9 | 9 | 8 | 7 | 10 | 7 | 9 | 9 | 7 | 7 | 10 | 7 | 9 | 8 | 8 | 11 | 9 | 10 | 7 | 6 | 7 | 8 | 8 | 7 | 7 | 6 | 6 | 7 | 7 | 6 | 8 | 8 | 7 | 8 | 8 | 7 | 7 | 8 | 7 | 6 | 7 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 6 | 7 | 13 | 8 | 9 | 7 | 8 | 7 | 8 | 8 | 9 | 6 | 7 | 7 | 7 | 8 | 8 | 10 | 7 | 8 | 7 | 10 | 9 | 8 | 9 | 8 | 10 | 11 | 8 | 7 | 9 | 18 | 13 | 12 | 7 | 7 | 8 | 8 | 7 | 10 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 115 | 226 | 51970 | 3738241 | 679252 | 10.04 (estimate) |
