### 📊 Metrics — issue 1158

Wall time for the issue: 13039 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1202.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 9 | 2 | 4 | 921 | 65637 | 42330 | 0.19 |
| red | 20 | 9 | 1 | 0 | 1260 | 679 | 115 | 224 | 63121 | 5796459 | 971089 | 8.41 |
| green | 18 | 9 | 0 | 0 | 4856 | 738 | 120 | 242 | 51046 | 6237061 | 833507 | 7.66 |
| refactor | 17 | 8 | 0 | 0 | 1631 | 392 | 87 | 172 | 30557 | 4047369 | 789421 | 6.20 |
| predicate | 6 | 0 | 0 | 0 | 150 | 111 | 24 | 48 | 9440 | 1050203 | 272466 | 2.58 |
| structural | 5 | 0 | 0 | 0 | 135 | 69 | 13 | 26 | 5756 | 487668 | 216088 | 1.94 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 28 | 27 | 1 | 0 | 4771 | 628 | 131 | 262 | 46020 | 5981169 | 1159390 | 6.62 |
| developer | claude-opus-5-5 | 39 | 0 | 0 | 0 | 3275 | 1370 | 230 | 454 | 114821 | 11703228 | 1965511 | 20.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 146 | 1.41 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| stop-run's suites (tests/stop-run.test.sh and tests/py/test_stop_run.py) pin the ported stop_run subject to the repository the suite built under its own scratch directory: a stop_run that resolves its main working tree from anywhere but that scratch repository (e.g. after `cd "$(dirname "$0")"`) fails the case and writes no .tdd/stop and signals no process outside the scratch directory ⟦criterion 1⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 532 | 65 | 130 | 38816 | 3371606 | 548027 | 4.86 | 1348 | unknown | 0/5 | structural-owed |  |  | full |
| tests/py/test_stop_run.py pins stop_run to its scratch repository: a stop_run that resolves a main working tree outside the fixture tree the case built fails the case and writes no .tdd/stop and signals no process outside that tree ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 226 | 39 | 78 | 17784 | 2025950 | 300927 | 2.59 | 632 | unknown | 1/5 | nothing-structural |  |  | full |
| issue-worktree.test.sh pins its subject to the scratch repository: an issue_worktree that resolves its main tree from anywhere but the suite's scratch repository fails the case and creates no worktree, branch or .tdd/wt entry outside the scratch directory ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 172 | 38 | 74 | 14399 | 1865696 | 290585 | 2.39 | 731 | unknown | 0/5 | structural-owed |  |  | full |
| parallel-conductors.test.sh pins its subject to the scratch repository: a parallel_conductors that resolves its git common dir or working directory from anywhere but the suite's scratch repository fails the case and appends to no info/exclude and writes no .tdd/parallel.exit or conductor log outside the scratch directory ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 206 | 44 | 86 | 17913 | 2229436 | 296009 | 2.58 | 1328 | unknown | 0/5 | structural-owed |  |  | full |
| preserve-attempt.test.sh pins its subject to the scratch repository: a preserve_attempt that resolves its toplevel from anywhere but the suite's scratch repository fails the case and writes no .tdd/attempts entry and touches no ledger outside the scratch directory ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 33 | 64 | 12967 | 1544708 | 288343 | 2.29 | 669 | unknown | 0/5 | structural-owed |  |  | full |
| leaf-timeout.test.sh pins its subject to the scratch repository: a leaf_timeout that finds its repository root anywhere but the suite's scratch repository fails the case and creates no .tdd/issue-<n>-timeout outside the scratch directory ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 190 | 42 | 84 | 18738 | 2088597 | 343802 | 2.92 | 622 | 1/2 | 0/5 | structural-owed |  |  | full |
| ensure-run-state-ignored.test.sh pins its subject to the scratch repository: an ensure_run_state_ignored that drops or ignores its root argument fails the case and writes no .gitignore or info/exclude outside the scratch directory ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 142 | 30 | 58 | 12650 | 1389494 | 283429 | 2.23 | 563 | unknown | 0/5 | structural-owed |  |  | full |
| fix the full-suite failure: hermetic-suites.test.sh — FAIL - solvable-issues.test.sh, tick-issue-criterion.test.sh, parallel-conductors.test.sh and invisible-work.test.sh: an ambient VERI_GH_DRIVER of auto, rest or graphql gives the same exit and the same stdout as a cleared run (the slice of parallel-conductors.test.sh held 5 assertions, want 4 — the markers may have moved) ⟦suite-repair⟧ ⟦criterion 1⟧ | 17 | 3 | 0 | 0 | 0 | 0 | 345 | 68 | 138 | 26653 | 3103273 | 731449 | 6.93 | 2731 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| stop-run's suites (tests/stop-run.test.sh and tests/py/test_stop_run.py) pin the ported stop_run subject to the repository the suite built under its own scratch directory: a stop_run that resolves its main working tree from anywhere but that scratch repository (e.g. after `cd "$(dirname "$0")"`) fails the case and writes no .tdd/stop and signals no process outside the scratch directory ⟦criterion 1⟧ | 2 | 0/5 | structural-owed | PASS | 0 | 174 | 1.11 |
| tests/py/test_stop_run.py pins stop_run to its scratch repository: a stop_run that resolves a main working tree outside the fixture tree the case built fails the case and writes no .tdd/stop and signals no process outside that tree ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 207 | 0.81 |
| issue-worktree.test.sh pins its subject to the scratch repository: an issue_worktree that resolves its main tree from anywhere but the suite's scratch repository fails the case and creates no worktree, branch or .tdd/wt entry outside the scratch directory ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 142 | 0.67 |
| parallel-conductors.test.sh pins its subject to the scratch repository: a parallel_conductors that resolves its git common dir or working directory from anywhere but the suite's scratch repository fails the case and appends to no info/exclude and writes no .tdd/parallel.exit or conductor log outside the scratch directory ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 255 | 0.86 |
| preserve-attempt.test.sh pins its subject to the scratch repository: a preserve_attempt that resolves its toplevel from anywhere but the suite's scratch repository fails the case and writes no .tdd/attempts entry and touches no ledger outside the scratch directory ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 158 | 0.70 |
| leaf-timeout.test.sh pins its subject to the scratch repository: a leaf_timeout that finds its repository root anywhere but the suite's scratch repository fails the case and creates no .tdd/issue-<n>-timeout outside the scratch directory ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 141 | 0.71 |
| ensure-run-state-ignored.test.sh pins its subject to the scratch repository: an ensure_run_state_ignored that drops or ignores its root argument fails the case and writes no .gitignore or info/exclude outside the scratch directory ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 123 | 0.64 |
| fix the full-suite failure: hermetic-suites.test.sh — FAIL - solvable-issues.test.sh, tick-issue-criterion.test.sh, parallel-conductors.test.sh and invisible-work.test.sh: an ambient VERI_GH_DRIVER of auto, rest or graphql gives the same exit and the same stdout as a cleared run (the slice of parallel-conductors.test.sh held 5 assertions, want 4 — the markers may have moved) ⟦suite-repair⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 431 | 0.70 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 7 | 4 | 4 | 6 | 5 | 3 | 2 | 0 | 5 | 4 | 5 | 7 | 4 | 30 | 29 | 31 | 107 | 0 | 109 | 91 | 1 | 2 | 12 | 1 | 12 | 16 | 15 | 15 | 0 | 0 | 1 | 13 | 2 | 2 | 5 | 1 | 1 | 3 | 1 | 6 | 5 | 3 | 58 | 58 | 105 | 105 | 0 | 0 | 1 | 0 | 0 | 0 | 181 | 112 | 34 |
| fast | 85 | 83 | 88 | 83 | 86 | 72 | 88 | 83 | 84 | 87 | 73 | 87 | 88 | 77 | 81 | 89 | 84 | 73 | 78 | 87 | 80 | 86 | 87 | 88 | 87 | 85 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 0 | 1 | 30 | 106 | 14 | 3 | 3 | 0 | 173 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 361 | 716 | 160841 | 17684397 | 3124901 | 26.98 |
