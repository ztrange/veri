### 📊 Metrics — issue 591

Wall time for the issue: 6090 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/597.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 11 | 2 | 4 | 988 | 56452 | 38017 | 0.34 |
| red | 10 | 5 | 0 | 0 | 696 | 442 | 93 | 176 | 41020 | 4521884 | 474413 | 5.52 |
| green | 10 | 5 | 0 | 0 | 1225 | 313 | 80 | 158 | 28083 | 3609410 | 418205 | 4.63 |
| refactor | 10 | 5 | 0 | 0 | 2246 | 270 | 63 | 126 | 21199 | 2853282 | 432077 | 4.45 |
| structural | 2 | 0 | 0 | 0 | 166 | 56 | 10 | 20 | 5101 | 410580 | 75747 | 0.79 |
| transform | 1 | 1 | 0 | 0 | 46 | 18 | 5 | 10 | 1721 | 199512 | 37078 | 0.37 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| solvable-issues.sh prints the same numbers and exits 0 for a VERI_GH_JSON fixture whose issues.json is larger than 256 KiB as for the same issues with short bodies, and no argument it hands python3 carries the JSON document ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 40 | 78 | 16199 | 1775858 | 252391 | 2.70 | 431 | unknown | 0/5 | nothing-left |  |  | full |
| workqueue.sh reads an issues document larger than 256 KiB and gives the same output and exit code as for a small one, and no argument it hands python3 carries the JSON document ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 253 | 56 | 110 | 19425 | 2717522 | 277969 | 3.16 | 1973 | unknown | 1/5 | structural-owed |  |  | full |
| invisible-work.sh reads issues and PR documents larger than 256 KiB and gives the same output and exit code as for small ones, and no argument it hands python3 carries a JSON document ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 179 | 43 | 84 | 15782 | 1918103 | 254503 | 2.74 | 568 | unknown | 0/5 | nothing-left |  |  | full |
| wait-ci.sh reads check-run and status documents larger than 256 KiB and gives the same output and exit code as for small ones, and no argument it hands python3 carries a JSON document ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 177 | 43 | 82 | 15461 | 1915793 | 259261 | 2.77 | 809 | unknown | 0/5 | nothing-left |  |  | full |
| a suite fails naming <file>:<line> when a script under skills/tdd/scripts/ passes a variable holding a gh JSON document as an argument to python3, against an exemption table carrying a reason per entry ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 238 | 54 | 106 | 23435 | 2657300 | 280571 | 3.25 | 881 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| solvable-issues.sh prints the same numbers and exits 0 for a VERI_GH_JSON fixture whose issues.json is larger than 256 KiB as for the same issues with short bodies, and no argument it hands python3 carries the JSON document ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 64 | 0.77 |
| workqueue.sh reads an issues document larger than 256 KiB and gives the same output and exit code as for a small one, and no argument it hands python3 carries the JSON document ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 1589 | 1.18 |
| invisible-work.sh reads issues and PR documents larger than 256 KiB and gives the same output and exit code as for small ones, and no argument it hands python3 carries a JSON document ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 126 | 0.82 |
| wait-ci.sh reads check-run and status documents larger than 256 KiB and gives the same output and exit code as for small ones, and no argument it hands python3 carries a JSON document ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 161 | 0.80 |
| a suite fails naming <file>:<line> when a script under skills/tdd/scripts/ passes a variable holding a gh JSON document as an argument to python3, against an exemption table carrying a reason per entry ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 306 | 0.89 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 6 | 6 | 7 | 10 | 10 | 10 | 38 | 738 | 734 | 25 | 26 | 25 | 30 | 25 | 26 | 49 | 49 | 77 | 50 | 49 | 50 | 1 | 1 | 2 | 43 | 44 | 129 | 0 | 241 | 11 | 10 | 90 |
| fast | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 6 | 10 | 26 | 50 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 253 | 494 | 98112 | 11651120 | 1475537 | 16.10 |
