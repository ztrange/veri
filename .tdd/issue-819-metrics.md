### 📊 Metrics — issue 819

Wall time for the issue: 1249 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/970.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 13 | 2 | 4 | 1334 | 62401 | 41041 | 0.37 |
| red | 12 | 5 | 0 | 0 | 910 | 551 | 104 | 204 | 42366 | 5598216 | 617799 | 6.91 |
| green | 10 | 5 | 0 | 0 | 1450 | 427 | 96 | 186 | 33593 | 4696310 | 466392 | 5.34 |
| refactor | 11 | 5 | 0 | 0 | 659 | 234 | 61 | 120 | 21143 | 2769603 | 495528 | 4.94 |
| pin | 1 | 1 | 0 | 0 | 23 | 19 | 4 | 8 | 1756 | 162982 | 44334 | 0.42 |
| predicate | 2 | 0 | 0 | 0 | 33 | 22 | 7 | 14 | 1779 | 278100 | 78989 | 0.72 |
| structural | 2 | 0 | 0 | 0 | 66 | 28 | 9 | 18 | 2880 | 383906 | 83473 | 0.80 |
| transform | 1 | 1 | 0 | 0 | 74 | 17 | 5 | 10 | 1746 | 210160 | 41049 | 0.41 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 18 | 18 | 0 | 0 | 1543 | 444 | 116 | 226 | 41357 | 5210267 | 788990 | 8.18 |
| developer | claude-opus-5-5 | 22 | 0 | 0 | 0 | 1690 | 867 | 172 | 338 | 65240 | 8951411 | 1079615 | 11.73 |

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
| transform | 0 | 0.00 | 74 | 0.41 |
| wait-ci | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| issue-worktree.sh hands back an existing registered worktree whose .tdd/conductor.pid holds 0 or 00, printing its path and exiting 0, rather than refusing it as held by a live conductor ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 186 | 53 | 104 | 17691 | 2761671 | 288982 | 3.22 | 520 | unknown | 0/5 | nothing-left |  |  | full |
| stop-run.sh for an issue whose worktree's .tdd/conductor.pid holds 0 or 00 exits 3 and writes no .tdd/stop request ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 42 | 82 | 13804 | 1987828 | 270220 | 2.84 | 422 | unknown | 0/5 | nothing-left |  |  | full |
| rebase-onto-default.sh run while a rebase is already in progress in the worktree exits 2 and leaves that rebase in progress, with HEAD and the rebase state directory unchanged ⟦criterion 2⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 362 | 74 | 146 | 31353 | 3737874 | 442238 | 4.91 | 914 | unknown | 0/5 | structural-owed |  |  | already-satisfied |
| issue-worktree.sh <n> <slug> given an <n> that is not a positive whole number exits 2 with its usage on stderr and creates no worktree and no branch ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 248 | 46 | 90 | 17405 | 2400176 | 294423 | 3.18 | 746 | unknown | 0/5 | structural-owed |  |  | full |
| issue-worktree.sh --remove <n> given an <n> that is not a positive whole number exits 2 with its usage on stderr and removes no worktree ⟦criterion 3⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 277 | 50 | 96 | 18605 | 2339562 | 328190 | 3.47 | 847 | 1/2 | 0/5 | structural-owed |  |  | full |
| every case each script's suites already hold passes with its assertions unchanged, apart from an assertion pinning a defect fixed above, listed by file:line in the PR body ⟦full-suite⟧ ⟦criterion 4⟧ | 1 | 1 | 0 | 0 | 0 | 0 | 17 | 5 | 10 | 1746 | 210160 | 41049 | 0.41 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| issue-worktree.sh hands back an existing registered worktree whose .tdd/conductor.pid holds 0 or 00, printing its path and exiting 0, rather than refusing it as held by a live conductor ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 131 | 0.85 |
| stop-run.sh for an issue whose worktree's .tdd/conductor.pid holds 0 or 00 exits 3 and writes no .tdd/stop request ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 89 | 0.82 |
| rebase-onto-default.sh run while a rebase is already in progress in the worktree exits 2 and leaves that rebase in progress, with HEAD and the rebase state directory unchanged ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 182 | 1.57 |
| rebase-onto-default.sh run while a rebase is already in progress in the worktree exits 2 and leaves that rebase in progress, with HEAD and the rebase state directory unchanged ⟦criterion 2⟧ | 2 | 0/5 | structural-owed |  | 0 | 0 | 0.00 |
| issue-worktree.sh <n> <slug> given an <n> that is not a positive whole number exits 2 with its usage on stderr and creates no worktree and no branch ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 121 | 0.82 |
| issue-worktree.sh --remove <n> given an <n> that is not a positive whole number exits 2 with its usage on stderr and removes no worktree ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 136 | 0.88 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 12 | 22 | 21 | 3 | 2 | 3 | 4 | 3 | 15 | 16 | 9 | 16 | 1 | 0 | 1 | 16 | 22 | 21 | 12 | 22 | 22 | 21 | 21 | 22 | 23 | 23 | 23 | 23 | 1 | 27 | 26 | 26 |
| fast | 45 | 44 | 41 | 42 | 42 | 40 | 40 | 41 | 42 | 42 | 42 | 41 | 42 | 48 | 44 | 43 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 2 | 2 | 16 | 0 | 1 | 21 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 288 | 564 | 106597 | 14161678 | 1868605 | 19.92 |
