### 📊 Metrics — issue 1546

Wall time for the issue: 2452 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1557.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 1 | 2 | 1182 | 12193 | 37930 | 0.16 |
| red | 5 | 2 | 0 | 0 | 158 | 128 | 27 | 54 | 13765 | 1368690 | 249558 | 1.27 |
| green | 4 | 2 | 0 | 0 | 1049 | 112 | 33 | 66 | 12563 | 1772498 | 197419 | 1.09 |
| refactor | 4 | 2 | 0 | 0 | 195 | 66 | 22 | 42 | 5639 | 1005243 | 183070 | 0.89 |
| pin | 1 | 1 | 0 | 0 | 23 | 15 | 4 | 8 | 1663 | 175357 | 44313 | 0.21 |
| predicate | 1 | 0 | 0 | 0 | 13 | 11 | 3 | 6 | 671 | 115824 | 42129 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 535 | 138 | 36 | 70 | 13423 | 1588881 | 351605 | 1.70 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 916 | 205 | 54 | 108 | 22060 | 2860924 | 402814 | 2.12 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On the pin path of a `⟦replaces-case⟧` step (SKILL.md's paragraph beginning "A `⟦replaces-case⟧` step whose Red reports `AGAINST_UNMODIFIED: PASSES`"), the deletion-only green leaf is followed by `replaces-case-survivors.sh` and, on survivors (exit 1), by the same bounded relaunch the Green path uses — relaunch the green leaf naming the survivors, record the relaunch as an event, launch no verifier on that green, each relaunch spending one `REVISE_BUDGET` attempt, `cause=revise-exhausted` when spent — all before that path's verify-green launches; pinned by a prose case in a skill-*.test.sh suite that goes red when the pin-path paragraph omits the survivors check ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 115 | 35 | 68 | 11527 | 1673391 | 283034 | 1.41 | 546 | unknown | 0/5 | nothing-left |  |  | full |
| SKILL.md runs `unreplaced-cases.sh` right after the Red report is written — after develop-red, and after a red revise against `.tdd/revise-red-<k>.out` — before verify-red launches, never first in Green's Verify sub-step; pinned by a prose order case that checks every place SKILL.md names `unreplaced-cases.sh` as a run (not only the first) and goes red when any one of them is moved after a verify-red launch; the existing #1521 and #1406 prose cases stay green ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 155 | 40 | 80 | 16377 | 2085760 | 291196 | 1.54 | 1002 | unknown | 1/5 | nothing-structural |  |  | full |
| SKILL.md runs `replaces-case-survivors.sh` after the green leaf and before verify-green at every place it names that run (the Green path and the pin path alike), and nowhere runs it before `unreplaced-cases.sh`; pinned by a prose order case that checks every place each of the two scripts is named as a run, not only the first, and goes red when either one is moved ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 62 | 14 | 28 | 6397 | 678461 | 142259 | 0.70 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| On the pin path of a `⟦replaces-case⟧` step (SKILL.md's paragraph beginning "A `⟦replaces-case⟧` step whose Red reports `AGAINST_UNMODIFIED: PASSES`"), the deletion-only green leaf is followed by `replaces-case-survivors.sh` and, on survivors (exit 1), by the same bounded relaunch the Green path uses — relaunch the green leaf naming the survivors, record the relaunch as an event, launch no verifier on that green, each relaunch spending one `REVISE_BUDGET` attempt, `cause=revise-exhausted` when spent — all before that path's verify-green launches; pinned by a prose case in a skill-*.test.sh suite that goes red when the pin-path paragraph omits the survivors check ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 93 | 0.44 |
| SKILL.md runs `unreplaced-cases.sh` right after the Red report is written — after develop-red, and after a red revise against `.tdd/revise-red-<k>.out` — before verify-red launches, never first in Green's Verify sub-step; pinned by a prose order case that checks every place SKILL.md names `unreplaced-cases.sh` as a run (not only the first) and goes red when any one of them is moved after a verify-red launch; the existing #1521 and #1406 prose cases stay green ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 102 | 0.45 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 0 | 0 | 238 | 238 | 1 | 0 | 1 | 1 |
| fast | 59 | 56 | 54 | 57 | 59 | 56 | 57 |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 90 | 178 | 35483 | 4449805 | 754419 | 3.82 |
