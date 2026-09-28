### 📊 Metrics — issue 505

Wall time for the issue: 3583 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/531.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 2 | 4 | 1037 | 56155 | 35280 | 0.31 |
| red | 6 | 2 | 0 | 0 | 952 | 184 | 46 | 86 | 18770 | 1994533 | 256095 | 2.82 |
| green | 6 | 2 | 1 | 0 | 1385 | 184 | 47 | 94 | 18704 | 2142834 | 209516 | 2.48 |
| refactor | 4 | 2 | 0 | 0 | 284 | 94 | 23 | 46 | 8158 | 979801 | 160060 | 1.64 |
| pin | 1 | 1 | 0 | 0 | 106 | 19 | 5 | 10 | 1921 | 196775 | 37382 | 0.38 |
| structural | 1 | 0 | 0 | 0 | 53 | 9 | 3 | 6 | 906 | 102130 | 34086 | 0.31 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1083 | 1.43 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| parallel-conductors.sh exits 2, naming VERI_MAX_ISSUES and the value, when VERI_MAX_ISSUES is set to a value that is not a whole number >= 1 (a word like abc, zero, a negative, a fraction), and launches no conductor ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 234 | 53 | 106 | 23717 | 2472984 | 300958 | 3.38 | 1307 | 1/2 | 1/5 | structural-owed |  |  | full |
| parallel-conductors.sh exits 2, naming VERI_MAX_ISSUES, when VERI_MAX_ISSUES is set but empty, and launches no conductor ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 194 | 53 | 102 | 18168 | 2200061 | 277705 | 3.03 | 1414 | 1/2 | 0/5 | structural-owed |  |  | full |
| with VERI_MAX_ISSUES unset, parallel-conductors.sh applies no cap and launches every solvable issue, unchanged ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 15 | 28 | 5668 | 640898 | 84390 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| parallel-conductors.sh exits 2, naming VERI_MAX_ISSUES and the value, when VERI_MAX_ISSUES is set to a value that is not a whole number >= 1 (a word like abc, zero, a negative, a fraction), and launches no conductor ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 182 | 0.87 |
| parallel-conductors.sh exits 2, naming VERI_MAX_ISSUES, when VERI_MAX_ISSUES is set but empty, and launches no conductor ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 102 | 0.77 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 41 | 41 | 38 | 38 | 38 | 38 | 39 | 40 | 38 | 40 | 40 | 39 | 39 | 41 | 39 |
| all | 502 | 506 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 4 | 4 | 5 | 4 | 5 | 5 | 4 | 4 |  |  |  |  |  |  |  |
| target | 39 | 41 | 39 | 41 | 41 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 126 | 246 | 49496 | 5472228 | 732419 | 7.94 |
