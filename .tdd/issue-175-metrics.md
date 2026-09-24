### 📊 Metrics — issue 175

Wall time for the issue: 12161 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/443.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 46 | 42 | 6 | 8 | 3501 | 161338 | 41960 | 0.59 |
| red | 18 | 7 | 1 | 0 | 4103 | 2272 | 315 | 572 | 171410 | 18321686 | 1121846 | 24.67 |
| green | 15 | 7 | 0 | 0 | 3009 | 1682 | 301 | 550 | 122456 | 16708323 | 895696 | 20.38 |
| refactor | 14 | 7 | 0 | 0 | 2982 | 1684 | 238 | 464 | 125563 | 14094894 | 786080 | 18.05 |
| pin | 1 | 1 | 0 | 0 | 75 | 52 | 12 | 20 | 4483 | 522687 | 49123 | 0.86 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 1018 | 4.44 | 242 | 2.61 |
| green | 0 | 0.00 | 70 | 0.89 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The built refactor prompt defines the overfit, uncovered-spec and beyond-spec flag classes and requires every flag line to carry one of them or to say none | 3 | 1 | 0 | 0 | 0 | 0 | 290 | 47 | 80 | 21306 | 2465805 | 173122 | 3.50 | unknown | unknown | unknown | unknown |
| The built refactor prompt reports overfit code on a FLAGS line carrying the class overfit, uncovered-spec or beyond-spec, or none, in place of the NEW_STEP line that carried it, and defines what each class names | 8 | 3 | 1 | 0 | 0 | 0 | 850 | 134 | 244 | 69083 | 7166583 | 421720 | 9.53 | 1655 | 1/2 | 3/5 | nothing-structural |
| The refactor loop in SKILL.md answers an overfit flag with one triangulating red and green pair inside the current step, adding no ledger step and no second step-done, then resumes that step's refactor loop with the budget it had left | 6 | 3 | 0 | 0 | 0 | 0 | 877 | 133 | 252 | 64214 | 8284773 | 390213 | 9.65 | 1574 | unknown | 4/5 | nothing-structural |
| SKILL.md amends the plan from an uncovered-spec flag and from no other flag class | 6 | 3 | 0 | 0 | 0 | 0 | 735 | 132 | 242 | 61155 | 7601089 | 379435 | 9.12 | 1516 | unknown | 3/5 | nothing-structural |
| The skill-refactor-leaf suite goes red on a SKILL.md whose refactor loop amends the plan from a flag class other than uncovered-spec | 2 | 1 | 0 | 0 | 0 | 0 | 302 | 35 | 66 | 26294 | 2317516 | 146447 | 3.28 | 489 | unknown | unknown | unknown |
| SKILL.md narrates a beyond-spec flag as a follow-up in the Refactor comment and in the PR body, without planning or building it in this run | 6 | 3 | 0 | 0 | 0 | 0 | 727 | 113 | 206 | 48305 | 6259707 | 350872 | 7.85 | 1371 | unknown | 1/5 | structural-owed |
| The skill-refactor-leaf suite goes red on a SKILL.md whose refactor loop plans and builds a beyond-spec flag instead of only narrating it | 7 | 3 | 0 | 0 | 0 | 0 | 1022 | 134 | 254 | 70107 | 8092308 | 436280 | 10.16 | 2663 | 1/2 | 1/5 | structural-owed |
| SKILL.md runs a step's triangulation at most once, narrating a flag raised inside that triangulation's own refactor loop about the same code instead of triangulating it again | 6 | 3 | 0 | 0 | 0 | 0 | 506 | 90 | 170 | 37679 | 4840837 | 337567 | 6.74 | 1046 | unknown | 1/5 | nothing-structural |
| The flag-class amendment guard plants a document whose granted class SKILL.md does not already name, so it still asks whether only uncovered-spec amends the plan | 4 | 2 | 0 | 0 | 0 | 0 | 381 | 48 | 92 | 25769 | 2618972 | 217089 | 4.13 | 614 | unknown | 0/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 2 | 76 | 76 | 77 | 2 | 2 | 2 | 0 | 77 | 77 | 2 | 3 | 1 | 0 | 78 | 77 | 77 | 78 | 76 | 77 | 0 | 77 | 68 | 3 | 3 | 78 | 0 | 78 | 0 | 78 | 79 | 78 | 3 | 69 | 70 | 59 | 3 | 58 | 0 | 71 | 71 | 70 | 6 | 3 | 3 | 3 | 0 | 79 | 0 | 80 | 78 | 80 | 7 | 72 | 7 |
| all | 275 | 277 | 282 | 284 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 2 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 0 | 2 | 5 | 5 | 3 | 6 | 4 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 872 | 1614 | 427413 | 49808928 | 2894705 | 64.54 |
