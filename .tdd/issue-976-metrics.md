### 📊 Metrics — issue 976

Wall time for the issue: 1834 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1157.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 722 | 10366 | 32606 | 0.14 |
| red | 2 | 1 | 0 | 0 | 58 | 52 | 16 | 30 | 5754 | 722178 | 91700 | 0.82 |
| green | 2 | 1 | 0 | 0 | 486 | 63 | 18 | 34 | 6828 | 800627 | 88160 | 0.81 |
| refactor | 2 | 1 | 0 | 0 | 486 | 54 | 17 | 34 | 5596 | 824729 | 91860 | 0.82 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 510 | 61 | 22 | 42 | 7106 | 885828 | 155484 | 0.87 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 528 | 113 | 30 | 58 | 11794 | 1472072 | 148842 | 1.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| SKILL.md states that a ⟦diff-checked⟧ step's step base sha, on a fresh run and on a resume alike, is the last commit that changed the ledger (git log -1 --format=%H -- .tdd/issue-<n>.md), never a HEAD taken after a killed attempt's commit — pinned by a text case in a skill-*.test.sh suite that goes red against today's text ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 169 | 51 | 98 | 18178 | 2347534 | 271720 | 2.45 | 1130 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md states that a ⟦diff-checked⟧ step's step base sha, on a fresh run and on a resume alike, is the last commit that changed the ledger (git log -1 --format=%H -- .tdd/issue-<n>.md), never a HEAD taken after a killed attempt's commit — pinned by a text case in a skill-*.test.sh suite that goes red against today's text ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 486 | 0.82 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 116 | 133 | 0 | 138 | 133 | 0 | 4 | 1 | 0 | 1 | 0 | 1 | 0 | 72 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | 1 | 24 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 13 | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 4 | 0 |
| fast | 18 | 18 | 18 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 52 | 100 | 18900 | 2357900 | 304326 | 2.59 |
