### 📊 Metrics — issue 452

Wall time for the issue: 3468 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/517.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 18 | 3 | 6 | 1732 | 105061 | 38630 | 0.36 |
| red | 13 | 5 | 0 | 0 | 608 | 501 | 122 | 234 | 47578 | 5989824 | 627655 | 7.17 |
| green | 10 | 5 | 0 | 0 | 1251 | 359 | 97 | 188 | 34355 | 4401273 | 437915 | 5.07 |
| refactor | 10 | 5 | 0 | 0 | 686 | 348 | 86 | 172 | 34223 | 4123058 | 434725 | 4.99 |
| pin | 3 | 3 | 0 | 0 | 85 | 63 | 15 | 28 | 6441 | 564819 | 119667 | 1.20 |

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
| SKILL.md's step cost check writes one `step-over-budget` event carrying `spent=` and `budget=` at the crossing, before the over-budget leaf is launched ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 208 | 56 | 108 | 20633 | 2615427 | 270795 | 3.10 | 631 | unknown | 1/5 | nothing-structural |
| SKILL.md writes that `step-over-budget` event on every crossing, so a crossing that goes on to split, one that goes on to park and one that goes on to continue each carry it ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 90 | 18 | 32 | 9180 | 838846 | 97291 | 1.13 | unknown | unknown | unknown | unknown |
| SKILL.md's over-budget exit 0 branch writes `step-split` carrying `at=over-budget`, while the revise-exhausted split keeps its `at=exhausted` spelling unchanged ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 202 | 49 | 98 | 19768 | 2328672 | 265796 | 2.99 | 628 | unknown | 2/5 | malformed |
| SKILL.md's over-budget exit 1 branch writes `step-escalated` carrying `at=over-budget` ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 199 | 51 | 100 | 19657 | 2407324 | 271700 | 3.05 | 518 | unknown | 2/5 | nothing-structural |
| SKILL.md's over-budget exit 3 branch writes no event mark beyond the crossing's `step-over-budget` ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 17 | 34 | 6891 | 894539 | 99340 | 1.11 | unknown | unknown | unknown | unknown |
| metrics.sh's `#### By step` table reports, for a step whose log holds `step-over-budget`, the `spent=` figure it carried, and leaves that column empty for a step that did not cross ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 219 | 60 | 118 | 21697 | 2918185 | 278132 | 3.24 | 433 | unknown | 1/5 | nothing-structural |
| metrics.sh's report distinguishes a log holding `step-split` with `at=over-budget` from one holding `step-split` with `at=exhausted` ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 224 | 55 | 104 | 19651 | 2459924 | 257829 | 2.95 | 443 | unknown | 1/5 | nothing-structural |
| classify-bail.sh refuses `step-over-budget` and `over-budget` as bail causes, knowing none of the new words ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 14 | 28 | 5120 | 616057 | 79079 | 0.86 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 84 | 0 | 105 | 105 | 0 | 1 | 1 | 0 | 1 | 104 | 0 | 105 | 1 | 1 | 0 | 104 | 0 | 1 | 1 | 1 | 0 | 104 | 0 | 105 | 1 | 1 | 1 | 1 | 0 | 1 | 4 | 5 | 4 | 5 | 4 | 4 | 5 | 5 | 0 | 62 | 5 | 0 | 5 | 4 | 4 | 1 |
| fast | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 5 | 4 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 323 | 628 | 124329 | 15184035 | 1658592 | 18.79 |
