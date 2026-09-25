### 📊 Metrics — issue 449

Wall time for the issue: 2331 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/477.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 752 | 11207 | 34265 | 0.29 |
| red | 13 | 4 | 0 | 0 | 430 | 351 | 95 | 184 | 34321 | 4116301 | 526478 | 5.72 |
| green | 8 | 4 | 0 | 0 | 713 | 256 | 76 | 148 | 24886 | 3360363 | 331020 | 3.82 |
| refactor | 8 | 4 | 0 | 0 | 302 | 155 | 44 | 86 | 15200 | 1813471 | 321860 | 3.24 |
| pin | 5 | 5 | 0 | 0 | 104 | 76 | 20 | 40 | 7513 | 754320 | 187218 | 1.80 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| step-budget.sh with neither VERI_STEP_BUDGET nor VERI_RUN_BUDGET set prints 12 then 120, each on its own line, and exits 0 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 182 | 47 | 92 | 18705 | 2080062 | 252933 | 2.81 | 526 | unknown | 0/5 | nothing-left |
| step-budget.sh prints a set VERI_STEP_BUDGET then a set VERI_RUN_BUDGET, decimal values included, in that order ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 10 | 20 | 4045 | 408076 | 76586 | 0.78 | unknown | unknown | unknown | unknown |
| A VERI_STEP_BUDGET that is not a non-negative decimal number exits 2, names VERI_STEP_BUDGET on stderr, and prints nothing on stdout ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 124 | 39 | 78 | 11686 | 1675327 | 236602 | 2.46 | 320 | unknown | 0/5 | nothing-left |
| A VERI_RUN_BUDGET that is not a non-negative decimal number exits 2, names VERI_RUN_BUDGET on stderr, and prints nothing on stdout ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 162 | 45 | 88 | 15185 | 1946392 | 240592 | 2.62 | 366 | unknown | 2/5 | structural-owed |
| Both budget variables invalid at once exits 2 and prints nothing on stdout, not the first figure then a failure ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 14 | 26 | 5293 | 574502 | 80951 | 0.87 | unknown | unknown | unknown | unknown |
| Either budget variable exported as the empty string exits 2 rather than falling back to its default ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 24 | 4282 | 517107 | 78339 | 0.82 | unknown | unknown | unknown | unknown |
| A budget of 0 is accepted for either variable and printed back ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 12 | 22 | 4147 | 464540 | 78412 | 0.80 | unknown | unknown | unknown | unknown |
| step-budget.sh given any argument exits 2 ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 39 | 76 | 12575 | 1623444 | 238356 | 2.48 | 321 | unknown | 0/5 | nothing-left |
| The step-budget suite lives in skills/tdd/scripts/tests/unit/ and its header states the fast-tier bar: no git, no network, no servers, no real sleep, no nested suites ⟦criterion 9⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 16 | 32 | 6002 | 755005 | 83805 | 0.94 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 81 | 0 | 45 | 0 | 0 | 83 | 0 | 0 | 0 | 0 | 83 | 0 | 0 | 0 | 0 | 0 | 0 | 86 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 82 | 0 | 0 | 1 |
| fast | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 236 | 460 | 82672 | 10055662 | 1400841 | 14.87 |
