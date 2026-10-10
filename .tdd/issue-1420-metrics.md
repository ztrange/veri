### 📊 Metrics — issue 1420

Wall time for the issue: 5491 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1433.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 7 | 1 | 2 | 810 | 12193 | 41397 | 0.17 |
| red | 6 | 2 | 0 | 0 | 275 | 215 | 47 | 92 | 21918 | 2903808 | 361102 | 3.49 |
| green | 6 | 2 | 1 | 0 | 2107 | 204 | 51 | 100 | 15527 | 2707598 | 248965 | 2.28 |
| refactor | 4 | 2 | 0 | 0 | 980 | 97 | 29 | 56 | 8213 | 1431421 | 190398 | 1.55 |
| pin | 2 | 2 | 0 | 0 | 54 | 23 | 7 | 14 | 2493 | 295079 | 87540 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 1428 | 153 | 48 | 94 | 14973 | 2205193 | 402038 | 1.98 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 2001 | 393 | 87 | 170 | 33988 | 5144906 | 527364 | 5.93 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1563 | 1.55 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| SKILL.md's Resume sub-step 2 says the stray capture already happened in preflight step 3 and uses that `$stray`; it never tells the conductor to run `stray="$(git status --porcelain)"` again after the reset, pinned by a prose case that goes red if sub-step 2 re-captures ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 240 | 67 | 128 | 21345 | 3629348 | 369911 | 3.37 | 2606 | 1/2 | 1/5 | nothing-structural |  |  | full |
| On a resume whose worktree holds an untracked file a killed leaf left at a path the default branch has since added, preflight's discard removes it after capturing `$stray`, so `rebase-onto-default.sh` then exits 0 instead of 2, pinned by a case that goes red without the removal ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 202 | 46 | 92 | 16569 | 2584318 | 312355 | 2.69 | 827 | unknown | 0/5 | nothing-left |  |  | full |
| The untracked stray file is listed in the `$stray` value captured before the removal, the list the ▶️ Resuming comment names ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 59 | 12 | 24 | 6244 | 699758 | 112952 | 0.96 | unknown | unknown | unknown | unknown |  |  | pin |
| Preflight's discard never removes files ignored by `.gitignore` — a `.tdd/` run-state file such as the ledger's leaf logs survives it ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 9 | 18 | 3993 | 424482 | 92787 | 0.71 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md's Resume sub-step 2 says the stray capture already happened in preflight step 3 and uses that `$stray`; it never tells the conductor to run `stray="$(git status --porcelain)"` again after the reset, pinned by a prose case that goes red if sub-step 2 re-captures ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 858 | 0.76 |
| On a resume whose worktree holds an untracked file a killed leaf left at a path the default branch has since added, preflight's discard removes it after capturing `$stray`, so `rebase-onto-default.sh` then exits 0 instead of 2, pinned by a case that goes red without the removal ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 122 | 0.79 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 267 | 268 | 357 | 362 | 2 | 0 | 3 | 296 | 3 | 4 |
| fast | 72 | 60 | 62 | 63 | 76 | 57 | 60 | 62 |  |  |  |  |
| target | 1 | 0 | 1 | 3 | 4 | 3 | 6 | 4 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 135 | 264 | 48961 | 7350099 | 929402 | 7.91 |
