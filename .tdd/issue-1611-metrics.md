### 📊 Metrics — issue 1611

Wall time for the issue: 6220 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1627.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 42 | 37 | 7 | 14 | 2944 | 376780 | 52893 | 0.28 |
| red | 10 | 5 | 0 | 0 | 516 | 252 | 54 | 108 | 24772 | 2788495 | 519241 | 2.60 |
| green | 10 | 5 | 0 | 0 | 2913 | 329 | 78 | 150 | 27076 | 3925318 | 494515 | 2.64 |
| refactor | 10 | 5 | 0 | 0 | 855 | 223 | 50 | 98 | 14799 | 2356460 | 472423 | 2.27 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 16 | 0 | 0 | 1929 | 411 | 89 | 174 | 29857 | 4221528 | 748785 | 3.72 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 2397 | 430 | 100 | 196 | 39734 | 5225525 | 790287 | 4.08 |

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
| SKILL.md's Resume preflight paragraph describes the tree as it stands before rebase-onto-default.sh runs — uncommitted .tdd/ appends kept, ledger ticks reconciled — and the old sentence "its worktree clean and its ledger untouched" no longer appears in SKILL.md; pinned by one prose case asserting both ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 33 | 64 | 9030 | 1551459 | 277875 | 1.36 | 577 | unknown | 0/5 | nothing-left |  |  | full |
| Uncommitted .tdd/ appends rebase-onto-default.sh sets aside for its rebase survive the process being killed at any point after it removed them from the tree: the next resume (preflight step 3's discard, then rebase-onto-default.sh) finds the saved appends and re-applies them, or exits 2 naming the file they are kept in; pinned by a case on a real git repo (a medium case marked process) that kills rebase-onto-default.sh mid-rebase and then runs the next resume ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 184 | 43 | 84 | 15920 | 2219912 | 300163 | 1.58 | 792 | unknown | 1/5 | nothing-left |  |  | full |
| A second failed re-apply of the saved .tdd/ appends never overwrites the appends a first failed re-apply kept: after two failures in a row both sets of appends are still recoverable from disk, and the exit-2 message names where each is kept; pinned by a case on a real git repo (a medium case marked process) running two failing re-applies in a row ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 159 | 35 | 68 | 13550 | 1734697 | 300695 | 1.51 | 1326 | unknown | 0/5 | nothing-left |  |  | full |
| The resume discard judges a ticked ledger step by its green commit, not by its text: a ticked step whose text was changed after its green commit (an instead-of replacement) keeps its tick when that green commit is on the branch; pinned by a case on a real git repo (a medium case marked process) running the SKILL.md discard block ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 189 | 34 | 66 | 12794 | 1663684 | 308029 | 1.53 | 925 | unknown | 0/5 | nothing-left |  |  | full |
| With two ledger steps of identical text, the resume discard judges each tick on its own: a stale tick on one (its green commit not on the branch) is unticked while the other's tick, whose green commit is on the branch, is kept; pinned by a case on a real git repo (a medium case marked process) running the SKILL.md discard block ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 37 | 74 | 15353 | 1900521 | 299417 | 1.54 | 1059 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md's Resume preflight paragraph describes the tree as it stands before rebase-onto-default.sh runs — uncommitted .tdd/ appends kept, ledger ticks reconciled — and the old sentence "its worktree clean and its ledger untouched" no longer appears in SKILL.md; pinned by one prose case asserting both ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 118 | 0.40 |
| Uncommitted .tdd/ appends rebase-onto-default.sh sets aside for its rebase survive the process being killed at any point after it removed them from the tree: the next resume (preflight step 3's discard, then rebase-onto-default.sh) finds the saved appends and re-applies them, or exits 2 naming the file they are kept in; pinned by a case on a real git repo (a medium case marked process) that kills rebase-onto-default.sh mid-rebase and then runs the next resume ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 218 | 0.49 |
| A second failed re-apply of the saved .tdd/ appends never overwrites the appends a first failed re-apply kept: after two failures in a row both sets of appends are still recoverable from disk, and the exit-2 message names where each is kept; pinned by a case on a real git repo (a medium case marked process) running two failing re-applies in a row ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 143 | 0.43 |
| The resume discard judges a ticked ledger step by its green commit, not by its text: a ticked step whose text was changed after its green commit (an instead-of replacement) keeps its tick when that green commit is on the branch; pinned by a case on a real git repo (a medium case marked process) running the SKILL.md discard block ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 164 | 0.46 |
| With two ledger steps of identical text, the resume discard judges each tick on its own: a stale tick on one (its green commit not on the branch) is unticked while the other's tick, whose green commit is on the branch, is kept; pinned by a case on a real git repo (a medium case marked process) running the SKILL.md discard block ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 212 | 0.49 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 30 | 33 | 0 | 0 | 33 | 0 | 32 | 34 | 35 | 301 | 35 | 35 | 35 | 166 | 34 | 34 | 0 | 35 | 4 | 4 |
| fast | 73 | 78 | 71 | 72 | 73 | 72 | 73 | 72 | 74 | 73 | 71 | 71 | 73 | 74 | 73 |  |  |  |  |  |  |  |
| target | 1 | 33 | 33 | 2 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 189 | 370 | 69591 | 9447053 | 1539072 | 7.80 |
