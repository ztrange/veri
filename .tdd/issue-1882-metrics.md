### 📊 Metrics — issue 1882

Wall time for the issue: 2482 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1933.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.44 over 65 turns, in 1 sessions.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84838 |
| 2 | $0.03 | 86514 |
| 3 | $0.03 | 88373 |
| 4 | $0.02 | 88710 |
| 5 | $0.02 | 89061 |
| 6 | $0.02 | 89420 |
| 7 | $0.02 | 89778 |
| 8 | $0.02 | 90359 |
| 9 | $0.02 | 90666 |
| 10 | $0.05 | 94105 |
| 11 | $0.03 | 95439 |
| 12 | $0.03 | 97134 |
| 13 | $0.02 | 97689 |
| 14 | $0.03 | 98506 |
| 15 | $0.02 | 99112 |
| 16 | $0.03 | 100536 |
| 17 | $0.02 | 101044 |
| 18 | $0.03 | 101743 |
| 19 | $0.03 | 102587 |
| 20 | $0.02 | 103051 |
| 21 | $0.03 | 104325 |
| 22 | $0.03 | 105205 |
| 23 | $0.02 | 105463 |
| 24 | $0.03 | 106076 |
| 25 | $0.03 | 106555 |
| 26 | $0.02 | 106851 |
| 27 | $0.03 | 107576 |
| 28 | $0.03 | 108131 |
| 29 | $0.03 | 109035 |
| 30 | $0.03 | 109668 |
| 31 | $0.03 | 110330 |
| 32 | $0.03 | 110960 |
| 33 | $0.03 | 112040 |
| 34 | $0.03 | 112714 |
| 35 | $0.03 | 113874 |
| 36 | $0.03 | 115064 |
| 37 | $0.04 | 116818 |
| 38 | $0.03 | 117715 |
| 39 | $0.03 | 118687 |
| 40 | $0.03 | 119319 |
| 41 | $0.03 | 120242 |
| 42 | $0.05 | 123048 |
| 43 | $0.04 | 124308 |
| 44 | $0.03 | 124649 |
| 45 | $0.03 | 125363 |
| 46 | $0.03 | 125808 |
| 47 | $0.03 | 126297 |
| 48 | $0.03 | 127188 |
| 49 | $0.03 | 127567 |
| 50 | $0.04 | 128847 |
| 51 | $0.03 | 129158 |
| 52 | $0.03 | 129726 |
| 53 | $0.04 | 131666 |
| 54 | $0.03 | 132146 |
| 55 | $0.04 | 133436 |
| 56 | $0.03 | 134364 |
| 57 | $0.03 | 134989 |
| 58 | $0.03 | 135239 |
| 59 | $0.03 | 135462 |
| 60 | $0.03 | 135729 |
| 61 | $0.03 | 135951 |
| 62 | $0.03 | 136629 |
| 63 | $0.04 | 137749 |
| 64 | $0.03 | 138237 |
| 65 | $0.03 | 138695 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 30 | 26 | 2 | 4 | 3053 | 33872 | 27543 | 0.10 |
| red | 9 | 3 | 0 | 0 | 208 | 158 | 42 | 82 | 12702 | 1214912 | 154664 | 0.64 |
| green | 6 | 3 | 0 | 0 | 301 | 108 | 32 | 52 | 8139 | 724842 | 87055 | 0.37 |
| refactor | 6 | 3 | 0 | 0 | 189 | 115 | 26 | 48 | 7451 | 697809 | 94892 | 0.38 |
| pin | 3 | 3 | 0 | 0 | 63 | 44 | 11 | 22 | 3145 | 289341 | 41550 | 0.16 |
| predicate | 1 | 0 | 0 | 0 | 17 | 14 | 4 | 8 | 763 | 104116 | 12844 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 13 | 1 | 0 | 395 | 200 | 43 | 84 | 13633 | 1073559 | 191065 | 0.72 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 413 | 265 | 74 | 132 | 21620 | 1991333 | 227483 | 0.98 |

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
| add-ledger-step.sh refuses a replaces-case step whose clause mixes quoted and unquoted names (such as `replaces 'a', b, 'c' in t/x.test.sh`): it exits 1 with a stderr line naming the step and leaves the ledger file unchanged; pinned by a small in-process unit case ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 115 | 30 | 56 | 8095 | 804296 | 93363 | 0.39 | 350 | unknown | 1/5 | nothing-structural |  |  | full |
| unreplaced-cases.sh answers a replaces-case step whose clause mixes quoted and unquoted names (such as `replaces 'a', b, 'c' in t/x.test.sh`) with exit 2 and exactly one stderr line naming the step; pinned by a small in-process unit case ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 10 | 20 | 3461 | 295682 | 34161 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| replaces-case-survivors.sh answers a replaces-case step whose clause mixes quoted and unquoted names (an unreadable clause, such as `replaces 'a', b, 'c' in t/x.test.sh`) with exit 2 and exactly one stderr line naming the step; pinned by a small in-process unit case ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 9 | 18 | 2900 | 256181 | 31216 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| replaces-case-survivors.sh answers a replaces-case step whose clause is fully unquoted (such as `replaces a, b in t/x.test.sh`) with exit 2 and exactly one stderr line naming the step, where it exits 3 today; pinned by a small in-process unit case ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 23 | 40 | 5685 | 540929 | 88070 | 0.33 | 214 | unknown | 0/5 | structural-owed |  |  | full |
| replaces-case-survivors.sh answers a replaces-case step whose quoted clause names a suite that is not a `*.test.sh` file (such as `replaces 'a' in t/x.py`) with exit 2 and exactly one stderr line naming the step, where it exits 3 today; pinned by a small in-process unit case ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 31 | 54 | 8151 | 794872 | 97474 | 0.40 | 238 | unknown | 1/5 | nothing-structural |  |  | full |
| pin (a regression pin, no production change: the behaviour already holds, so Red reports AGAINST_UNMODIFIED: PASSES and the step takes the verify-pin path) that build-verify-prompt.sh's red phase, given a step whose text ends with the `⟦replaces-case⟧` mark (the mark not at its start), renders the per-case verify-red wording `judge each of them`; a small in-process unit case that goes red if `is_replaces_case_step` at build_verify_prompt.py:160 is swapped for a `startswith` check ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 54 | 12 | 24 | 3908 | 339060 | 46721 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| add-ledger-step.sh refuses a replaces-case step whose clause mixes quoted and unquoted names (such as `replaces 'a', b, 'c' in t/x.test.sh`): it exits 1 with a stderr line naming the step and leaves the ledger file unchanged; pinned by a small in-process unit case ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 75 | 0.12 |
| replaces-case-survivors.sh answers a replaces-case step whose clause is fully unquoted (such as `replaces a, b in t/x.test.sh`) with exit 2 and exactly one stderr line naming the step, where it exits 3 today; pinned by a small in-process unit case ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 43 | 0.10 |
| replaces-case-survivors.sh answers a replaces-case step whose quoted clause names a suite that is not a `*.test.sh` file (such as `replaces 'a' in t/x.py`) with exit 2 and exactly one stderr line naming the step, where it exits 3 today; pinned by a small in-process unit case ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 71 | 0.16 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 0 | 2 | 34 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 0 | 2 | 4 |
| fast | 15 | 15 | 15 | 15 | 15 | 16 | 15 | 16 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 117 | 216 | 35253 | 3064892 | 418548 | 1.71 |
