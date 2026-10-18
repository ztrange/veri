### 📊 Metrics — issue 1734

Wall time for the issue: 3038 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1769.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 1 | 2 | 1656 | 0 | 31953 | 0.10 |
| diff | 4 | 2 | 0 | 0 | 328 | 57 | 21 | 42 | 6003 | 592490 | 84934 | 0.33 |
| red | 7 | 2 | 0 | 0 | 302 | 146 | 48 | 88 | 19428 | 1530482 | 165745 | 0.76 |
| green | 4 | 2 | 0 | 0 | 308 | 68 | 25 | 46 | 7794 | 713963 | 76975 | 0.34 |
| refactor | 4 | 2 | 0 | 0 | 132 | 35 | 16 | 28 | 3417 | 390569 | 62291 | 0.23 |
| pin | 3 | 3 | 0 | 0 | 161 | 34 | 13 | 26 | 3569 | 364011 | 48404 | 0.19 |
| predicate | 1 | 0 | 0 | 0 | 9 | 6 | 3 | 6 | 445 | 59339 | 30512 | 0.09 |
| structural | 1 | 0 | 0 | 0 | 7 | 4 | 2 | 4 | 271 | 47561 | 12583 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 639 | 149 | 51 | 98 | 15716 | 1356740 | 210862 | 0.82 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 625 | 215 | 78 | 144 | 26867 | 2341675 | 302535 | 1.26 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The remote-only checkout cases are removed, with no production change: the bash cases "a branch that exists only on the remote: checked out at its own tip…" and "a worktree made for a remote-only branch tracks that remote branch" in skills/tdd/scripts/tests/issue-worktree.test.sh, and the second loop (the remote-tracking arm) of test_main_checks_out_a_local_branch_else_cuts_from_the_remote_one_without_a_fetch_and_maps_a_dying_add_to_2 in skills/tdd/scripts/tests/py/test_issue_worktree.py, whose name drops the remote half ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 7 | 14 | 2869 | 178795 | 52774 | 0.18 | 157 | n/a | n/a | n/a |  |  | full |
| A fresh run whose clone holds refs/remotes/origin/tdd/<n>-<slug>, while origin's live ls-remote also names that branch and the clone has neither a local tdd/<n>-* branch nor a registered .tdd/wt/<n>, makes issue-worktree.sh exit 2 with stderr naming the branch and the command `git branch tdd/<n>-<slug> origin/tdd/<n>-<slug>` that takes the run over, creating no local branch and no worktree — a medium bash case in issue-worktree.test.sh over a real cloned upstream ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 31 | 58 | 9814 | 886668 | 109060 | 0.46 | 435 | unknown | 1/5 | structural-owed |  |  | full |
| The same refusal pinned as a small pytest case in test_issue_worktree.py, git faked at the process boundary: the remote-tracking ref exists and ls-remote --heads names the branch, so issue_worktree.main exits 2 with that stderr and makes no `git worktree add` call ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 12 | 24 | 3964 | 411925 | 42687 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| A clone holding the local branch tdd/<n>-<slug>, with origin also holding the branch and the remote-tracking ref present, still starts as a resume: issue-worktree.sh exits 0 printing the worktree path, checked out on the local branch's own tip — a medium bash case over a real cloned upstream ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 13 | 26 | 5104 | 428231 | 40567 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| A clone with the issue's .tdd/wt/<n> already registered as a worktree, with origin holding the branch and the remote-tracking ref present, still starts as a resume: issue-worktree.sh exits 0 printing that same path on the branch's own tip — a medium bash case over a real cloned upstream ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 13 | 26 | 4946 | 447429 | 44392 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| A stale remote-tracking ref refuses nothing: when the clone holds refs/remotes/origin/tdd/<n>-<slug> but origin's live ls-remote no longer names any tdd/<n>-* branch, issue-worktree.sh cuts a fresh branch from origin/<default> and exits 0 printing the path | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 33 | 54 | 10380 | 824772 | 116709 | 0.48 | 316 | unknown | 0/5 | nothing-left |  |  | full |
| The issue-worktree.sh entry in skills/tdd/SCRIPTS.md says a fresh run refuses (exit 2) an issue branch origin holds even when this clone has fetched it, that only a local branch or a registered worktree makes a run a resume, and names the `git branch tdd/<n>-<slug> origin/tdd/<n>-<slug>` takeover ⟦diff-checked⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 41 | 19 | 38 | 3850 | 520595 | 75255 | 0.28 | 269 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A fresh run whose clone holds refs/remotes/origin/tdd/<n>-<slug>, while origin's live ls-remote also names that branch and the clone has neither a local tdd/<n>-* branch nor a registered .tdd/wt/<n>, makes issue-worktree.sh exit 2 with stderr naming the branch and the command `git branch tdd/<n>-<slug> origin/tdd/<n>-<slug>` that takes the run over, creating no local branch and no worktree — a medium bash case in issue-worktree.test.sh over a real cloned upstream ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 78 | 0.13 |
| A stale remote-tracking ref refuses nothing: when the clone holds refs/remotes/origin/tdd/<n>-<slug> but origin's live ls-remote no longer names any tdd/<n>-* branch, issue-worktree.sh cuts a fresh branch from origin/<default> and exits 0 printing the path | 1 | 0/5 | nothing-left | PASS | 0 | 54 | 0.10 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 19 | 17 | 18 | 18 | 19 | 18 | 18 | 17 | 16 | 17 |  |  |  |  |  |  |  |  |  |  |
| affected | 18 | 16 | 16 | 0 | 17 | 30 | 18 | 16 | 1 | 17 | 18 | 2 | 1 | 19 | 27 | 17 | 0 | 76 | 0 | 77 |
| target | 29 | 1 | 1 | 0 | 29 | 29 | 29 | 28 | 1 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 129 | 242 | 42583 | 3698415 | 513397 | 2.08 |
