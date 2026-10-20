### 📊 Metrics — issue 1861

Wall time for the issue: 1511 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1873.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.77 over 44 turns, in 1 sessions.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84041 |
| 2 | $0.03 | 85334 |
| 3 | $0.03 | 87282 |
| 4 | $0.02 | 87652 |
| 5 | $0.02 | 88029 |
| 6 | $0.02 | 88356 |
| 7 | $0.02 | 88677 |
| 8 | $0.02 | 89257 |
| 9 | $0.02 | 89626 |
| 10 | $0.03 | 91674 |
| 11 | $0.04 | 94992 |
| 12 | $0.03 | 95921 |
| 13 | $0.02 | 96225 |
| 14 | $0.03 | 97139 |
| 15 | $0.03 | 97740 |
| 16 | $0.03 | 98485 |
| 17 | $0.03 | 99781 |
| 18 | $0.02 | 100353 |
| 19 | $0.03 | 101681 |
| 20 | $0.03 | 102421 |
| 21 | $0.03 | 103199 |
| 22 | $0.03 | 103950 |
| 23 | $0.03 | 105257 |
| 24 | $0.03 | 106066 |
| 25 | $0.03 | 106804 |
| 26 | $0.03 | 107536 |
| 27 | $0.02 | 107915 |
| 28 | $0.03 | 108695 |
| 29 | $0.03 | 110026 |
| 30 | $0.03 | 111468 |
| 31 | $0.04 | 113908 |
| 32 | $0.03 | 114639 |
| 33 | $0.03 | 114928 |
| 34 | $0.03 | 115622 |
| 35 | $0.03 | 116743 |
| 36 | $0.03 | 117523 |
| 37 | $0.04 | 119087 |
| 38 | $0.03 | 119878 |
| 39 | $0.04 | 121413 |
| 40 | $0.03 | 122227 |
| 41 | $0.03 | 123120 |
| 42 | $0.03 | 123397 |
| 43 | $0.03 | 123684 |
| 44 | $0.03 | 124255 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 1 | 2 | 933 | 0 | 30282 | 0.09 |
| red | 6 | 1 | 0 | 0 | 233 | 169 | 42 | 84 | 18319 | 1367097 | 145407 | 0.68 |
| green | 2 | 1 | 0 | 0 | 133 | 46 | 16 | 32 | 4790 | 482989 | 32721 | 0.18 |
| refactor | 2 | 1 | 0 | 0 | 35 | 14 | 6 | 12 | 1103 | 153893 | 27338 | 0.09 |
| pin | 4 | 4 | 0 | 0 | 82 | 56 | 16 | 32 | 5354 | 425408 | 55781 | 0.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 179 | 97 | 27 | 54 | 9708 | 685376 | 129317 | 0.49 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 315 | 195 | 54 | 108 | 20791 | 1744011 | 162212 | 0.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In a bash suite shaped like the real ones (cases followed by the `finish` trailer, fixture copied from a real suite's shape, trailer included), a Red that adds one case just before `finish` is recorded by `tests-frozen.sh record --step` as adding that case only: the previous last case is not recorded as edited, and a WRONG_TEST naming it still routes to `red <case>` through wrong_test_route ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 94 | 33 | 66 | 9568 | 971462 | 118149 | 0.49 | 342 | unknown | 0/5 | nothing-left |  |  | full |
| In a pytest file with no imports, a Red that inserts a new case at file start directly above an older one records only the new case (the older case's recorded body starts at its own `def`, not at blank lines above it), and a WRONG_TEST naming the older case still routes to `red <case>` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 14 | 28 | 5487 | 422601 | 35026 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| In a pytest file where an older case sits below a single blank line, a Red that inserts a new case directly above it (one blank line above becoming two) records only the new case, and a WRONG_TEST naming the older case still routes to `red <case>` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 8 | 16 | 3758 | 228242 | 33972 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| In a pytest file with a test class, a Red that inserts a new method directly above an older method of that class records only the new method, and a WRONG_TEST naming the older method still routes to `red <case>` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 12 | 24 | 5612 | 376959 | 35458 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| In a bash suite, a Red that inserts a new case directly above an older one records only the new case (the older case's recorded body starts at its own `name="…"` line, not at blank lines above it), and a WRONG_TEST naming the older case still routes to `red <case>` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 13 | 26 | 5141 | 430123 | 38642 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| In a bash suite shaped like the real ones (cases followed by the `finish` trailer, fixture copied from a real suite's shape, trailer included), a Red that adds one case just before `finish` is recorded by `tests-frozen.sh record --step` as adding that case only: the previous last case is not recorded as edited, and a WRONG_TEST naming it still routes to `red <case>` through wrong_test_route ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 0 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 4 |  |
| fast | 13 | 12 | 13 | 12 | 12 |  |  |  |  |  |  |  |  |
| target | 3 | 0 | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 1 | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 162 | 30499 | 2429387 | 291529 | 1.28 |
