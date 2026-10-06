### 📊 Metrics — issue 987

Wall time for the issue: 6411 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/999.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 16 | 2 | 4 | 1566 | 59869 | 43204 | 0.39 |
| red | 9 | 4 | 0 | 0 | 580 | 511 | 84 | 166 | 42981 | 4781347 | 489925 | 5.74 |
| green | 8 | 4 | 0 | 0 | 3038 | 418 | 99 | 186 | 32681 | 5117168 | 419469 | 5.03 |
| refactor | 8 | 4 | 0 | 0 | 1276 | 219 | 54 | 108 | 20041 | 2777933 | 404410 | 4.19 |
| predicate | 2 | 0 | 0 | 0 | 43 | 30 | 8 | 16 | 2752 | 353204 | 87730 | 0.83 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 13 | 13 | 0 | 0 | 2585 | 518 | 109 | 212 | 41093 | 5467625 | 642611 | 7.06 |
| developer | claude-opus-5-5 | 15 | 0 | 0 | 0 | 2372 | 676 | 138 | 268 | 58928 | 7621896 | 802127 | 9.12 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In SKILL.md's preflight step 3, a `.tdd/conductor.pid` write of `$PPID` appears after the `issue-worktree.sh` call and its `cd "$wt"` and before the first fast-tier baseline command (`detect-test-command.sh --tier fast` / `detach-command.sh start`), pinned by line order in a prose suite that goes red when the write sits in step 1.2 instead ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 44 | 88 | 16540 | 2267387 | 300074 | 3.19 | 963 | unknown | 0/5 | structural-owed |  |  | full |
| Preflight step 3 runs `stop-requested.sh --clear` beside its `.tdd/conductor.pid` write and says it is for a stale request a killed run left behind; the `skill-stopping.test.sh` case that required this of step 1.2 requires it of preflight step 3 instead ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 205 | 55 | 106 | 19588 | 2843982 | 307256 | 3.42 | 1162 | unknown | 0/5 | structural-owed |  |  | full |
| Step 1.2 of SKILL.md contains no `.tdd/conductor.pid` write and no `stop-requested.sh --clear`, and a suite case fails if either reappears there ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 284 | 62 | 118 | 20649 | 3223004 | 308516 | 3.53 | 1262 | unknown | 0/5 | nothing-structural |  |  | full |
| The prose explaining the worktree lock (the worktree guard, `$PPID` not `$$`, what it does and does not claim under ADR-0024) states that the lock is taken in preflight step 3, before the baseline, and no sentence in SKILL.md says the lock is taken in step 1.2, pinned by a suite case ⟦criterion 4⟧ | 9 | 3 | 0 | 0 | 0 | 0 | 491 | 84 | 164 | 41678 | 4695279 | 485688 | 5.66 | 1767 | 1/2 | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| In SKILL.md's preflight step 3, a `.tdd/conductor.pid` write of `$PPID` appears after the `issue-worktree.sh` call and its `cd "$wt"` and before the first fast-tier baseline command (`detect-test-command.sh --tier fast` / `detach-command.sh start`), pinned by line order in a prose suite that goes red when the write sits in step 1.2 instead ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 93 | 0.97 |
| Preflight step 3 runs `stop-requested.sh --clear` beside its `.tdd/conductor.pid` write and says it is for a stale request a killed run left behind; the `skill-stopping.test.sh` case that required this of step 1.2 requires it of preflight step 3 instead ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 353 | 0.98 |
| Step 1.2 of SKILL.md contains no `.tdd/conductor.pid` write and no `stop-requested.sh --clear`, and a suite case fails if either reappears there ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 104 | 0.98 |
| The prose explaining the worktree lock (the worktree guard, `$PPID` not `$$`, what it does and does not claim under ADR-0024) states that the lock is taken in preflight step 3, before the baseline, and no sentence in SKILL.md says the lock is taken in step 1.2, pinned by a suite case ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 726 | 1.26 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 235 | 0 | 284 | 2 | 1 | 1 | 206 | 2 | 261 | 0 | 262 | 1 | 1 | 211 | 216 | 0 | 262 | 11 | 1 | 0 | 1 | 0 | 222 | 0 | 269 | 0 | 18 | 0 | 2 | 2 | 0 | 3 | 2 | 141 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 6 | 1 | 0 | 49 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 19 | 5 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 4 | 0 | 1 | 0 | 10 | 1 | 0 | 284 |
| fast | 44 | 45 | 39 | 39 | 39 | 40 | 40 | 40 | 40 | 40 | 39 | 41 | 44 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 2 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 247 | 480 | 100021 | 13089521 | 1444738 | 16.18 |
