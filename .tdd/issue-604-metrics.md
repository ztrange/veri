### 📊 Metrics — issue 604

Wall time for the issue: 4830 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/640.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 8 | 2 | 4 | 717 | 58252 | 37333 | 0.32 |
| red | 13 | 6 | 0 | 0 | 634 | 475 | 114 | 216 | 45110 | 5496728 | 609089 | 6.88 |
| green | 14 | 6 | 1 | 0 | 1985 | 570 | 143 | 282 | 50492 | 6958383 | 592314 | 7.14 |
| refactor | 12 | 6 | 0 | 0 | 689 | 355 | 93 | 182 | 30544 | 4302587 | 515965 | 5.60 |
| pin | 1 | 1 | 0 | 0 | 28 | 20 | 5 | 10 | 1803 | 201908 | 37736 | 0.38 |
| structural | 2 | 0 | 0 | 0 | 67 | 42 | 9 | 18 | 3837 | 365517 | 76575 | 0.76 |
| transform | 1 | 0 | 1 | 0 | 39 | 22 | 5 | 10 | 1961 | 200021 | 37026 | 0.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1037 | 1.95 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| the `usage` event harvest-usage.sh appends carries a `model` key naming the one model a result record's `modelUsage` lists ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 157 | 41 | 80 | 13059 | 1779829 | 246478 | 2.59 | 340 | unknown | 0/5 | structural-owed |  |  | full |
| when `modelUsage` names more than one model, the usage event's `model` key lists every one of them ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 17 | 32 | 5839 | 766849 | 84596 | 0.95 | unknown | unknown | unknown | unknown |  |  | pin |
| when `modelUsage` names more than one model, the usage event keeps each model's own token and cost figures alongside, rather than only their sums ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 204 | 48 | 96 | 17317 | 2275808 | 259979 | 2.88 | 413 | unknown | 2/5 | nothing-structural |  |  | full |
| a result record with no `modelUsage` still yields a `usage` event with `model` empty, and harvest-usage.sh's exit code and stderr for it are unchanged ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 170 | 47 | 90 | 15502 | 2110079 | 255302 | 2.77 | 367 | unknown | 1/5 | structural-owed |  |  | full |
| metrics.sh prints a "By model" table with one row per (role, model) — role developer or verifier — carrying the same columns as "By phase" ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 334 | 81 | 156 | 32335 | 4087452 | 350612 | 4.27 | 1412 | 1/2 | 1/5 | structural-owed |  |  | full |
| the metrics report's header states the run's requested model knobs (`VERI_MODEL`, `VERI_MODEL_DEVELOPER`, `VERI_MODEL_VERIFIER`, each or "unset") next to the models that actually answered ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 269 | 65 | 126 | 23835 | 3260820 | 286648 | 3.42 | 570 | unknown | 1/5 | nothing-structural |  |  | full |
| an event log whose `usage` events carry no `model` key still produces a metrics report, its "By model" table saying the model was not recorded ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 225 | 56 | 110 | 20062 | 2678769 | 271489 | 3.11 | 582 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| the `usage` event harvest-usage.sh appends carries a `model` key naming the one model a result record's `modelUsage` lists ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 88 | 0.86 |
| when `modelUsage` names more than one model, the usage event keeps each model's own token and cost figures alongside, rather than only their sums ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 124 | 0.98 |
| a result record with no `modelUsage` still yields a `usage` event with `model` empty, and harvest-usage.sh's exit code and stderr for it are unchanged ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 106 | 0.91 |
| metrics.sh prints a "By model" table with one row per (role, model) — role developer or verifier — carrying the same columns as "By phase" ⟦criterion 3⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 137 | 1.00 |
| the metrics report's header states the run's requested model knobs (`VERI_MODEL`, `VERI_MODEL_DEVELOPER`, `VERI_MODEL_VERIFIER`, each or "unset") next to the models that actually answered ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 116 | 0.98 |
| an event log whose `usage` events carry no `model` key still produces a metrics report, its "By model" table saying the model was not recorded ⟦criterion 5⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 118 | 0.88 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 10 | 0 | 2 | 1 | 1 | 1 | 1 | 11 | 2 | 1 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 11 | 12 | 11 | 11 | 26 | 11 | 12 | 11 | 11 | 12 | 11 | 12 | 12 | 11 | 12 | 0 | 12 | 12 | 35 | 12 | 11 | 2 | 13 | 12 |
| fast | 20 | 20 | 20 | 20 | 20 | 20 | 19 | 20 | 19 | 19 | 21 | 21 | 21 | 22 | 21 | 21 | 22 | 22 | 21 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 2 | 2 | 2 | 11 | 11 | 12 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 606 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 371 | 722 | 134464 | 17583396 | 1906038 | 21.46 |
