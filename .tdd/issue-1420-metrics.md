### 📊 Metrics — issue 1420

Wall time for the issue: 2968 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1433.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 7 | 1 | 2 | 810 | 12193 | 41397 | 0.17 |
| red | 8 | 3 | 0 | 0 | 341 | 265 | 57 | 112 | 27402 | 3409084 | 462645 | 4.31 |
| green | 8 | 3 | 1 | 0 | 3080 | 286 | 70 | 138 | 23541 | 3743579 | 349788 | 3.21 |
| refactor | 6 | 3 | 0 | 0 | 1081 | 125 | 37 | 72 | 10834 | 1789111 | 284146 | 2.22 |
| pin | 2 | 2 | 0 | 0 | 54 | 23 | 7 | 14 | 2493 | 295079 | 87540 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 12 | 1 | 0 | 2099 | 203 | 62 | 122 | 20158 | 2850956 | 536576 | 2.63 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 2470 | 503 | 110 | 216 | 44922 | 6398090 | 688940 | 7.69 |

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
| Preflight's resume discard never loses run state under `.tdd/`: an untracked-but-not-ignored file there (e.g. `issue-<n>-refactor-owed.md`) is neither removed nor captured as a stray, and uncommitted appends to a tracked file there are not reverted; pinned by a case built on the repo's real `.gitignore` patterns (`.tdd/*`, `!.tdd/issue-*.md`), watched red against the discard as #1433 first shipped it ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 37 | 74 | 16119 | 1898947 | 296114 | 2.42 | 1255 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md's Resume sub-step 2 says the stray capture already happened in preflight step 3 and uses that `$stray`; it never tells the conductor to run `stray="$(git status --porcelain)"` again after the reset, pinned by a prose case that goes red if sub-step 2 re-captures ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 858 | 0.76 |
| On a resume whose worktree holds an untracked file a killed leaf left at a path the default branch has since added, preflight's discard removes it after capturing `$stray`, so `rebase-onto-default.sh` then exits 0 instead of 2, pinned by a case that goes red without the removal ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 122 | 0.79 |
| Preflight's resume discard never loses run state under `.tdd/`: an untracked-but-not-ignored file there (e.g. `issue-<n>-refactor-owed.md`) is neither removed nor captured as a stray, and uncommitted appends to a tracked file there are not reverted; pinned by a case built on the repo's real `.gitignore` patterns (`.tdd/*`, `!.tdd/issue-*.md`), watched red against the discard as #1433 first shipped it ⟦added⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 101 | 0.67 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 267 | 268 | 357 | 362 | 2 | 0 | 3 | 296 | 3 | 4 | 4 | 3 | 269 |
| fast | 72 | 60 | 62 | 63 | 76 | 57 | 60 | 62 | 63 | 62 | 58 |  |  |  |  |
| target | 1 | 0 | 1 | 3 | 4 | 3 | 6 | 4 | 4 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 172 | 338 | 65080 | 9249046 | 1225516 | 10.32 |
