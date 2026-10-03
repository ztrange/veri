### 📊 Metrics — issue 726

Wall time for the issue: 7031 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/731.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 6 | 2 | 4 | 514 | 59728 | 38533 | 0.33 |
| red | 10 | 5 | 0 | 0 | 423 | 311 | 81 | 158 | 27559 | 3881829 | 456248 | 4.98 |
| green | 10 | 5 | 0 | 0 | 1295 | 392 | 101 | 196 | 33962 | 4760441 | 445689 | 5.20 |
| refactor | 10 | 5 | 0 | 0 | 967 | 221 | 66 | 128 | 21602 | 2935032 | 425606 | 4.42 |
| rebase | 2 | 1 | 0 | 0 | 1524 | 50 | 18 | 36 | 5107 | 871068 | 92139 | 1.01 |
| structural | 1 | 0 | 0 | 0 | 48 | 39 | 6 | 12 | 3081 | 261036 | 40033 | 0.43 |
| transform | 1 | 1 | 0 | 0 | 36 | 24 | 6 | 12 | 2462 | 257658 | 39538 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 18 | 18 | 0 | 0 | 2205 | 469 | 124 | 246 | 44192 | 5566194 | 760637 | 8.08 |
| developer | claude-opus-5-5 | 17 | 0 | 0 | 0 | 2099 | 574 | 156 | 300 | 50095 | 7460598 | 777149 | 8.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| event.sh refuses a structural-pass mark whose stopped= is not candidates-done, budget-spent or nothing-structural with exit 2, naming the value and the three allowed ones on stderr, and appends nothing to the event log ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 183 | 44 | 84 | 15168 | 1954981 | 257847 | 2.76 | 417 | unknown | 0/5 | nothing-left |  |  | full |
| event.sh refuses a structural-pass mark carrying no stopped= argument with exit 2, naming the three allowed reasons, and appends nothing to the event log ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 48 | 94 | 14582 | 2189263 | 252586 | 2.75 | 400 | unknown | 1/5 | structural-owed |  |  | full |
| event.sh refuses a structural-pass mark with stopped=budget-spent whose transforms is not equal to its budget with exit 2, and appends nothing to the event log ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 170 | 44 | 88 | 15668 | 2053816 | 260463 | 2.81 | 427 | unknown | 1/5 | nothing-structural |  |  | full |
| SKILL.md's structural-pass step says a missing .tdd/issue-<n>-refactor-owed.md is the refactor-owed.sh list exit-3 case, marked stopped=nothing-structural before the PR is readied ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 193 | 54 | 102 | 18941 | 2537574 | 283758 | 3.16 | 1095 | unknown | 1/5 | nothing-structural |  |  | full |
| metrics.sh on a log that reaches a draft PR (a done mark) but carries no structural-pass mark renders the #### Structural pass section with a row saying the pass was not marked ⟦criterion 4⟧ | 10 | 5 | 0 | 0 | 0 | 0 | 333 | 88 | 174 | 29414 | 4231430 | 444599 | 4.99 | 671 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| event.sh refuses a structural-pass mark whose stopped= is not candidates-done, budget-spent or nothing-structural with exit 2, naming the value and the three allowed ones on stderr, and appends nothing to the event log ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 82 | 0.78 |
| event.sh refuses a structural-pass mark carrying no stopped= argument with exit 2, naming the three allowed reasons, and appends nothing to the event log ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 95 | 0.86 |
| event.sh refuses a structural-pass mark with stopped=budget-spent whose transforms is not equal to its budget with exit 2, and appends nothing to the event log ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 100 | 0.87 |
| SKILL.md's structural-pass step says a missing .tdd/issue-<n>-refactor-owed.md is the refactor-owed.sh list exit-3 case, marked stopped=nothing-structural before the PR is readied ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 524 | 0.97 |
| metrics.sh on a log that reaches a draft PR (a done mark) but carries no structural-pass mark renders the #### Structural pass section with a row saying the pass was not marked ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 166 | 0.94 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 15 | 1 | 0 | 4 | 4 | 3 | 3 | 3 | 3 | 18 | 3 | 3 | 4 | 0 | 1 | 0 | 1 | 201 | 0 | 78 | 209 | 0 | 217 | 15 | 15 | 16 | 0 | 36 | 15 | 14 | 14 | 4 | 3 | 3 |
| fast | 28 | 30 | 30 | 31 | 29 | 30 | 28 | 28 | 29 | 26 | 29 | 32 | 29 | 33 | 34 | 29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 3 | 4 | 1 | 1 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 722 | 739 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 280 | 546 | 94287 | 13026792 | 1537786 | 16.80 |
