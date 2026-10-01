### 📊 Metrics — issue 504

Wall time for the issue: 9222 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/613.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 25 | 20 | 3 | 6 | 2130 | 104851 | 39694 | 0.38 |
| red | 14 | 6 | 0 | 0 | 588 | 493 | 109 | 210 | 45651 | 5150216 | 639148 | 7.06 |
| green | 18 | 6 | 3 | 0 | 5329 | 624 | 164 | 322 | 59841 | 7657215 | 682605 | 8.19 |
| refactor | 12 | 6 | 0 | 0 | 821 | 323 | 82 | 164 | 27846 | 3680088 | 501630 | 5.31 |
| pin | 2 | 2 | 0 | 0 | 61 | 46 | 11 | 22 | 4362 | 458199 | 79779 | 0.82 |
| structural | 2 | 0 | 0 | 0 | 33 | 21 | 6 | 12 | 1820 | 208827 | 71005 | 0.65 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 5010 | 5.85 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| refactor-owed.sh list prints each recorded structural candidate once, most valuable first: a candidate recorded under more steps before one recorded under fewer, ties kept in the order they were recorded ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 168 | 46 | 90 | 15471 | 2103811 | 256171 | 2.78 | 343 | unknown | 1/5 | nothing-structural |  |  | full |
| SKILL.md's structural pass takes the candidates in the order `refactor-owed.sh list` prints them and names that order as most valuable first ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 48 | 92 | 14496 | 2091480 | 254181 | 2.74 | 632 | unknown | 0/5 | structural-owed |  |  | full |
| refactor-overflow.sh <n> <owed-file> <reached> files one issue whose title and body name the parent issue #<n> and whose body lists every candidate `refactor-owed.sh list` prints after the first <reached>, prints the new issue's URL and exits 0 ⟦criterion 2⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 354 | 83 | 164 | 33693 | 3982184 | 380042 | 4.51 | 3135 | 2/2 | 1/5 | nothing-structural |  |  | full |
| refactor-overflow.sh files nothing — no `gh` call — and exits 3 with empty stdout when the owed file is missing or holds no candidate, or when <reached> covers every candidate; it exits 2 on a missing or non-numeric argument ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 286 | 63 | 126 | 26925 | 2945069 | 307465 | 3.59 | 1273 | 1/2 | 1/5 | nothing-structural |  |  | full |
| refactor-overflow.sh sends no label with the issue it files, makes no call that labels or edits the parent issue, and writes no file into the repository ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 14 | 28 | 6847 | 629221 | 83973 | 0.93 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's structural pass, when it ends with `stopped=budget-spent`, runs refactor-overflow.sh with the number of candidates it took up and puts the filed issue's URL in the PR body; when it ends with `candidates-done` or `nothing-structural` it files nothing ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 205 | 48 | 96 | 18994 | 2384582 | 276588 | 3.07 | 921 | unknown | 1/5 | nothing-structural |  |  | full |
| SKILL.md's Draft PR body still carries `refactor-owed.sh render`'s `## Refactor owed` section after the structural pass has run ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 15 | 30 | 6212 | 729043 | 88499 | 0.98 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md states that the overflow filing applies no label to the parent issue and commits no standing debt file to the repository ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 173 | 49 | 92 | 15062 | 2080328 | 256243 | 2.77 | 649 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| refactor-owed.sh list prints each recorded structural candidate once, most valuable first: a candidate recorded under more steps before one recorded under fewer, ties kept in the order they were recorded ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 89 | 0.91 |
| SKILL.md's structural pass takes the candidates in the order `refactor-owed.sh list` prints them and names that order as most valuable first ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 127 | 0.82 |
| refactor-overflow.sh <n> <owed-file> <reached> files one issue whose title and body name the parent issue #<n> and whose body lists every candidate `refactor-owed.sh list` prints after the first <reached>, prints the new issue's URL and exits 0 ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 83 | 0.87 |
| refactor-overflow.sh files nothing — no `gh` call — and exits 3 with empty stdout when the owed file is missing or holds no candidate, or when <reached> covers every candidate; it exits 2 on a missing or non-numeric argument ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 107 | 0.94 |
| SKILL.md's structural pass, when it ends with `stopped=budget-spent`, runs refactor-overflow.sh with the number of candidates it took up and puts the filed issue's URL in the PR body; when it ends with `candidates-done` or `nothing-structural` it files nothing ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 209 | 0.88 |
| SKILL.md states that the overflow filing applies no label to the parent issue and commits no standing debt file to the repository ⟦criterion 5⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 206 | 0.89 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 27 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 126 | 141 | 0 | 63 | 0 | 0 | 2 | 2 | 66 | 0 | 259 | 251 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 128 | 338 | 0 | 13 | 1 | 1 | 1 | 2 | 1 | 47 | 1 | 1 | 0 | 0 | 1 | 0 | 3 | 1 | 0 | 31 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 5 | 6 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 3 | 1 | 0 | 0 | 9 | 1 | 0 | 1 | 0 | 107 | 129 | 0 | 131 | 1 |
| fast | 14 | 14 | 13 | 14 | 13 | 14 | 13 | 13 | 13 | 14 | 13 | 12 | 14 | 13 | 12 | 11 | 11 | 11 | 12 | 12 | 12 | 11 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 868 | 870 | 812 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 375 | 736 | 141650 | 17259396 | 2013861 | 22.40 |
