### 📊 Metrics — issue 501

Wall time for the issue: 4224 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/522.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 15 | 1 | 2 | 912 | 11207 | 31885 | 0.28 |
| red | 16 | 8 | 0 | 0 | 564 | 472 | 112 | 214 | 43960 | 4816325 | 681506 | 7.30 |
| green | 20 | 8 | 2 | 0 | 1996 | 617 | 153 | 300 | 56427 | 6618459 | 770573 | 8.62 |
| refactor | 15 | 7 | 0 | 0 | 558 | 362 | 92 | 182 | 33641 | 3909344 | 607339 | 6.31 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1364 | 3.36 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A new veri skill ships as its own directory under skills/ whose SKILL.md frontmatter name matches the directory, and it says it shapes and files candidates without surveying, ranking or judging them | 8 | 3 | 1 | 0 | 0 | 0 | 230 | 53 | 102 | 20249 | 2238664 | 331343 | 3.50 | 1063 | 1/2 | 0/5 | structural-owed |
| Given architecture-analysis candidates taken from the conversation, the skill files one GitHub issue per module (not one per smell), each with acceptance criteria phrased as structural predicates carrying a runnable check where one exists ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 163 | 40 | 78 | 15530 | 1707906 | 244317 | 2.61 | 455 | unknown | 1/5 | structural-owed |
| Given the path to the analysis's HTML report instead of conversation candidates, the skill reads the candidates from that file and files the same issues it would have filed from the conversation ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 151 | 37 | 74 | 13709 | 1618885 | 244423 | 2.55 | 277 | unknown | 1/5 | nothing-left |
| Every issue the skill files ends its body with a final `Test command:` line and lists under `## Blocked by` only real blockers ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 39 | 76 | 12967 | 1623198 | 244231 | 2.54 | 259 | unknown | 0/5 | nothing-left |
| A candidate with no checkable predicate is not filed, and the skill says which candidate was skipped and why ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 168 | 47 | 90 | 16283 | 1994453 | 243214 | 2.67 | 294 | unknown | 1/5 | nothing-structural |
| Re-running the skill over candidates it already filed files no duplicate issue for them ⟦criterion 5⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 344 | 77 | 152 | 31103 | 3378092 | 457339 | 4.96 | 559 | unknown | 2/5 | nothing-left |
| The lookup for an already-filed issue finds its marker however many issues the repository holds, so a repository with more than 1,000 issues still files no duplicate ⟦added⟧ ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 254 | 64 | 124 | 24187 | 2782930 | 294551 | 3.40 | 845 | 1/2 | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 61 | 0 | 82 | 0 | 81 | 0 | 0 | 0 | 81 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 |
| fast | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 434 | 433 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 358 | 698 | 134940 | 15355335 | 2091303 | 22.50 |
