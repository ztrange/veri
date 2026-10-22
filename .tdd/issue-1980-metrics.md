### 📊 Metrics — issue 1980

Wall time for the issue: 1002 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2104.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 18 | 7 | 14 | 1803 | 209576 | 18056 | 0.08 |
| red | 5 | 2 | 0 | 0 | 126 | 93 | 29 | 54 | 9467 | 808000 | 87793 | 0.40 |
| green | 4 | 2 | 0 | 0 | 124 | 66 | 19 | 34 | 5452 | 463109 | 58126 | 0.25 |
| refactor | 4 | 2 | 0 | 0 | 50 | 23 | 12 | 20 | 2410 | 240781 | 51981 | 0.18 |
| pin | 1 | 1 | 0 | 0 | 18 | 10 | 4 | 8 | 1100 | 103931 | 13605 | 0.06 |
| cover | 1 | 0 | 0 | 0 | 35 | 22 | 8 | 16 | 2069 | 224386 | 13823 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 159 | 84 | 32 | 64 | 8507 | 852662 | 113068 | 0.45 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 214 | 148 | 47 | 82 | 13794 | 1197121 | 130316 | 0.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| suite-reported.sh exits 0 for a retried leaf `develop-red-2` whose report has no SUITE: line but carries every key of an exempt format develop-red.md declares, exactly as it does for `develop-red`, finding the prompt through leaf_role's parse of the leaf name (its phase), not by stripping the name itself; pinned by a small in-process unit case under skills/tdd/scripts/tests/py/unit/ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 32 | 56 | 8698 | 807198 | 94045 | 0.40 | 233 | unknown | 0/5 | nothing-left |  |  | full |
| suite-reported.sh exits 0 for a retried leaf `develop-structural-3` whose report has no SUITE: line but carries every key of an exempt format develop-structural.md declares (such as its out-of-bounds skip), exactly as it does for `develop-structural`; pinned by a small in-process unit case under skills/tdd/scripts/tests/py/unit/ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 20 | 3090 | 285268 | 31484 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| suite-reported.sh, given a leaf name whose prompt file cannot be found (no develop prompt for its parsed phase, or a name leaf_role refuses), exits 2 and writes exactly one stderr line naming that leaf, instead of silently treating the leaf as exempting nothing; pinned by a small in-process unit case under skills/tdd/scripts/tests/py/unit/ ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 98 | 30 | 56 | 8710 | 747741 | 99799 | 0.41 | 204 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| suite-reported.sh exits 0 for a retried leaf `develop-red-2` whose report has no SUITE: line but carries every key of an exempt format develop-red.md declares, exactly as it does for `develop-red`, finding the prompt through leaf_role's parse of the leaf name (its phase), not by stripping the name itself; pinned by a small in-process unit case under skills/tdd/scripts/tests/py/unit/ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 26 | 0.09 |
| suite-reported.sh, given a leaf name whose prompt file cannot be found (no develop prompt for its parsed phase, or a name leaf_role refuses), exits 2 and writes exactly one stderr line naming that leaf, instead of silently treating the leaf as exempting nothing; pinned by a small in-process unit case under skills/tdd/scripts/tests/py/unit/ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 24 | 0.09 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 2 | 0 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 6 |
| fast | 5 | 6 | 5 | 5 | 4 | 5 |  |  |  |  |  |  |  |  |  |
| target | 3 | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 79 | 146 | 22301 | 2049783 | 243384 | 1.04 |
