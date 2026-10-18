### 📊 Metrics — issue 1741

Wall time for the issue: 2331 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1749.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 1 | 2 | 1306 | 0 | 30367 | 0.09 |
| red | 13 | 4 | 0 | 0 | 1238 | 359 | 92 | 182 | 32472 | 2979357 | 329471 | 1.45 |
| green | 8 | 4 | 0 | 0 | 669 | 130 | 44 | 88 | 13019 | 1285284 | 128940 | 0.58 |
| refactor | 8 | 4 | 0 | 0 | 279 | 58 | 25 | 50 | 5019 | 651560 | 114002 | 0.40 |
| pin | 5 | 5 | 0 | 0 | 161 | 74 | 27 | 54 | 8028 | 739790 | 94648 | 0.39 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 18 | 18 | 0 | 0 | 973 | 252 | 78 | 156 | 23920 | 2089081 | 322722 | 1.26 |
| developer | claude-sonnet-5-5 | 17 | 0 | 0 | 0 | 1387 | 380 | 111 | 220 | 35924 | 3566910 | 374706 | 1.65 |

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
| supervise.sh refuses a develop-green launch (exit 2, no leaf launched — a stub claude never runs — and exactly one stderr line naming the step and the missing verify-red PASS) when the run's event log holds, for that step, a red leaf launch followed only by a verify-red REJECT; a verdict recorded for another step does not count ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 109 | 33 | 66 | 9365 | 1027690 | 126804 | 0.51 | 498 | unknown | 0/5 | nothing-left |  |  | full |
| supervise.sh refuses develop-green (exit 2, no leaf, one stderr line naming the step and the missing verify-red PASS) when the step's latest red leaf launch has no verdict recorded after it at all ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 22 | 4070 | 322864 | 33706 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| supervise.sh launches develop-green as today (stub claude runs, its exit status recorded) when the run's event log holds a verify-red PASS for that step after the step's latest red leaf launch ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 13 | 26 | 4444 | 394365 | 35513 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| supervise.sh launches develop-green as today when the run's event log holds a verify-pin PASS for that step after the step's latest red leaf launch (the pin path) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 28 | 54 | 7926 | 778177 | 101816 | 0.41 | 401 | unknown | 0/5 | nothing-left |  |  | full |
| supervise.sh refuses develop-green (exit 2, no leaf, one stderr line naming the step and the missing verdict) when the step's only verify-red PASS was recorded before a later red leaf launch of that step (a revise-red attempt launched after the PASS) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 14 | 28 | 4447 | 427734 | 36812 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| supervise.sh still launches develop-green as today on a step whose text carries ⟦ci-repair⟧, which SKILL.md sends to Green on AGAINST_UNMODIFIED: PASSES with no verify-red or verify-pin, so the guard never blocks the procedure's own path | 6 | 3 | 0 | 0 | 0 | 0 | 93 | 30 | 60 | 9449 | 886572 | 99212 | 0.43 | 405 | unknown | 0/5 | nothing-left |  |  | full |
| supervise.sh launches develop-green as today (stub claude runs, its exit status recorded) on a CI-repair step when VERI_STEP carries that step's full ledger text, mark included, exactly as next-unchecked.sh prints it, after a red leaf launch with no verdict recorded; the case passes the real step text, never a step number ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 32 | 64 | 9494 | 932988 | 134817 | 0.53 | 512 | unknown | 0/5 | nothing-left |  |  | full |
| supervise.sh still refuses develop-green (exit 2, no leaf, one stderr line naming the step and the missing verdict) on a step without the CI-repair mark whose ledger is present, when VERI_STEP carries that step's full ledger text and its latest red leaf launch has no verdict; the case passes the real step text, never a step number ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 16 | 32 | 5352 | 546900 | 58955 | 0.26 | unknown | unknown | unknown | unknown |  |  | pin |
| a develop-green launch supervise.sh refuses for a missing verdict leaves no trace of a launch: no launch event is appended to .tdd/events.jsonl and no .tdd/leaf.owner file is written ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 11 | 22 | 3991 | 338701 | 39426 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.sh refuses a develop-green launch (exit 2, no leaf launched — a stub claude never runs — and exactly one stderr line naming the step and the missing verify-red PASS) when the run's event log holds, for that step, a red leaf launch followed only by a verify-red REJECT; a verdict recorded for another step does not count ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 73 | 0.10 |
| supervise.sh launches develop-green as today when the run's event log holds a verify-pin PASS for that step after the step's latest red leaf launch (the pin path) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 72 | 0.11 |
| supervise.sh still launches develop-green as today on a step whose text carries ⟦ci-repair⟧, which SKILL.md sends to Green on AGAINST_UNMODIFIED: PASSES with no verify-red or verify-pin, so the guard never blocks the procedure's own path | 1 | 0/5 | nothing-left | PASS | 0 | 68 | 0.09 |
| supervise.sh launches develop-green as today (stub claude runs, its exit status recorded) on a CI-repair step when VERI_STEP carries that step's full ledger text, mark included, exactly as next-unchecked.sh prints it, after a red leaf launch with no verdict recorded; the case passes the real step text, never a step number ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 66 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 32 | 33 | 0 | 36 | 33 | 32 | 33 | 33 | 32 | 32 | 32 | 0 | 35 | 32 | 32 | 31 | 31 | 35 | 32 | 31 | 31 | 32 | 0 | 36 | 31 | 34 | 31 | 31 |
| fast | 21 | 20 | 18 | 18 | 17 | 16 | 16 | 18 | 17 | 16 | 17 | 17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 1 | 0 | 32 | 29 | 33 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 2 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 189 | 376 | 59844 | 5655991 | 697428 | 2.91 |
