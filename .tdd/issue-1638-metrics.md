### 📊 Metrics — issue 1638

Wall time for the issue: 3246 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1790.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 18 | 7 | 14 | 2015 | 197180 | 35592 | 0.13 |
| red | 6 | 3 | 0 | 0 | 301 | 101 | 34 | 66 | 12944 | 1023368 | 137434 | 0.58 |
| green | 7 | 3 | 0 | 0 | 964 | 129 | 44 | 86 | 12895 | 1292158 | 160059 | 0.83 |
| refactor | 6 | 3 | 0 | 0 | 237 | 49 | 23 | 44 | 4728 | 579041 | 101520 | 0.36 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 711 | 111 | 41 | 80 | 11098 | 1060760 | 184976 | 0.68 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 632 | 122 | 48 | 94 | 15581 | 1439019 | 187073 | 0.77 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 181 | 64 | 19 | 36 | 5903 | 591968 | 62556 | 0.45 |

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
| When rebase_onto_default.py cannot re-apply a set-aside-tdd-appends.diff a killed run left, its exit-2 stop names that set-aside file and every kept-tdd-appends.diff* file on disk, pinned by a case with both kinds of file present ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 62 | 28 | 54 | 7399 | 751815 | 114110 | 0.43 | 408 | unknown | 1/5 | nothing-left |  |  | full |
| When rebase_onto_default.py cannot re-apply the uncommitted .tdd/ appends after its rebase, its exit-2 stop names the set-aside-tdd-appends.diff it left on disk as well as every kept-tdd-appends.diff* file, pinned by a case with both kinds of file present ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 138 | 43 | 84 | 13962 | 1312227 | 149443 | 0.82 | 578 | 1/2 | 1/5 | nothing-left |  |  | full |
| When SKILL.md's resume discard cannot re-apply the uncommitted .tdd/ appends, its exit-2 stop names a set-aside-tdd-appends.diff already on disk as well as every kept-tdd-appends.diff* file, pinned by a case running the discard as SKILL.md writes it with both kinds of file present ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 30 | 58 | 9206 | 830525 | 135460 | 0.51 | 892 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When rebase_onto_default.py cannot re-apply a set-aside-tdd-appends.diff a killed run left, its exit-2 stop names that set-aside file and every kept-tdd-appends.diff* file on disk, pinned by a case with both kinds of file present ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 89 | 0.12 |
| When rebase_onto_default.py cannot re-apply the uncommitted .tdd/ appends after its rebase, its exit-2 stop names the set-aside-tdd-appends.diff it left on disk as well as every kept-tdd-appends.diff* file, pinned by a case with both kinds of file present ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 90 | 0.11 |
| When SKILL.md's resume discard cannot re-apply the uncommitted .tdd/ appends, its exit-2 stop names a set-aside-tdd-appends.diff already on disk as well as every kept-tdd-appends.diff* file, pinned by a case running the discard as SKILL.md writes it with both kinds of file present ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 58 | 0.13 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 24 | 24 | 23 | 23 | 24 | 25 | 25 | 25 | 0 | 24 | 25 | 25 | 25 | 25 | 0 | 245 | 238 | 24 |
| fast | 16 | 17 | 16 | 17 | 17 | 17 | 17 | 16 | 17 | 16 |  |  |  |  |  |  |  |  |
| target | 24 | 24 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 108 | 210 | 32582 | 3091747 | 434605 | 1.89 |
