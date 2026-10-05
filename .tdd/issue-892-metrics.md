### 📊 Metrics — issue 892

Wall time for the issue: 3274 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/903.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 2 | 4 | 751 | 53606 | 38594 | 0.17 |
| red | 6 | 3 | 0 | 0 | 401 | 253 | 53 | 104 | 21471 | 2670698 | 279571 | 2.70 |
| green | 6 | 3 | 0 | 0 | 1025 | 206 | 57 | 114 | 19610 | 2733694 | 269245 | 2.52 |
| refactor | 6 | 3 | 0 | 0 | 461 | 173 | 40 | 80 | 14979 | 1882627 | 259420 | 2.23 |
| predicate | 3 | 0 | 0 | 0 | 52 | 44 | 8 | 16 | 3537 | 260771 | 112917 | 1.03 |
| structural | 1 | 0 | 0 | 0 | 79 | 32 | 8 | 16 | 3005 | 373452 | 45037 | 0.50 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 863 | 167 | 52 | 104 | 16896 | 2140742 | 398016 | 2.19 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 1164 | 548 | 116 | 230 | 46457 | 5834106 | 606768 | 6.95 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The Draft PR step's develop-rebase block reads its step text — the build-develop-prompt.sh rebase argument and the leaf launch's VERI_STEP — as the open step or, when none is open, the last done step, the same fallback the verdict-rebase line spells ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 182 | 46 | 90 | 16206 | 2155588 | 261801 | 2.33 | 596 | unknown | 0/5 | nothing-left |  |  | full |
| The develop-reconcile block of Reconciling a rejected push reads its step text — the build-develop-prompt.sh reconcile argument and the leaf launch's VERI_STEP — as the open step or, when none is open, the last done step ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 229 | 52 | 104 | 19972 | 2501667 | 264801 | 2.49 | 758 | unknown | 1/5 | nothing-left |  |  | full |
| The revise loop of Revising on a REJECT reads its step text — the revise event mark's VERI_STEP, the build-develop-prompt.sh revise argument, the revise leaf launch's VERI_STEP and the re-verify launch's VERI_STEP — as the open step or, when none is open, the last done step ⟦criterion 3⟧ | 10 | 3 | 0 | 0 | 0 | 0 | 297 | 68 | 136 | 26424 | 3263987 | 439588 | 4.15 | 741 | unknown | 2/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The Draft PR step's develop-rebase block reads its step text — the build-develop-prompt.sh rebase argument and the leaf launch's VERI_STEP — as the open step or, when none is open, the last done step, the same fallback the verdict-rebase line spells ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 150 | 0.60 |
| The develop-reconcile block of Reconciling a rejected push reads its step text — the build-develop-prompt.sh reconcile argument and the leaf launch's VERI_STEP — as the open step or, when none is open, the last done step ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 160 | 0.79 |
| The revise loop of Revising on a REJECT reads its step text — the revise event mark's VERI_STEP, the build-develop-prompt.sh revise argument, the revise leaf launch's VERI_STEP and the re-verify launch's VERI_STEP — as the open step or, when none is open, the last done step ⟦criterion 3⟧ | 1 | 2/5 | structural-owed | PASS | 0 | 151 | 0.84 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 21 | 21 | 0 | 75 | 0 | 1 | 22 | 22 | 0 | 90 | 0 | 89 | 21 | 22 | 23 | 0 | 102 | 23 | 22 | 22 | 21 |
| fast | 17 | 16 | 16 | 16 | 15 | 15 | 16 | 17 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 22 | 21 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 168 | 334 | 63353 | 7974848 | 1004784 | 9.14 |
