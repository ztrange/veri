### 📊 Metrics — issue 111

Wall time for the issue: 4744 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/440.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 11 | 5 | 0 | 0 | 1065 | 833 | 138 | 240 | 64333 | 6290033 | 554408 | 10.30 |
| green | 10 | 5 | 0 | 0 | 1674 | 717 | 151 | 284 | 52705 | 7313103 | 480555 | 9.78 |
| refactor | 10 | 5 | 0 | 0 | 1185 | 762 | 113 | 218 | 53754 | 5567035 | 476937 | 8.90 |
| pin | 1 | 1 | 0 | 0 | 60 | 45 | 12 | 22 | 3665 | 553699 | 46166 | 0.83 |

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
| skills/tdd-fix/SKILL.md exists as the /tdd-fix skill, taking an optional one-line description and asking only for what that line left out, in one short round ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 487 | 80 | 154 | 35974 | 4123565 | 301088 | 5.97 | 1101 | unknown | 1/5 | structural-owed |
| The issue body it files carries exactly the six headings the conductor reads — What happened, Expected, Steps to reproduce, Environment, Acceptance criteria, and Blocked by holding None ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 427 | 76 | 138 | 34245 | 3488466 | 286190 | 5.46 | 559 | unknown | 2/5 | structural-owed |
| Each acceptance criterion it writes is one per manifestation, in the reproduction-fails-now-and-passes-after-the-fix shape ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 134 | 27 | 52 | 11075 | 1326855 | 96603 | 1.91 | 186 | unknown | unknown | unknown |
| The issue is labelled bug and the opt-in label, ready-for-agent by default or ready-for-agent with a scope suffix when the user names one, creating the bug label when the repo lacks it ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 478 | 74 | 130 | 32873 | 3353233 | 286147 | 5.36 | 671 | unknown | 2/5 | nothing-structural |
| The skill asks one question before starting the fix run, and invokes /tdd only on yes ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 430 | 82 | 146 | 31736 | 3802232 | 297640 | 5.67 | 560 | unknown | 2/5 | structural-owed |
| The README documents /tdd-fix beside /tdd, and the skill ships no scripts ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 401 | 75 | 144 | 28554 | 3629519 | 290398 | 5.43 | 1356 | unknown | 0/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 64 | 65 | 10 | 16 | 65 | 65 | 66 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 68 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 1 | 274 | 284 | 275 |
| fast | 2 | 2 | 2 | 3 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 414 | 764 | 174457 | 19723870 | 1558066 | 29.81 |
