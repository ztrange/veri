### 📊 Metrics — issue 2917

Wall time for the issue: 9298 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3024.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.80 over 67 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90190 tokens, largest 154053 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90190 |
| 2 | $0.07 | 97169 |
| 3 | $0.03 | 98390 |
| 4 | $0.03 | 99990 |
| 5 | $0.03 | 101617 |
| 6 | $0.03 | 102241 |
| 7 | $0.02 | 102666 |
| 8 | $0.02 | 102921 |
| 9 | $0.02 | 103248 |
| 10 | $0.02 | 103504 |
| 11 | $0.02 | 103835 |
| 12 | $0.02 | 104281 |
| 13 | $0.02 | 104600 |
| 14 | $0.02 | 104869 |
| 15 | $0.03 | 105516 |
| 16 | $0.03 | 107062 |
| 17 | $0.03 | 108388 |
| 18 | $0.03 | 109626 |
| 19 | $0.03 | 110310 |
| 20 | $0.03 | 110830 |
| 21 | $0.03 | 111719 |
| 22 | $0.03 | 112714 |
| 23 | $0.03 | 113516 |
| 24 | $0.03 | 114921 |
| 25 | $0.03 | 115574 |
| 26 | $0.03 | 116178 |
| 27 | $0.04 | 117780 |
| 28 | $0.03 | 118373 |
| 29 | $0.04 | 119842 |
| 30 | $0.03 | 120682 |
| 31 | $0.09 | 128867 |
| 32 | $0.03 | 129905 |
| 33 | $0.03 | 131026 |
| 34 | $0.03 | 131812 |
| 35 | $0.03 | 132138 |
| 36 | $0.03 | 132634 |
| 37 | $0.03 | 133374 |
| 38 | $0.03 | 133741 |
| 39 | $0.03 | 134701 |
| 40 | $0.05 | 137920 |
| 41 | $0.03 | 138244 |
| 42 | $0.03 | 138614 |
| 43 | $0.03 | 139313 |
| 44 | $0.04 | 140278 |
| 45 | $0.03 | 140604 |
| 46 | $0.03 | 141049 |
| 47 | $0.03 | 141371 |
| 48 | $0.03 | 141599 |
| 49 | $0.03 | 141992 |
| 50 | $0.03 | 142560 |
| 51 | $0.03 | 143095 |
| 52 | $0.03 | 143847 |
| 53 | $0.05 | 145885 |
| 54 | $0.05 | 148791 |
| 55 | $0.03 | 149395 |
| 56 | $0.03 | 149702 |
| 57 | $0.04 | 150455 |
| 58 | $0.03 | 150771 |
| 59 | $0.03 | 151037 |
| 60 | $0.03 | 151278 |
| 61 | $0.03 | 151771 |
| 62 | $0.03 | 152261 |
| 63 | $0.03 | 152499 |
| 64 | $0.03 | 152769 |
| 65 | $0.03 | 153040 |
| 66 | $0.03 | 153285 |
| 67 | $0.04 | 154053 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 5 | 1 | 2 | 634 | 0 | 31231 | 0.08 |
| red | 3 | 1 | 0 | 0 | 204 | 60 | 16 | 32 | 8570 | 466906 | 95284 | 0.37 |
| green | 4 | 1 | 1 | 0 | 748 | 75 | 23 | 46 | 6651 | 655318 | 88128 | 0.47 |
| refactor | 1 | 0 | 0 | 0 | 8 | 3 | 2 | 4 | 172 | 30517 | 31501 | 0.08 |
| pin | 1 | 1 | 0 | 0 | 37 | 10 | 3 | 6 | 1068 | 60666 | 32834 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 4 | 1 | 0 | 505 | 49 | 16 | 32 | 5163 | 387085 | 115129 | 0.38 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 126 | 55 | 15 | 30 | 7985 | 420414 | 111992 | 0.40 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 376 | 49 | 14 | 28 | 3947 | 405908 | 51857 | 0.32 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 748 | 0.47 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Ticking a step with `tick-ledger.sh --refactor-pending` from a subdirectory of the repo, after a case recorded by `tests-frozen.sh record --step` was renamed in the uncommitted work tree, leaves the step's frozen-cases record holding the renamed title and exits 0 (the record and the test file it names are found from the repo's top level, not the cwd) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 117 | 35 | 70 | 12538 | 977514 | 176074 | 0.78 | 3055 | 1/2 | 0/5 | nothing-left |  |  | full |
| Ticking the same step with `tick-ledger.sh --refactor-pending` from a subdirectory of the repo and from the repo root, after the same rename, leaves byte-identical frozen-cases records ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 18 | 3923 | 235893 | 71673 | 0.24 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Ticking a step with `tick-ledger.sh --refactor-pending` from a subdirectory of the repo, after a case recorded by `tests-frozen.sh record --step` was renamed in the uncommitted work tree, leaves the step's frozen-cases record holding the renamed title and exits 0 (the record and the test file it names are found from the repo's top level, not the cwd) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 14 | 13 | 10 | 16 | 68 | 18 | 71 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 67 | 64 | 65 | 71 | 80 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 7 | 6 | 10 | 13 | 10 | 9 | 10 | 10 | 10 | 10 | 10 | 10 | 11 | 11 | 10 | 11 | 10 | 10 | 10 | 10 | 13 | 13 | 12 | 13 | 12 | 13 | 12 | 12 | 11 | 11 | 11 | 12 | 13 | 11 | 10 | 11 | 11 | 13 | 12 | 12 | 8 | 8 | 9 | 8 | 10 | 10 | 8 | 10 | 9 | 8 | 10 | 15 | 11 | 10 | 11 | 9 | 9 | 9 | 7 | 7 | 8 | 8 | 7 | 8 | 9 | 8 | 8 | 8 | 9 | 9 | 8 | 9 | 9 | 9 | 9 | 10 | 11 | 12 | 11 | 11 | 12 | 11 | 12 | 10 | 12 | 12 | 12 | 11 | 12 | 12 | 13 | 9 | 8 | 9 | 10 | 9 | 10 | 9 | 11 | 10 | 10 | 8 | 13 | 11 | 12 | 11 | 12 | 11 | 11 | 9 | 10 | 9 | 10 | 10 | 10 | 7 | 8 | 7 | 9 | 10 | 9 | 10 | 12 | 9 | 11 | 9 | 8 | 8 | 13 | 9 | 10 | 9 | 9 | 8 | 6 | 7 | 9 | 7 | 11 | 11 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 45 | 90 | 17095 | 1213407 | 278978 | 3.90 (estimate) |
