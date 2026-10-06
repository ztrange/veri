### 📊 Metrics — issue 1030

Wall time for the issue: 1442 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1043.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 780 | 10227 | 31729 | 0.14 |
| red | 4 | 2 | 0 | 0 | 129 | 113 | 25 | 48 | 9653 | 1095708 | 174884 | 1.47 |
| green | 4 | 2 | 0 | 0 | 283 | 111 | 29 | 56 | 9851 | 1243965 | 160170 | 1.39 |
| refactor | 4 | 2 | 0 | 0 | 98 | 53 | 17 | 34 | 4660 | 661838 | 157937 | 1.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 222 | 91 | 31 | 62 | 9772 | 1213976 | 263555 | 1.39 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 296 | 192 | 41 | 78 | 15172 | 1797762 | 261165 | 2.75 |

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
| Run from a directory that is not inside a git work tree, preserve-attempt.sh <issue> <step> <phase> <attempt> exits 2 (the existing case pinning exit 1 there changes to 2) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 105 | 32 | 62 | 10235 | 1289004 | 241367 | 1.88 | 259 | unknown | 0/5 | nothing-left |  |  | full |
| Outside a git work tree, preserve-attempt.sh prints exactly one stderr line, naming preserve-attempt.sh and saying it is not in a git work tree (git's own fatal line suppressed), creates no scratch directory and runs no git add ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 172 | 39 | 76 | 13929 | 1712507 | 251624 | 2.13 | 415 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Run from a directory that is not inside a git work tree, preserve-attempt.sh <issue> <step> <phase> <attempt> exits 2 (the existing case pinning exit 1 there changes to 2) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.57 |
| Outside a git work tree, preserve-attempt.sh prints exactly one stderr line, naming preserve-attempt.sh and saying it is not in a git work tree (git's own fatal line suppressed), creates no scratch directory and runs no git add ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 46 | 0.58 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 40 | 0 | 2 |
| fast | 15 | 15 | 15 | 15 | 16 | 15 | 15 | 16 |  |  |  |  |
| target | 0 | 2 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 72 | 140 | 24944 | 3011738 | 524720 | 4.15 |
