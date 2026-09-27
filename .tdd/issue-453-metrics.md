### 📊 Metrics — issue 453

Wall time for the issue: 5804 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/518.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 14 | 2 | 4 | 1397 | 57995 | 36403 | 0.33 |
| red | 19 | 7 | 0 | 0 | 761 | 634 | 143 | 276 | 62767 | 6581150 | 859986 | 9.45 |
| green | 18 | 7 | 2 | 0 | 3183 | 701 | 180 | 348 | 70293 | 8634279 | 754501 | 9.17 |
| refactor | 14 | 7 | 0 | 0 | 785 | 369 | 95 | 184 | 34772 | 4166465 | 594187 | 6.28 |
| pin | 5 | 5 | 0 | 0 | 117 | 84 | 19 | 38 | 8069 | 722561 | 194506 | 1.86 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2371 | 4.23 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `run-affordable.sh <n>`, run from a worktree whose event log holds completed full steps, exits 1 and prints spent, steps remaining, the median full-step cost and the projection when `spent + n × median` exceeds `VERI_RUN_BUDGET` ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 300 | 68 | 130 | 29871 | 3208278 | 339310 | 3.95 | 1261 | 1/2 | 1/5 | nothing-structural |
| `run-affordable.sh <n>` exits 0 and prints nothing when `spent + n × median` is within `VERI_RUN_BUDGET` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 12 | 24 | 5130 | 522844 | 82035 | 0.86 | unknown | unknown | unknown | unknown |
| The median is taken over completed full steps only, told apart by leaf count from `step-cost.sh --steps`, so a log whose completed steps are mostly cheap pins still projects the remainder at the full-step median ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 170 | 42 | 80 | 16787 | 1854405 | 261857 | 2.80 | 271 | unknown | 1/5 | structural-owed |
| `run-affordable.sh <n>` exits 3 with nothing on stdout when the event log holds no completed full step, only pins or no usage at all ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 142 | 41 | 80 | 14148 | 1764373 | 249172 | 2.63 | 228 | unknown | 1/5 | structural-owed |
| `run-affordable.sh` exits 2 with nothing on stdout for a missing or non-whole-number `<steps-remaining>` argument ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 163 | 45 | 88 | 16459 | 1997433 | 252520 | 2.75 | 253 | unknown | 2/5 | nothing-left |
| `run-affordable.sh <n>` exits 2 with nothing on stdout when `.tdd/events.jsonl` is missing ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 15 | 28 | 5196 | 661473 | 85655 | 0.92 | unknown | unknown | unknown | unknown |
| `run-affordable.sh <n>` exits 2 with nothing on stdout when `VERI_RUN_BUDGET` is not a non-negative decimal number ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 11 | 22 | 4621 | 489925 | 85351 | 0.87 | unknown | unknown | unknown | unknown |
| A run at 8 of 9 steps done with one median step left and a ceiling above the projection is exit 0, so a converging run near its finish is not parked ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 11 | 22 | 5782 | 490289 | 84345 | 0.89 | unknown | unknown | unknown | unknown |
| A run early in a long plan whose projection exceeds the ceiling is exit 1, so it parks while parking is still cheap ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 11 | 20 | 4757 | 442425 | 83616 | 0.85 | unknown | unknown | unknown | unknown |
| `SKILL.md` calls `run-affordable.sh` at each step boundary, after a step's ledger commit, with the remaining count `next-unchecked.sh` implies, and parks on exit 1 with a comment carrying spent, steps remaining, the median, the projection, the ceiling and the two answers (raise `VERI_RUN_BUDGET` and resume, or split the issue) ⟦criterion 8⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 358 | 76 | 148 | 33857 | 3819091 | 345625 | 4.21 | 1700 | 1/2 | 0/5 | nothing-left |
| `SKILL.md` says what the step boundary does when `run-affordable.sh` exits 3 (no full step done yet — carry on) or exits 2 (no answer could be obtained) ⟦added⟧ ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 215 | 53 | 104 | 21523 | 2486090 | 272145 | 3.11 | 710 | unknown | 2/5 | nothing-structural |
| `SKILL.md` states that an affordability park is not a bail and that `classify-bail.sh` is not called on it ⟦criterion 9⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 185 | 52 | 100 | 17770 | 2367829 | 261549 | 2.92 | 474 | unknown | 1/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 0 | 0 | 90 | 0 | 89 | 76 | 84 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 86 | 97 | 0 | 179 | 0 | 1 | 180 | 0 | 180 | 0 | 0 | 0 | 0 | 85 | 0 | 105 | 0 | 0 | 0 | 106 | 0 | 106 | 0 | 0 | 0 | 86 | 0 | 106 | 0 | 6 | 1 |
| fast | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 4 | 3 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 449 | 457 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 439 | 850 | 177298 | 20162450 | 2439583 | 27.10 |
