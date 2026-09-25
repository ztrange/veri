### 📊 Metrics — issue 175

Wall time for the issue: 6183 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 11 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/443.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 46 | 42 | 6 | 8 | 3501 | 161338 | 41960 | 0.59 |
| red | 26 | 10 | 2 | 0 | 5154 | 2757 | 397 | 732 | 213881 | 22857015 | 1524889 | 29.65 |
| green | 27 | 11 | 2 | 0 | 6110 | 2574 | 470 | 884 | 203169 | 26688540 | 1565469 | 29.35 |
| refactor | 22 | 11 | 0 | 0 | 4051 | 2010 | 310 | 608 | 154875 | 17747995 | 1167740 | 22.42 |
| pin | 1 | 1 | 0 | 0 | 75 | 52 | 12 | 20 | 4483 | 522687 | 49123 | 0.86 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 1780 | 6.72 | 380 | 3.87 |
| green | 2415 | 6.42 | 340 | 2.01 |
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
| SKILL.md describes the refactor leaf report footer as the built prompt actually writes it, naming no line the prompt does not emit ⟦added⟧ ⟦criterion 1⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 207 | 44 | 86 | 18497 | 2217542 | 196835 | 2.39 | unknown | unknown | unknown | unknown |
| The conductor grows the plan from the refactor leaf FLAGS classes alone, reading no NEW_STEP or CANDIDATES line from the leaf anywhere in SKILL.md ⟦added⟧ ⟦criterion 3⟧ | 8 | 4 | 0 | 0 | 0 | 0 | 486 | 93 | 184 | 42123 | 5030049 | 418981 | 5.20 | 1298 | unknown | 2/5 | structural-owed |
| A blind verify-refactor verdict reports a finding as a FLAGS line of the same three classes, so no plan amendment comes from a verifier NEW_STEP line ⟦added⟧ ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 593 | 108 | 212 | 53240 | 5880850 | 506723 | 6.30 | 2264 | 2/2 | 0/5 | nothing-left |
| The two guard suites that replant SKILL.md, beyond-spec-narration-guard and flag-class-amendment-guard, pass over the committed tree and still see their one planted case fail alone, now that skill-refactor-leaf.test.sh builds the refactor prompt | 6 | 2 | 1 | 0 | 0 | 0 | 417 | 78 | 156 | 38636 | 5040206 | 331937 | 4.44 | 1352 | 1/2 | 1/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 2 | 76 | 76 | 77 | 2 | 2 | 2 | 0 | 77 | 77 | 2 | 3 | 1 | 0 | 78 | 77 | 77 | 78 | 76 | 77 | 0 | 77 | 68 | 3 | 3 | 78 | 0 | 78 | 0 | 78 | 79 | 78 | 3 | 69 | 70 | 59 | 3 | 58 | 0 | 71 | 71 | 70 | 6 | 3 | 3 | 3 | 0 | 79 | 0 | 80 | 78 | 80 | 7 | 72 | 7 | 4 | 4 | 66 | 0 | 82 | 4 | 9 | 0 | 4 | 0 | 4 | 0 | 0 | 80 | 0 | 81 | 0 | 84 | 81 | 0 | 82 | 2 | 159 | 3 | 0 | 3 | 3 | 0 | 58 | 0 | 88 | 0 | 88 | 128 | 0 | 92 | 0 | 91 | 4 | 9 | 9 | 4 | 4 |
| all | 275 | 277 | 282 | 284 | 332 | 325 | 322 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 0 | 2 | 5 | 5 | 3 | 6 | 4 | 7 | 4 | 4 | 3 | 3 | 8 | 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 1195 | 2252 | 579909 | 67977575 | 4349181 | 82.87 |
