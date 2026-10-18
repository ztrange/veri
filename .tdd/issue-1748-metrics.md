### 📊 Metrics — issue 1748

Wall time for the issue: 2500 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1755.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 949 | 0 | 30726 | 0.09 |
| red | 11 | 4 | 0 | 0 | 404 | 297 | 65 | 128 | 25079 | 2045727 | 264500 | 1.31 |
| green | 10 | 4 | 1 | 0 | 467 | 175 | 58 | 110 | 13765 | 1583861 | 137281 | 0.70 |
| refactor | 8 | 4 | 0 | 0 | 174 | 70 | 25 | 48 | 5046 | 629293 | 110518 | 0.39 |
| pin | 2 | 2 | 0 | 0 | 85 | 37 | 13 | 26 | 4011 | 364911 | 29009 | 0.15 |
| diff | 2 | 1 | 0 | 0 | 69 | 22 | 8 | 16 | 1676 | 210508 | 25413 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 16 | 1 | 0 | 596 | 240 | 76 | 150 | 21197 | 2053819 | 248716 | 1.04 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 368 | 207 | 68 | 128 | 18693 | 1918130 | 242897 | 0.99 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 246 | 163 | 26 | 52 | 10636 | 862351 | 105834 | 0.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 229 | 0.33 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When a done run's recorded PR URL is empty, run-finished.sh exits 2 with one stderr line saying no PR is recorded, and never calls `gh pr view` without a URL — even when run from a worktree whose branch has an open PR (pinned by a case with gh faked, the fake answering a URL-less `gh pr view` with an open PR's body) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 87 | 27 | 50 | 7563 | 700044 | 113103 | 0.43 | 277 | unknown | 1/5 | nothing-structural |  |  | full |
| An indented unticked human-owed checkbox in the PR body (`  - [ ] … ⟦human-owed⟧`) counts as unmet exactly as one at the start of the line does: exit 1, its `human-owed` line printed (pinned by a case with gh faked) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 73 | 25 | 48 | 5985 | 671792 | 92315 | 0.36 | 242 | unknown | 0/5 | nothing-left |  |  | full |
| An unticked human-owed checkbox in the PR body written `* [ ] … ⟦human-owed⟧` counts as unmet exactly as `- [ ]` does: exit 1, its `human-owed` line printed (pinned by a case with gh faked) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 87 | 29 | 54 | 7071 | 785910 | 94897 | 0.39 | 250 | unknown | 0/5 | nothing-left |  |  | full |
| When a done run's ledger `issue-<n>.md` is missing, run-finished.sh exits 2 with one stderr line naming the missing file and no Python traceback (pinned by a case) ⟦criterion 2⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 254 | 53 | 106 | 18158 | 1647559 | 171006 | 1.02 | 562 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| A run whose state is `stale` is reported not done: exit 1 and the state `stale` named on stdout, exactly as a bailed or stopped run is (pinned by a case, so a check written as `state in ("bailed", "stopped")` goes red) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 13 | 26 | 4364 | 389695 | 35153 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| A run whose state is `running` is reported not done: exit 1 and the state `running` named on stdout, exactly as a bailed or stopped run is (pinned by a case, so a check written as `state in ("bailed", "stopped")` goes red) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 14 | 28 | 4760 | 428792 | 34834 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| run-finished.test.sh's first case builds its scratch repo with the harness's `new_repo` instead of a bare `git init`; no production change and no change to what the case asserts ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 8 | 16 | 1676 | 210508 | 25413 | 0.10 | 110 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a done run's recorded PR URL is empty, run-finished.sh exits 2 with one stderr line saying no PR is recorded, and never calls `gh pr view` without a URL — even when run from a worktree whose branch has an open PR (pinned by a case with gh faked, the fake answering a URL-less `gh pr view` with an open PR's body) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 54 | 0.11 |
| An indented unticked human-owed checkbox in the PR body (`  - [ ] … ⟦human-owed⟧`) counts as unmet exactly as one at the start of the line does: exit 1, its `human-owed` line printed (pinned by a case with gh faked) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| An unticked human-owed checkbox in the PR body written `* [ ] … ⟦human-owed⟧` counts as unmet exactly as `- [ ]` does: exit 1, its `human-owed` line printed (pinned by a case with gh faked) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.09 |
| When a done run's ledger `issue-<n>.md` is missing, run-finished.sh exits 2 with one stderr line naming the missing file and no Python traceback (pinned by a case) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 3 |
| fast | 16 | 16 | 16 | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 17 | 16 |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 5 | 6 | 6 | 0 | 6 | 0 | 0 | 6 | 7 | 7 | 0 | 0 | 7 | 7 | 7 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 170 | 330 | 50526 | 4834300 | 597447 | 2.73 |
