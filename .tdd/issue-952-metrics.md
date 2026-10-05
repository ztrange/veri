### 📊 Metrics — issue 952

Wall time for the issue: 2120 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 14 | 2 | 4 | 1317 | 53175 | 35917 | 0.17 |
| red | 5 | 2 | 0 | 0 | 177 | 159 | 45 | 90 | 16054 | 2252815 | 230708 | 2.27 |
| green | 4 | 2 | 0 | 0 | 488 | 120 | 36 | 66 | 11232 | 1507022 | 164835 | 1.50 |
| refactor | 4 | 2 | 0 | 0 | 99 | 60 | 19 | 34 | 5371 | 664284 | 156930 | 1.18 |
| pin | 1 | 1 | 0 | 0 | 69 | 66 | 5 | 10 | 1342 | 195361 | 37163 | 0.20 |
| predicate | 1 | 0 | 0 | 0 | 16 | 14 | 4 | 8 | 788 | 145079 | 34219 | 0.32 |
| structural | 1 | 0 | 0 | 0 | 24 | 20 | 6 | 12 | 1623 | 240172 | 35495 | 0.36 |
| transform | 1 | 1 | 0 | 0 | 31 | 12 | 5 | 10 | 1436 | 190248 | 35597 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 464 | 174 | 43 | 82 | 13587 | 1579639 | 337528 | 1.80 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 456 | 291 | 79 | 152 | 25576 | 3668517 | 393336 | 4.39 |

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
| `refactor-owed.sh applied <file> '<candidate>' <sha>` records that the structural pass applied a candidate, after which `refactor-owed.sh render <file>` no longer lists that candidate as owed under any step and instead lists it as applied, naming <sha> ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 157 | 46 | 88 | 15188 | 2004806 | 243979 | 2.16 | 312 | unknown | 1/5 | structural-owed |  |  | full |
| `refactor-owed.sh render <file>` still lists as owed, as today, a structural candidate no `applied` call named, in the same file as one that was recorded applied ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 108 | 16 | 32 | 5742 | 789569 | 88404 | 0.82 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's Draft PR structural pass runs `refactor-owed.sh applied` on the run's owed file with the candidate and the commit after each `transform` verifier PASS, before the PR body is rendered ⟦criterion 1⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 186 | 58 | 110 | 16916 | 2400606 | 362564 | 3.05 | 544 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `refactor-owed.sh applied <file> '<candidate>' <sha>` records that the structural pass applied a candidate, after which `refactor-owed.sh render <file>` no longer lists that candidate as owed under any step and instead lists it as applied, naming <sha> ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 64 | 0.63 |
| SKILL.md's Draft PR structural pass runs `refactor-owed.sh applied` on the run's owed file with the candidate and the commit after each `transform` verifier PASS, before the PR body is rendered ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.55 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 89 | 1 | 0 |
| fast | 15 | 14 | 16 | 15 | 15 | 14 | 15 |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 122 | 234 | 39163 | 5248156 | 730864 | 6.19 |
