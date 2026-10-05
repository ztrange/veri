### 📊 Metrics — issue 954

Wall time for the issue: 12477 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/971.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 27 | 22 | 2 | 4 | 2126 | 63697 | 46853 | 0.43 |
| red | 19 | 8 | 1 | 0 | 1538 | 714 | 159 | 312 | 65087 | 8881134 | 971260 | 10.85 |
| green | 22 | 8 | 3 | 0 | 6474 | 897 | 223 | 432 | 87572 | 11529997 | 1049200 | 12.45 |
| refactor | 16 | 8 | 0 | 0 | 1267 | 323 | 88 | 174 | 29581 | 4072819 | 731641 | 7.26 |
| pin | 1 | 1 | 0 | 0 | 121 | 17 | 4 | 8 | 1786 | 170876 | 43917 | 0.42 |
| predicate | 2 | 0 | 0 | 0 | 31 | 21 | 5 | 10 | 1657 | 180557 | 82782 | 0.73 |
| structural | 1 | 0 | 0 | 0 | 75 | 15 | 4 | 8 | 1421 | 172925 | 43576 | 0.41 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 30 | 26 | 4 | 0 | 5686 | 952 | 220 | 434 | 89406 | 10767712 | 1328158 | 14.57 |
| developer | claude-opus-5-5 | 32 | 0 | 0 | 0 | 3847 | 1057 | 265 | 514 | 99824 | 14304293 | 1641071 | 17.99 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 160 | 1.87 | 0 | 0.00 |
| green | 3545 | 6.43 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise.sh launched with VERI_TIMEOUT unset, in a worktree whose run state records a settled timeout for the run's issue (VERI_ISSUE), supervises the leaf under that recorded value: a leaf outliving an injected small settled value is killed-stuck with `hard timeout <settled>s exceeded`, not `900s` ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 238 | 58 | 108 | 21811 | 2803834 | 360505 | 3.88 | 1197 | 1/2 | 0/5 | nothing-left |  |  | full |
| supervise.sh refuses a settled-timeout record in .tdd/issue-<n>-timeout that is empty or not a whole number >= 1, with exit 2 and a stderr line naming the file, rather than falling back to 900 or misreading it ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 42 | 80 | 14781 | 1951318 | 278522 | 2.91 | 757 | unknown | 0/5 | nothing-left |  |  | full |
| supervise.sh finds the settled-timeout record for VERI_ISSUE when launched from a subdirectory of the run worktree, not only from its root ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 193 | 44 | 88 | 16661 | 2199379 | 281023 | 3.02 | 985 | unknown | 1/5 | nothing-structural |  |  | full |
| the conductor's settling of the timeout records it in the worktree's run state once per issue: a second settling for the same issue (a resumed run in a new conductor session) leaves the recorded value in place, so the resumed run's leaves are supervised under the first session's settled timeout without re-measuring ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 331 | 78 | 154 | 31105 | 4399040 | 395418 | 4.67 | 1302 | 1/2 | 0/5 | nothing-left |  |  | full |
| leaf-timeout.sh, settling from a subdirectory of the run worktree, records the settled timeout at the worktree root's .tdd/issue-<n>-timeout, where supervise.sh reads it ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 211 | 49 | 98 | 19219 | 2510920 | 285599 | 3.17 | 928 | unknown | 0/5 | structural-owed |  |  | full |
| a leaf's test run cannot settle the run's timeout: running leaf-timeout.test.sh inside a run worktree with VERI_ISSUE=<n> in the environment, as every leaf has, leaves no .tdd/issue-<n>-timeout in that worktree ⟦added⟧ ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 331 | 74 | 146 | 31285 | 4170061 | 423518 | 4.85 | 2632 | 1/2 | 0/5 | nothing-left |  |  | full |
| an explicit VERI_TIMEOUT in the leaf's environment wins over the recorded settled timeout: supervise.sh kills a leaf with `hard timeout <explicit>s exceeded` when both are present ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 14 | 28 | 6005 | 722826 | 95688 | 1.03 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's preflight step 7 no longer claims an export in the conductor's shell is in force for later launches; it names the run-state file the settled timeout is recorded in and says supervise.sh picks it up when VERI_TIMEOUT is unset ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 177 | 52 | 100 | 18268 | 2640709 | 299683 | 3.29 | 957 | unknown | 0/5 | nothing-left |  |  | full |
| SKILL.md records the settled timeout inside the issue's run worktree: the leaf-timeout.sh call that writes .tdd/issue-<n>-timeout is made after step 1.2 has entered the worktree, not from the caller's checkout where preflight runs, so the record lands where that run's supervise.sh reads it ⟦added⟧ ⟦criterion 4⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 247 | 63 | 124 | 24891 | 3256739 | 376062 | 4.16 | 991 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.sh launched with VERI_TIMEOUT unset, in a worktree whose run state records a settled timeout for the run's issue (VERI_ISSUE), supervises the leaf under that recorded value: a leaf outliving an injected small settled value is killed-stuck with `hard timeout <settled>s exceeded`, not `900s` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 142 | 0.92 |
| supervise.sh refuses a settled-timeout record in .tdd/issue-<n>-timeout that is empty or not a whole number >= 1, with exit 2 and a stderr line naming the file, rather than falling back to 900 or misreading it ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 144 | 0.89 |
| supervise.sh finds the settled-timeout record for VERI_ISSUE when launched from a subdirectory of the run worktree, not only from its root ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 246 | 0.93 |
| the conductor's settling of the timeout records it in the worktree's run state once per issue: a second settling for the same issue (a resumed run in a new conductor session) leaves the recorded value in place, so the resumed run's leaves are supervised under the first session's settled timeout without re-measuring ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 112 | 0.94 |
| leaf-timeout.sh, settling from a subdirectory of the run worktree, records the settled timeout at the worktree root's .tdd/issue-<n>-timeout, where supervise.sh reads it ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 110 | 0.87 |
| a leaf's test run cannot settle the run's timeout: running leaf-timeout.test.sh inside a run worktree with VERI_ISSUE=<n> in the environment, as every leaf has, leaves no .tdd/issue-<n>-timeout in that worktree ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 347 | 0.90 |
| SKILL.md's preflight step 7 no longer claims an export in the conductor's shell is in force for later launches; it names the run-state file the settled timeout is recorded in and says supervise.sh picks it up when VERI_TIMEOUT is unset ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.91 |
| SKILL.md records the settled timeout inside the issue's run worktree: the leaf-timeout.sh call that writes .tdd/issue-<n>-timeout is made after step 1.2 has entered the worktree, not from the caller's checkout where preflight runs, so the record lands where that run's supervise.sh reads it ⟦added⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.90 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 46 | 47 | 44 | 44 | 46 | 47 | 45 | 49 | 48 | 46 | 46 | 49 | 50 | 50 | 51 | 57 | 52 | 50 | 1 | 1 | 2 | 216 | 210 | 2 | 0 | 2 | 0 | 1 | 0 | 3 | 2 | 2 | 2 | 2 | 0 | 55 | 3 | 143 | 142 | 134 | 141 | 119 | 126 | 134 | 49 | 0 | 0 | 205 | 174 | 175 | 0 | 0 | 9 | 9 | 0 | 211 | 0 | 253 | 0 | 55 |
| fast | 41 | 40 | 40 | 40 | 39 | 43 | 40 | 42 | 39 | 40 | 41 | 43 | 42 | 57 | 50 | 49 | 53 | 52 | 49 | 49 | 51 | 48 | 46 | 42 | 40 | 40 | 40 | 41 | 40 | 43 | 39 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 43 | 47 | 48 | 51 | 1 | 1 | 2 | 145 | 132 | 48 | 51 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 485 | 948 | 189230 | 25072005 | 2969229 | 32.56 |
