### 📊 Metrics — issue 112

Wall time for the issue: 8062 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/442.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 42 | 39 | 7 | 10 | 3419 | 211490 | 43625 | 0.63 |
| red | 13 | 6 | 0 | 0 | 1525 | 1295 | 202 | 350 | 93807 | 10486455 | 731661 | 14.91 |
| green | 16 | 6 | 2 | 0 | 3195 | 1361 | 253 | 448 | 102474 | 12115721 | 817415 | 16.80 |
| refactor | 12 | 6 | 0 | 0 | 2334 | 1366 | 193 | 354 | 102863 | 9951119 | 646704 | 14.02 |
| pin | 1 | 1 | 0 | 0 | 46 | 37 | 15 | 22 | 3371 | 526921 | 43149 | 0.78 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1766 | 7.37 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| capture-spec.sh writes the blind spec with a Bug section carrying what happened, expected, steps to reproduce and environment when the issue carries the bug label ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 747 | 120 | 204 | 54131 | 5567051 | 414310 | 8.28 | unknown | 1/2 | 1/5 | structural-owed |
| capture-spec.sh writes a spec with no Bug section when the issue does not carry the bug label ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 604 | 71 | 124 | 44324 | 3151542 | 290748 | 5.59 | 860 | unknown | 3/5 | structural-owed |
| SKILL.md captures the blind spec through capture-spec.sh rather than a bare gh issue view ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 632 | 109 | 194 | 49241 | 5703038 | 349665 | 7.58 | 1358 | unknown | 2/5 | structural-owed |
| build-develop-prompt.sh red emits its reproduction paragraph only when the spec has a Bug section, with its parameters unchanged ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 674 | 112 | 190 | 52720 | 5674796 | 343538 | 7.59 | 1066 | unknown | 3/5 | nothing-structural |
| build-verify-prompt.sh red emits its reproduction paragraph, requiring the observed failure to match what happened, only when the spec has a Bug section, with its four parameters unchanged ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 559 | 95 | 172 | 43463 | 4900409 | 331416 | 6.85 | 704 | unknown | 1/5 | structural-owed |
| the develop-red reproduction paragraph tells the leaf to name the bug test so it carries the issue number ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 153 | 41 | 74 | 12065 | 2188579 | 109868 | 2.49 | unknown | unknown | unknown | unknown |
| SKILL.md gives a bug step's green commit a fix: subject and a bug run's PR title a fix: prefix ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 690 | 115 | 216 | 46571 | 5894801 | 399384 | 8.11 | 1683 | 1/2 | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 88 | 101 | 69 | 0 | 62 | 62 | 62 | 0 | 0 | 1 | 0 | 62 | 0 | 1 | 0 | 0 | 0 | 29 | 0 | 0 | 0 | 0 | 0 | 74 | 124 | 0 | 76 | 0 | 76 | 2 | 1 | 10 | 46 | 47 | 47 | 46 | 5 | 2 | 3 | 2 | 3 | 2 | 4 | 4 | 4 | 2 | 0 | 0 | 76 | 0 | 130 | 125 | 1 | 126 | 0 |
| fast | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 1 | 2 | 3 | 2 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 274 | 274 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 670 | 1184 | 305934 | 33291706 | 2282554 | 47.13 |
