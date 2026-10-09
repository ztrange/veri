### 📊 Metrics — issue 1250

Wall time for the issue: 4994 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1284.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 1 | 2 | 1104 | 11966 | 39930 | 0.17 |
| red | 9 | 3 | 0 | 0 | 432 | 236 | 52 | 100 | 21553 | 2442565 | 421959 | 3.74 |
| green | 6 | 3 | 0 | 0 | 866 | 109 | 34 | 64 | 9999 | 1448853 | 256783 | 1.99 |
| refactor | 6 | 3 | 0 | 0 | 489 | 122 | 28 | 56 | 8205 | 1250514 | 262081 | 1.96 |
| pin | 1 | 1 | 0 | 0 | 28 | 17 | 4 | 8 | 1297 | 170917 | 43271 | 0.22 |
| predicate | 1 | 0 | 0 | 0 | 22 | 15 | 3 | 6 | 1523 | 114619 | 40918 | 0.38 |
| structural | 1 | 0 | 0 | 0 | 50 | 25 | 6 | 12 | 2676 | 277871 | 42873 | 0.45 |
| transform | 1 | 1 | 0 | 0 | 41 | 13 | 4 | 8 | 942 | 167686 | 41420 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 1048 | 219 | 51 | 100 | 16444 | 2142261 | 507785 | 2.62 |
| developer | claude-opus-5-5 | 14 | 0 | 0 | 0 | 895 | 328 | 81 | 156 | 30855 | 3742730 | 641450 | 6.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Through orchestrate.sh, a non-numeric VERI_CONDUCTOR_STOP_TIMEOUT (`abc`) exits 2 before any conductor starts, with one stderr line naming the variable and the value and no traceback ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 163 | 39 | 72 | 11892 | 1746385 | 271666 | 2.21 | 655 | unknown | 0/5 | structural-owed |  |  | full |
| Through orchestrate.sh, a non-finite VERI_CONDUCTOR_STOP_TIMEOUT (`nan`, `inf`) is refused the same way: exit 2 before any conductor starts, one stderr line naming the variable and the value ⟦added⟧ ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 134 | 33 | 66 | 12101 | 1478685 | 307247 | 2.44 | 719 | 1/2 | 0/5 | nothing-structural |  |  | full |
| Through orchestrate.sh, a zero or negative VERI_CONDUCTOR_STOP_TIMEOUT (`0`, `-1`) is refused the same way: exit 2 before any conductor starts, one stderr line naming the variable and the value ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 136 | 33 | 66 | 12004 | 1488156 | 309053 | 2.46 | 677 | 1/2 | 0/5 | nothing-structural |  |  | full |
| An unset or empty VERI_CONDUCTOR_STOP_TIMEOUT bounds the stopped conductor's drain at 10 s, and a positive value (`0.5`) is used as the bound as given ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 104 | 26 | 50 | 10198 | 1159799 | 221339 | 1.85 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Through orchestrate.sh, a non-numeric VERI_CONDUCTOR_STOP_TIMEOUT (`abc`) exits 2 before any conductor starts, with one stderr line naming the variable and the value and no traceback ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 177 | 0.68 |
| Through orchestrate.sh, a non-finite VERI_CONDUCTOR_STOP_TIMEOUT (`nan`, `inf`) is refused the same way: exit 2 before any conductor starts, one stderr line naming the variable and the value ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 175 | 0.66 |
| Through orchestrate.sh, a zero or negative VERI_CONDUCTOR_STOP_TIMEOUT (`0`, `-1`) is refused the same way: exit 2 before any conductor starts, one stderr line naming the variable and the value ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 137 | 0.62 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 14 | 20 | 14 | 16 | 16 | 20 | 3 | 0 | 26 | 15 | 16 | 18 | 2 | 0 | 16 | 3 | 18 | 15 | 3 |
| fast | 77 | 75 | 79 | 80 | 76 | 73 | 80 | 77 | 82 |  |  |  |  |  |  |  |  |  |  |
| target | 15 | 15 | 16 | 2 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 132 | 256 | 47299 | 5884991 | 1149235 | 9.12 |
