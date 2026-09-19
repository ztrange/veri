### 📊 Metrics — issue 329

Wall time for the issue: 4266 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/345.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 13 | 3 | 0 | 0 | 551 | 475 | 68 | 134 | 48863 | 2827145 | 540459 | 8.04 |
| green | 6 | 3 | 0 | 0 | 1419 | 143 | 34 | 68 | 13964 | 1405885 | 229824 | 3.35 |
| refactor | 6 | 3 | 0 | 0 | 729 | 194 | 45 | 90 | 19736 | 2133602 | 262564 | 4.19 |
| pin | 7 | 7 | 0 | 0 | 475 | 146 | 40 | 78 | 14010 | 1533107 | 259968 | 3.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Given a fixture suite whose trace carries fabricated EPOCHREALTIME timestamps for two cases, one above and one below VERI_PROFILE_THRESHOLD, only the case at or above it is printed ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 194 | 34 | 68 | 19688 | 1434852 | 236584 | 3.58 | 1078 | unknown | 0/5 | nothing-left |
| The printed line for a fixture case matches `<secs> <suite> case <n> L<a>-<b>` exactly, with n and the line range matching the fixture's own case number and source lines ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 10 | 20 | 5854 | 390910 | 75613 | 1.10 | unknown | unknown | unknown | unknown |
| A case boundary is a top-level pass=/fail= assignment whose value exceeds the counter's previous value, and no other assignment (a top-level pass=0 plus a local passed=1 inside a case is not two boundaries) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 76 | 10 | 20 | 7965 | 394721 | 78524 | 1.18 | unknown | unknown | unknown | unknown |
| Cases at or above the threshold are printed slowest first, proven with three fixture cases of distinct fabricated durations ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 9 | 16 | 4125 | 295187 | 73939 | 0.99 | unknown | unknown | unknown | unknown |
| Setting VERI_PROFILE_THRESHOLD to a different value changes which fixture cases are printed, against the same injected timestamps ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 8 | 16 | 3918 | 295071 | 72974 | 0.98 | unknown | unknown | unknown | unknown |
| A non-numeric VERI_PROFILE_THRESHOLD, and a suite whose trace never shows a pass=/fail= increment, both exit 2 ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 173 | 42 | 82 | 17438 | 1832890 | 233599 | 3.69 | 758 | unknown | 5/5 | structural-owed |
| With VERI_PROFILE_THRESHOLD unset the threshold is 1 second, and a run in which no case reaches the threshold still exits 0 | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 11 | 22 | 6582 | 450386 | 81619 | 1.21 | unknown | unknown | unknown | unknown |
| make -n profile runs every suite make -n test runs, over the same TESTS glob and the same offline/PATH environment test's recipe sets up ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 165 | 35 | 70 | 16730 | 1585479 | 271655 | 3.93 | 742 | unknown | 1/5 | structural-owed |
| make -n test does not invoke profile and profile does not invoke test — they are independent targets ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 15 | 30 | 5971 | 663225 | 86598 | 1.35 | unknown | unknown | unknown | unknown |
| profile.test.sh requests no real sleep and runs no real suite from skills/tdd/scripts/tests/ — only its own fixture suites — and is covered by make test's own glob ⟦criterion 9⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 13 | 26 | 8302 | 557018 | 81710 | 1.30 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 187 | 370 | 96573 | 7899739 | 1292815 | 19.29 |
