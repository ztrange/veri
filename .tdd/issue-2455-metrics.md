### 📊 Metrics — issue 2455

Wall time for the issue: 3425 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2493.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.73 over 65 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88652 tokens, largest 159961 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88652 |
| 2 | $0.03 | 90707 |
| 3 | $0.03 | 92649 |
| 4 | $0.02 | 92996 |
| 5 | $0.02 | 93338 |
| 6 | $0.02 | 93800 |
| 7 | $0.02 | 94142 |
| 8 | $0.03 | 94958 |
| 9 | $0.03 | 96161 |
| 10 | $0.04 | 98703 |
| 11 | $0.03 | 99543 |
| 12 | $0.03 | 100418 |
| 13 | $0.02 | 100948 |
| 14 | $0.03 | 101942 |
| 15 | $0.03 | 103337 |
| 16 | $0.03 | 104328 |
| 17 | $0.03 | 105399 |
| 18 | $0.02 | 105828 |
| 19 | $0.03 | 106566 |
| 20 | $0.03 | 107545 |
| 21 | $0.03 | 108581 |
| 22 | $0.03 | 109329 |
| 23 | $0.03 | 110191 |
| 24 | $0.03 | 110896 |
| 25 | $0.03 | 111434 |
| 26 | $0.03 | 112466 |
| 27 | $0.03 | 112924 |
| 28 | $0.04 | 114662 |
| 29 | $0.04 | 117186 |
| 30 | $0.03 | 117904 |
| 31 | $0.03 | 118244 |
| 32 | $0.03 | 119009 |
| 33 | $0.04 | 120945 |
| 34 | $0.03 | 121922 |
| 35 | $0.04 | 123865 |
| 36 | $0.03 | 124895 |
| 37 | $0.04 | 126288 |
| 38 | $0.03 | 126934 |
| 39 | $0.04 | 128451 |
| 40 | $0.04 | 129735 |
| 41 | $0.03 | 130005 |
| 42 | $0.03 | 130487 |
| 43 | $0.03 | 130791 |
| 44 | $0.04 | 132129 |
| 45 | $0.03 | 132601 |
| 46 | $0.04 | 134429 |
| 47 | $0.03 | 135427 |
| 48 | $0.09 | 143478 |
| 49 | $0.05 | 146337 |
| 50 | $0.03 | 146798 |
| 51 | $0.04 | 147532 |
| 52 | $0.03 | 147853 |
| 53 | $0.04 | 148581 |
| 54 | $0.03 | 148959 |
| 55 | $0.04 | 149706 |
| 56 | $0.03 | 150326 |
| 57 | $0.03 | 150691 |
| 58 | $0.06 | 153879 |
| 59 | $0.04 | 154564 |
| 60 | $0.04 | 155475 |
| 61 | $0.04 | 156235 |
| 62 | $0.04 | 157192 |
| 63 | $0.04 | 157855 |
| 64 | $0.04 | 159358 |
| 65 | $0.04 | 159961 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 954 | 0 | 33354 | 0.09 |
| red | 7 | 2 | 0 | 0 | 203 | 132 | 31 | 60 | 14800 | 912971 | 203970 | 0.89 |
| green | 4 | 2 | 0 | 0 | 242 | 64 | 22 | 38 | 6017 | 572014 | 71345 | 0.30 |
| refactor | 3 | 1 | 0 | 0 | 60 | 32 | 10 | 20 | 3156 | 288168 | 50797 | 0.19 |
| pin | 3 | 2 | 1 | 0 | 82 | 37 | 10 | 20 | 4073 | 273472 | 53794 | 0.20 |
| cover | 1 | 0 | 0 | 0 | 41 | 21 | 6 | 12 | 1338 | 165939 | 34580 | 0.12 |
| predicate | 1 | 0 | 0 | 0 | 17 | 14 | 4 | 8 | 580 | 111281 | 14292 | 0.05 |
| structural | 1 | 0 | 0 | 0 | 41 | 18 | 4 | 8 | 1199 | 115167 | 16114 | 0.06 |
| transform | 1 | 1 | 0 | 0 | 25 | 8 | 3 | 6 | 714 | 61713 | 31578 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 340 | 114 | 33 | 66 | 11192 | 877806 | 201934 | 0.70 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 270 | 157 | 46 | 84 | 14635 | 1247578 | 225394 | 0.83 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 112 | 63 | 12 | 24 | 7004 | 375341 | 82496 | 0.45 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 62 | 0.13 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A queued-merge run whose local `git branch -D` of the merged branch fails names that failure on stderr, lists it in the "merged, but cleanup failed" summary and exits 2 (a small unit case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through the existing fake_processes `scenario(fail=...)` harness, failing on the current code) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 57 | 18 | 34 | 5321 | 471268 | 104435 | 0.36 | 238 | unknown | 0/5 | nothing-left |  |  | full |
| A successful queued-merge run still exits 0 and deletes the local branch with `git branch -D` exactly once, and only after the worktree is removed (a small unit case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py using the fake_processes harness; no production change expected) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 8 | 16 | 3584 | 244079 | 39570 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| With the main clone checked out on a branch other than `main`, a queued-merge run does not fast-forward that branch to origin/main, names on stderr why the fast-forward was not done, and lists the fast-forward in the cleanup-failed summary (a small unit case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py using the fake_processes harness) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 93 | 29 | 52 | 9711 | 795773 | 116038 | 0.47 | 375 | unknown | 1/5 | structural-owed |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_queued_merge_process.py — test_queued_merge_with_green_ci_rebase_merges_the_pr_for_the_pushed_head_deletes_the_branch_removes_the_worktree_exits_0_and_frees_the_merge_lock_2372: assert (2, 0, 1, True, True) == (0, 0, 1, True, True); test_queued_merge_after_a_confirmed_merge_cuts_the_next_version_tag_on_the_reported_merge_commit_with_the_message_and_pushes_it_but_cuts_none_for_a_dash_2372: assert (2, 1, 1, 2, []) == (0, 1, 1, 0, []) ⟦suite-repair⟧ ⟦criterion 3⟧ | 8 | 2 | 1 | 0 | 0 | 0 | 147 | 35 | 70 | 13261 | 989605 | 216427 | 0.91 | unknown | 1/2 | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A queued-merge run whose local `git branch -D` of the merged branch fails names that failure on stderr, lists it in the "merged, but cleanup failed" summary and exits 2 (a small unit case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py driven through the existing fake_processes `scenario(fail=...)` harness, failing on the current code) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.05 |
| With the main clone checked out on a branch other than `main`, a queued-merge run does not fast-forward that branch to origin/main, names on stderr why the fast-forward was not done, and lists the fast-forward in the cleanup-failed summary (a small unit case in skills/tdd/scripts/tests/py/unit/test_queued_merge.py using the fake_processes harness) ⟦criterion 3⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 50 | 0.13 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 18 | 1 | 1 | 13 | 13 | 1 | 19 | 13 |
| fast | 19 | 19 | 19 | 18 | 18 |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 3 | 14 | 13 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 91 | 174 | 32831 | 2500725 | 509824 | 1.99 |
