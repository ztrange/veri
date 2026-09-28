### 📊 Metrics — issue 503

Wall time for the issue: 7942 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/530.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 14 | 2 | 4 | 1468 | 57163 | 36218 | 0.33 |
| red | 24 | 12 | 0 | 0 | 997 | 817 | 193 | 378 | 79747 | 9393975 | 1104124 | 12.31 |
| green | 30 | 12 | 3 | 0 | 4629 | 1069 | 294 | 576 | 106615 | 13831128 | 1252297 | 14.92 |
| refactor | 24 | 12 | 0 | 0 | 1143 | 498 | 142 | 284 | 49598 | 6145241 | 981872 | 10.08 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2014 | 4.84 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| build-develop-prompt.sh refactor prints a prompt telling the per-step leaf to apply only duplication removal against code this cycle wrote, and to apply no other structural transform (extract a module, move behaviour, rename across files) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 174 | 50 | 96 | 17425 | 2244298 | 255469 | 2.84 | 320 | unknown | 0/5 | nothing-structural |  |  | full |
| The per-step refactor prompt tells the leaf to report every other structural candidate it sees as a `CANDIDATES: structural | …` line rather than apply it, and refactor-owed.sh append records such a line under the step's name ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 187 | 49 | 96 | 17929 | 2311444 | 264088 | 2.93 | 312 | unknown | 0/5 | structural-owed |  |  | full |
| refactor-touched.sh given a base sha and `--issue` prints, comma-joined, every file changed between that base and HEAD outside `.tdd/`, exits 3 with empty stdout when there is none, and exits 2 when the base does not resolve ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 209 | 50 | 98 | 20663 | 2165989 | 289330 | 3.16 | 835 | 1/2 | 1/5 | nothing-structural |  |  | full |
| refactor-owed.sh list prints every recorded structural candidate of the run one per line, without the step headings, and exits 3 with empty stdout when the owed file is missing or holds none ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 174 | 42 | 84 | 16837 | 1900367 | 252513 | 2.74 | 279 | unknown | 1/5 | structural-owed |  |  | full |
| refactor-budget.sh --issue bounds the structural pass by its own budget, VERI_ISSUE_REFACTOR_BUDGET (default 10), exiting 0 under it, 3 once spent and 2 on a value that is not a whole number ≥ 0, while refactor-budget.sh without the flag still reads VERI_REFACTOR_BUDGET ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 223 | 56 | 112 | 22905 | 2594343 | 307296 | 3.44 | 825 | 1/2 | 0/5 | structural-owed |  |  | full |
| build-develop-prompt.sh accepts a `structural` phase that builds a transform prompt for one recorded structural candidate, naming the issue's touched files as its bounds, telling the leaf to commit that one transform as its own `refactor:` commit and to touch no test file ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 185 | 49 | 98 | 17742 | 2363182 | 273102 | 3.01 | 334 | unknown | 0/5 | structural-owed |  |  | full |
| SKILL.md runs one structural pass after `next-unchecked.sh` exits 3 and before the PR is marked ready: one `structural` transform leaf per candidate `refactor-owed.sh list` prints, bounded to the files `refactor-touched.sh --issue` prints, counted against `refactor-budget.sh --issue` ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 229 | 58 | 116 | 22719 | 2912219 | 283504 | 3.31 | 1150 | unknown | 0/5 | nothing-structural |  |  | full |
| SKILL.md's structural pass checks each transform leaf's commits with transform-touches-tests.sh and has the blind `transform` verifier judge them against that transform's base sha, one commit per transform, before the next candidate ⟦criterion 4⟧ | 12 | 6 | 0 | 0 | 0 | 0 | 365 | 102 | 202 | 36548 | 4731053 | 518238 | 5.82 | 1060 | unknown | 1/4 | structural-owed |  |  | full |
| SKILL.md skips the structural pass when `refactor-owed.sh list` exits 3, writing a `structural-pass` mark with `stopped=nothing-structural` and no bail mark, and going straight on to readying the PR ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 183 | 49 | 94 | 17760 | 2176209 | 261530 | 2.88 | 633 | unknown | 1/5 | nothing-left |  |  | full |
| metrics.sh renders the `structural-pass` mark (transforms, budget, stopped) as its own section of the `### 📊 Metrics` block, separate from the per-step refactor cells, and a log with no such mark renders no such section ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 254 | 69 | 136 | 24668 | 3396879 | 357918 | 4.04 | 994 | 1/2 | 1/5 | nothing-left |  |  | full |
| SKILL.md writes one `structural-pass` mark carrying transforms, budget and stopped once the pass ends, and preflight refuses an unreadable VERI_ISSUE_REFACTOR_BUDGET the way it refuses VERI_REFACTOR_BUDGET ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 201 | 55 | 106 | 20764 | 2574361 | 275305 | 3.13 | 644 | unknown | 0/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| build-develop-prompt.sh refactor prints a prompt telling the per-step leaf to apply only duplication removal against code this cycle wrote, and to apply no other structural transform (extract a module, move behaviour, rename across files) ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 39 | 0.69 |
| The per-step refactor prompt tells the leaf to report every other structural candidate it sees as a `CANDIDATES: structural | …` line rather than apply it, and refactor-owed.sh append records such a line under the step's name ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 47 | 0.79 |
| refactor-touched.sh given a base sha and `--issue` prints, comma-joined, every file changed between that base and HEAD outside `.tdd/`, exits 3 with empty stdout when there is none, and exits 2 when the base does not resolve ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 66 | 0.83 |
| refactor-owed.sh list prints every recorded structural candidate of the run one per line, without the step headings, and exits 3 with empty stdout when the owed file is missing or holds none ⟦criterion 5⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 84 | 0.95 |
| refactor-budget.sh --issue bounds the structural pass by its own budget, VERI_ISSUE_REFACTOR_BUDGET (default 10), exiting 0 under it, 3 once spent and 2 on a value that is not a whole number ≥ 0, while refactor-budget.sh without the flag still reads VERI_REFACTOR_BUDGET ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 61 | 0.87 |
| build-develop-prompt.sh accepts a `structural` phase that builds a transform prompt for one recorded structural candidate, naming the issue's touched files as its bounds, telling the leaf to commit that one transform as its own `refactor:` commit and to touch no test file ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 53 | 0.83 |
| SKILL.md runs one structural pass after `next-unchecked.sh` exits 3 and before the PR is marked ready: one `structural` transform leaf per candidate `refactor-owed.sh list` prints, bounded to the files `refactor-touched.sh --issue` prints, counted against `refactor-budget.sh --issue` ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 246 | 0.87 |
| SKILL.md's structural pass checks each transform leaf's commits with transform-touches-tests.sh and has the blind `transform` verifier judge them against that transform's base sha, one commit per transform, before the next candidate ⟦criterion 4⟧ | 1 | 1/5 | overfit | PASS | 0 | 68 | 0.90 |
| SKILL.md's structural pass checks each transform leaf's commits with transform-touches-tests.sh and has the blind `transform` verifier judge them against that transform's base sha, one commit per transform, before the next candidate ⟦criterion 4⟧ | 2 | 1/4 | structural-owed | PASS | 0 | 54 | 0.79 |
| SKILL.md skips the structural pass when `refactor-owed.sh list` exits 3, writing a `structural-pass` mark with `stopped=nothing-structural` and no bail mark, and going straight on to readying the PR ⟦criterion 5⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 175 | 0.85 |
| metrics.sh renders the `structural-pass` mark (transforms, budget, stopped) as its own section of the `### 📊 Metrics` block, separate from the per-step refactor cells, and a log with no such mark renders no such section ⟦criterion 6⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 81 | 0.86 |
| SKILL.md writes one `structural-pass` mark carrying transforms, budget and stopped once the pass ends, and preflight refuses an unreadable VERI_ISSUE_REFACTOR_BUDGET the way it refuses VERI_REFACTOR_BUDGET ⟦criterion 6⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 169 | 0.84 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 4 | 0 | 0 | 0 | 3 | 1 | 1 | 4 | 0 | 3 | 2 | 4 | 5 | 3 | 1 | 1 | 1 | 6 | 2 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 3 | 3 | 3 | 0 | 36 | 3 | 0 | 1 | 119 | 190 | 0 | 191 | 0 | 190 | 0 | 1 | 0 | 92 | 0 | 114 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 93 | 0 | 192 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 119 | 0 | 115 | 0 | 11 | 0 | 0 | 1 | 2 | 1 | 40 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 29 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 4 | 6 | 1 | 0 | 1 | 1 | 0 | 2 | 0 | 1 | 0 | 1 | 0 | 4 | 1 | 7 | 7 | 7 | 24 | 8 | 7 | 8 | 7 | 0 | 1 | 0 | 0 | 112 | 0 | 113 | 1 | 116 |
| fast | 3 | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 2 | 1 | 1 | 1 | 1 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 7 | 8 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 479 | 478 | 474 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 631 | 1242 | 237428 | 29427507 | 3374511 | 37.64 |
