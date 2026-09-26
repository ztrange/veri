### 📊 Metrics — issue 451

Wall time for the issue: 11124 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 14 of 16 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 18 | 4 | 8 | 1676 | 152020 | 37685 | 0.37 |
| red | 33 | 14 | 1 | 0 | 1742 | 1162 | 279 | 544 | 114642 | 13742918 | 1495124 | 17.00 |
| green | 30 | 14 | 1 | 0 | 5467 | 1161 | 315 | 616 | 112534 | 14881397 | 1321279 | 15.80 |
| refactor | 29 | 14 | 0 | 0 | 2777 | 735 | 214 | 418 | 72603 | 9584276 | 1257710 | 13.43 |
| pin | 2 | 2 | 0 | 0 | 55 | 39 | 9 | 18 | 3979 | 356115 | 77989 | 0.77 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 506 | 1.69 | 92 | 1.29 |
| green | 1040 | 1.80 | 399 | 1.06 |
| refactor | 0 | 0.00 | 152 | 0.88 |
| pin | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's preflight calls `step-budget.sh` beside `refactor-budget.sh 0`, and its exit 2 is a preflight-class stop before any leaf is launched ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 217 | 55 | 106 | 22137 | 2575823 | 271919 | 3.13 | 610 | unknown | 1/5 | nothing-left |
| SKILL.md places a `step-cost.sh` cost check against the step budget after develop-red, after each verify-red, after each revise attempt, after develop-green and after each verify-green ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 260 | 56 | 112 | 25601 | 3120500 | 314117 | 3.65 | 771 | unknown | 0/5 | nothing-left |
| SKILL.md says in prose, not only in an inline comment, that the shared revise block runs `step-cost.sh` only when the phase being revised is red or green, never for a refactor-phase revise ⟦added⟧ ⟦criterion 2⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 252 | 70 | 136 | 25515 | 3158726 | 388989 | 4.25 | 558 | unknown | 1/5 | nothing-left |
| SKILL.md places no cost check after the step's green commit — not in the refactor loop, not after verify-refactor — and says why ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 13 | 26 | 7146 | 640209 | 96769 | 1.05 | unknown | unknown | unknown | unknown |
| SKILL.md runs each cost check only once the leaf has exited and its `usage` event has been harvested | 6 | 3 | 0 | 0 | 0 | 0 | 182 | 55 | 106 | 17698 | 2548437 | 265710 | 2.99 | 641 | unknown | 1/5 | structural-owed |
| SKILL.md states that the cost check fires at most once per step and is not re-armed once its branch has run ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 169 | 47 | 92 | 16059 | 2051170 | 254293 | 2.77 | 693 | unknown | 0/5 | nothing-left |
| SKILL.md states that `step-cost.sh` exit 3 (no leaf of this step has reported yet) is not a crossing ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 169 | 50 | 96 | 17312 | 2176463 | 250521 | 2.79 | 538 | unknown | 1/5 | structural-owed |
| SKILL.md's crossing branch builds the `over-budget` prompt, launches its leaf through `supervise.sh` the way the exhausted leaf is launched, and reads its answer with `exhausted-outcome.sh`, never by eye ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 283 | 74 | 144 | 28641 | 3524077 | 325877 | 3.89 | 1073 | 1/2 | 1/5 | structural-owed |
| The over-budget exit 0 branch restores the tree (`git reset --hard HEAD`, `git clean -f -- <test-path>`) before growing the plan, grows it in one `add-ledger-step.sh instead-of` call, and commits the plan before the run continues ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 264 | 67 | 130 | 26153 | 3211707 | 327019 | 3.78 | 1242 | 1/2 | 1/5 | structural-owed |
| The over-budget exit 0 branch treats `add-ledger-step.sh` exit 1 as a `step-too-big` bail ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 185 | 53 | 102 | 17740 | 2433163 | 268215 | 2.99 | 575 | unknown | 0/5 | nothing-left |
| The over-budget exit 1 branch parks the step carrying the leaf's answer and the spent and budget figures, and leaves the plan unchanged ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 204 | 54 | 106 | 18181 | 2545385 | 270317 | 3.04 | 1253 | unknown | 0/5 | nothing-left |
| The *Bailing* list's `step-too-big` entry names all three splits that lead to it — a Green leaf's `SPLIT:`, the revise-exhausted split and the over-budget split ⟦added⟧ ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 52 | 104 | 18262 | 2457374 | 259576 | 2.93 | unknown | unknown | 1/5 | structural-owed |
| The over-budget exit 3 branch records the crossing and continues the step, and SKILL.md says in so many words that it is not a bail and why ⟦criterion 9⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 187 | 53 | 106 | 18727 | 2494351 | 258383 | 2.94 | 613 | unknown | 1/5 | nothing-left |
| SKILL.md states once, in the over-budget section, why a crossing is not a failure and why no exit code changes meaning | 6 | 3 | 0 | 0 | 0 | 0 | 233 | 59 | 114 | 22399 | 2777329 | 280727 | 3.25 | 1023 | unknown | 1/5 | nothing-left |
| A supervisor exit 2 on the over-budget leaf is a `killed-stuck` bail, and SKILL.md says the step's budget stays crossed rather than re-arming ⟦criterion 10⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 211 | 58 | 114 | 21474 | 2838201 | 283947 | 3.27 | 969 | unknown | 2/5 | nothing-left |
| `make unit` and every SKILL.md prose suite (`skill-*.test.sh`) pass against the finished SKILL.md ⟦criterion 11⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 7 | 1 | 2 | 713 | 11791 | 35723 | 0.30 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s | run 147 s | run 148 s | run 149 s | run 150 s | run 151 s | run 152 s | run 153 s | run 154 s | run 155 s | run 156 s | run 157 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 91 | 0 | 94 | 96 | 0 | 1 | 1 | 1 | 0 | 99 | 94 | 0 | 98 | 1 | 1 | 0 | 77 | 93 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 93 | 94 | 0 | 9 | 1 | 1 | 0 | 2 | 1 | 36 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 24 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 1 | 1 | 0 | 2 | 0 | 1 | 0 | 0 | 4 | 93 | 1 | 1 | 1 | 94 | 0 | 1 | 257 | 0 | 93 | 1 | 1 | 0 | 93 | 3 | 94 | 94 | 1 | 1 | 1 | 1 | 93 | 94 | 95 | 1 | 1 | 1 | 1 | 1 | 75 | 95 | 0 | 121 | 1 | 1 | 1 | 1 | 0 | 9 | 0 | 96 | 95 | 0 | 96 | 1 | 1 | 94 | 0 | 95 | 95 | 0 | 0 | 0 | 95 | 95 | 95 | 0 | 0 | 1 | 1 | 0 | 94 | 102 | 102 | 28 | 1 | 1 | 1 | 2 | 0 | 84 | 85 | 3 | 101 | 99 | 0 | 0 | 101 | 1 | 1 | 0 | 100 | 98 | 101 | 101 | 101 | 0 | 101 |
| fast | 2 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 345 | 357 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 821 | 1604 | 305434 | 38716726 | 4189787 | 47.38 |
