### 📊 Metrics — issue 907

Wall time for the issue: 5216 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/910.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 2 | 4 | 1219 | 53675 | 38175 | 0.18 |
| red | 12 | 6 | 0 | 0 | 787 | 413 | 103 | 198 | 35289 | 5091782 | 555310 | 5.18 |
| green | 12 | 6 | 0 | 0 | 2121 | 417 | 100 | 196 | 33395 | 4464691 | 506970 | 4.51 |
| refactor | 12 | 6 | 0 | 0 | 510 | 230 | 57 | 112 | 17001 | 2286934 | 485094 | 3.68 |
| predicate | 8 | 0 | 0 | 0 | 181 | 164 | 23 | 46 | 10642 | 770529 | 295806 | 2.73 |
| structural | 4 | 0 | 0 | 0 | 289 | 135 | 25 | 50 | 10340 | 1101508 | 170660 | 1.79 |
| transform | 4 | 0 | 4 | 0 | 45 | 36 | 12 | 24 | 3287 | 477804 | 55479 | 0.35 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 23 | 19 | 4 | 0 | 1808 | 350 | 115 | 224 | 34400 | 4519418 | 789711 | 4.41 |
| developer | claude-opus-5-5 | 30 | 0 | 0 | 0 | 2137 | 1055 | 207 | 406 | 76773 | 9727505 | 1317783 | 14.02 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 180 | 1.40 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The Draft PR step's verdict-rebase launch reads its VERI_STEP as the open step or, when none is open, the last done step, the same fallback its --step argument already spells | 6 | 3 | 0 | 0 | 0 | 0 | 151 | 41 | 78 | 12534 | 1832805 | 258668 | 2.17 | 595 | unknown | 0/5 | structural-owed |  |  | full |
| The revise diff prompt line of Revising on a REJECT reads its build-develop-prompt.sh step argument as the open step or, when none is open, the last done step | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 43 | 86 | 14189 | 1964992 | 251887 | 2.17 | 621 | unknown | 0/5 | structural-owed |  |  | full |
| The revise-exhausted path reads its step text — the build-develop-prompt.sh exhausted argument, the develop-exhausted launch's VERI_STEP and the step-escalated mark's step — as the open step or, when none is open, the last done step | 6 | 3 | 0 | 0 | 0 | 0 | 213 | 44 | 86 | 17564 | 2071792 | 267744 | 2.37 | 730 | unknown | 0/5 | structural-owed |  |  | full |
| Bailing reads its step text — the preserve-attempt.sh step argument and the bail mark's VERI_STEP — as the open step or, when none is open, the last done step | 6 | 3 | 0 | 0 | 0 | 0 | 194 | 43 | 84 | 15382 | 2040608 | 267773 | 2.36 | 603 | unknown | 0/5 | structural-owed |  |  | full |
| Stopping's stop mark reads its VERI_STEP as the open step or, when none is open, the last done step | 6 | 3 | 0 | 0 | 0 | 0 | 184 | 50 | 96 | 15092 | 2251398 | 259627 | 2.30 | 563 | unknown | 0/5 | structural-owed |  |  | full |
| Resume's resume mark reads its VERI_STEP as the open step or, when none is open, the last done step | 22 | 3 | 4 | 0 | 0 | 0 | 477 | 99 | 196 | 35193 | 4031653 | 763620 | 6.88 | 497 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The Draft PR step's verdict-rebase launch reads its VERI_STEP as the open step or, when none is open, the last done step, the same fallback its --step argument already spells | 1 | 0/5 | structural-owed | PASS | 0 | 91 | 0.57 |
| The revise diff prompt line of Revising on a REJECT reads its build-develop-prompt.sh step argument as the open step or, when none is open, the last done step | 1 | 0/5 | structural-owed | PASS | 0 | 80 | 0.59 |
| The revise-exhausted path reads its step text — the build-develop-prompt.sh exhausted argument, the develop-exhausted launch's VERI_STEP and the step-escalated mark's step — as the open step or, when none is open, the last done step | 1 | 0/5 | structural-owed | PASS | 0 | 79 | 0.59 |
| Bailing reads its step text — the preserve-attempt.sh step argument and the bail mark's VERI_STEP — as the open step or, when none is open, the last done step | 1 | 0/5 | structural-owed | PASS | 0 | 113 | 0.77 |
| Stopping's stop mark reads its VERI_STEP as the open step or, when none is open, the last done step | 1 | 0/5 | structural-owed | PASS | 0 | 79 | 0.62 |
| Resume's resume mark reads its VERI_STEP as the open step or, when none is open, the last done step | 1 | 0/5 | structural-owed | PASS | 0 | 68 | 0.55 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 22 | 72 | 22 | 23 | 22 | 0 | 74 | 0 | 23 | 1 | 0 | 1 | 0 | 0 | 22 | 22 | 0 | 84 | 0 | 24 | 23 | 85 | 51 | 0 | 23 | 23 | 0 | 0 | 23 | 0 | 79 | 0 | 0 | 23 | 24 | 23 | 80 | 23 | 24 | 23 | 24 | 24 |
| fast | 16 | 14 | 15 | 15 | 15 | 15 | 15 | 16 | 16 | 16 | 14 | 15 | 14 | 15 | 14 | 15 | 14 | 14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 21 | 23 | 23 | 23 | 23 | 23 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 322 | 630 | 111173 | 14246923 | 2107494 | 18.43 |
