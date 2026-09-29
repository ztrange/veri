### 📊 Metrics — issue 494

Wall time for the issue: 10484 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 14 of 18 planned.
Outcome: the run bailed — step-too-big, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 29 | 24 | 5 | 10 | 2206 | 196098 | 38378 | 0.39 |
| red | 38 | 16 | 0 | 0 | 2857 | 1272 | 321 | 622 | 113866 | 14778381 | 1648179 | 18.42 |
| pin | 1 | 1 | 0 | 0 | 33 | 24 | 7 | 12 | 2099 | 252429 | 39608 | 0.41 |
| green | 43 | 15 | 6 | 0 | 10489 | 2284 | 504 | 1000 | 209381 | 25332605 | 1835792 | 24.56 |
| refactor | 29 | 14 | 0 | 0 | 1616 | 719 | 186 | 362 | 67653 | 7881699 | 1187782 | 12.43 |
| exhausted | 1 | 0 | 0 | 0 | 54 | 47 | 9 | 18 | 3970 | 425606 | 47491 | 0.54 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 1467 | 2.29 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 8348 | 15.94 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 54 | 0.54 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The text of every class 3 `#` line in the suites (24 lines, in capture-spec, orchestrate, parallel-conductors, run-verdict, skill-refactor-pending and solvable-issues) is pinned, so a sweep that edits, moves or deletes one turns a suite red ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 89 | 19 | 36 | 8829 | 931488 | 95292 | 1.13 | unknown | unknown | unknown | unknown |  |  | pin |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with a or b ⟦criterion 1⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 390 | 94 | 186 | 34047 | 4689368 | 426081 | 5.03 | 527 | unknown | 0/5 | nothing-left |  |  | full |
| comment-class.sh does not report a `#`-led line inside a multi-line single- or double-quoted string as a comment ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 301 | 63 | 124 | 27201 | 2831736 | 300331 | 3.51 | 1108 | 1/2 | 1/5 | nothing-structural |  |  | full |
| comment-class.sh --sweepable omits the `#!` line that opens a heredoc's body ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 208 | 56 | 106 | 20087 | 2303185 | 298208 | 3.25 | 973 | 1/2 | 0/5 | nothing-left |  |  | full |
| comment-class.sh classes a `#` line inside a heredoc written to a `.md` file as class 3 ⟦added⟧ ⟦criterion 1⟧ | 16 | 6 | 2 | 0 | 0 | 0 | 503 | 122 | 232 | 46492 | 5325796 | 656245 | 7.25 | 2629 | 2/2 | 1/5 | structural-owed |  |  | full |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with c or d ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 182 | 49 | 98 | 17813 | 2246834 | 252609 | 2.83 | 804 | unknown | 0/5 | nothing-structural |  |  | full |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with e through j ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 217 | 53 | 104 | 20606 | 2422934 | 258126 | 2.96 | 684 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with k through m ⟦criterion 1⟧ | 13 | 5 | 1 | 0 | 0 | 0 | 569 | 129 | 254 | 53024 | 6137667 | 536490 | 6.58 | 1726 | 1/2 | 1/5 | structural-owed |  |  | full |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with n through r ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 394 | 82 | 166 | 31529 | 4187226 | 333388 | 4.75 | 2501 | 1/2 | 1/5 | structural-owed |  |  | full |
| The sweepable report is empty for `tests/supervise.test.sh` and `tests/supervise-retry.test.sh` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 208 | 56 | 112 | 19941 | 2585472 | 250058 | 2.92 | 496 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with s, other than the `skill-*` and `supervise*` files ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 281 | 66 | 130 | 25320 | 3546302 | 293379 | 3.56 | 820 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with t through z ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 245 | 64 | 126 | 23181 | 3083796 | 269864 | 3.24 | 827 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for every `tests/skill-*.test.sh` whose name after `skill-` starts with a through l ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 245 | 62 | 120 | 22210 | 2928982 | 267796 | 3.17 | 487 | unknown | 1/5 | structural-owed |  |  | full |
| The sweepable report is empty for every `tests/skill-*.test.sh` whose name after `skill-` starts with m through z ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 280 | 64 | 124 | 25443 | 3082987 | 279477 | 3.36 | 511 | unknown | 0/5 | structural-owed |  |  | full |
| The sweepable report is empty for every shell file under `tests/unit/` and `tests/fixtures/`, and for `tests/unit-guard/git` and `tests/offline/gh` ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 234 | 48 | 96 | 21246 | 2366947 | 241508 | 2.83 | unknown | 2/2 | unknown | unknown |  | exhausted | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| comment-class.sh does not report a `#`-led line inside a multi-line single- or double-quoted string as a comment ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 76 | 0.89 |
| comment-class.sh --sweepable omits the `#!` line that opens a heredoc's body ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 49 | 0.71 |
| comment-class.sh classes a `#` line inside a heredoc written to a `.md` file as class 3 ⟦added⟧ ⟦criterion 1⟧ | 2 | 1/5 | structural-owed | PASS | 0 | 145 | 1.75 |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with a or b ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 102 | 0.82 |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with c or d ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 207 | 0.74 |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with e through j ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 141 | 0.80 |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with k through m ⟦criterion 1⟧ | 2 | 1/5 | structural-owed | PASS | 0 | 106 | 1.27 |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with n through r ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 155 | 1.01 |
| The sweepable report is empty for `tests/supervise.test.sh` and `tests/supervise-retry.test.sh` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 100 | 0.81 |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with s, other than the `skill-*` and `supervise*` files ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 116 | 0.82 |
| The sweepable report is empty for every top-level `tests/*.sh` whose name starts with t through z ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 206 | 0.83 |
| The sweepable report is empty for every `tests/skill-*.test.sh` whose name after `skill-` starts with a through l ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 86 | 0.88 |
| The sweepable report is empty for every `tests/skill-*.test.sh` whose name after `skill-` starts with m through z ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 127 | 1.11 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 0 | 2 | 1 | 2 | 4 | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 5 | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 0 | 34 | 0 | 39 | 0 | 40 | 2 | 2 | 3 | 156 | 0 | 157 | 0 | 156 | 2 | 2 | 0 | 89 | 82 | 0 | 82 | 2 | 2 | 0 | 46 | 46 | 47 | 0 | 47 | 2 | 2 | 5 | 6 | 2 | 2 | 0 | 3 | 2 | 2 | 106 | 0 | 193 | 615 | 33 | 0 | 34 | 2 | 2 | 38 | 37 | 0 | 37 | 3 | 3 | 0 | 1 | 56 | 33 | 1 | 2 | 3 | 4 | 8 | 2 | 7 | 0 | 2 | 1 | 1 | 71 | 0 | 12 | 0 | 71 | 0 | 1 | 1 | 1 | 0 | 0 | 1 | 3 | 0 | 0 | 55 | 3 | 3 | 2 | 3 | 0 | 136 | 137 | 0 | 138 | 2 | 0 | 3 | 0 | 39 | 0 | 37 | 2 | 3 | 3 | 2 | 0 | 45 | 0 | 19 | 0 | 22 | 3 |
| target | 1 | 1 | 0 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 0 | 2 | 0 | 3 | 3 | 2 | 0 | 2 | 2 | 2 | 0 | 2 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 8 | 8 | 8 | 7 | 8 | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 8 | 8 | 9 | 9 | 8 | 9 | 9 | 9 | 8 | 9 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 8 | 8 | 9 | 8 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 597 | 596 | 610 | 601 | 600 | 610 | 614 | 626 | 622 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 1032 | 2024 | 399175 | 48866818 | 4797230 | 56.76 |
