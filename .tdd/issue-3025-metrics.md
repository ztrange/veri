### 📊 Metrics — issue 3025

Wall time for the issue: 2666 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.73 over 57 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90196 tokens, largest 165268 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90196 |
| 2 | $0.08 | 97439 |
| 3 | $0.03 | 99182 |
| 4 | $0.04 | 101109 |
| 5 | $0.02 | 101376 |
| 6 | $0.02 | 101832 |
| 7 | $0.02 | 102152 |
| 8 | $0.02 | 102492 |
| 9 | $0.03 | 103148 |
| 10 | $0.04 | 105741 |
| 11 | $0.05 | 109915 |
| 12 | $0.09 | 118579 |
| 13 | $0.04 | 120810 |
| 14 | $0.03 | 121747 |
| 15 | $0.03 | 122062 |
| 16 | $0.03 | 122991 |
| 17 | $0.03 | 123449 |
| 18 | $0.03 | 124033 |
| 19 | $0.03 | 124575 |
| 20 | $0.11 | 135014 |
| 21 | $0.03 | 135627 |
| 22 | $0.03 | 136486 |
| 23 | $0.05 | 139674 |
| 24 | $0.03 | 140035 |
| 25 | $0.03 | 140798 |
| 26 | $0.03 | 141233 |
| 27 | $0.03 | 142009 |
| 28 | $0.03 | 142660 |
| 29 | $0.03 | 143366 |
| 30 | $0.03 | 143917 |
| 31 | $0.05 | 146812 |
| 32 | $0.03 | 147504 |
| 33 | $0.03 | 147694 |
| 34 | $0.03 | 148187 |
| 35 | $0.03 | 148825 |
| 36 | $0.04 | 150070 |
| 37 | $0.03 | 150412 |
| 38 | $0.04 | 151098 |
| 39 | $0.04 | 151701 |
| 40 | $0.03 | 152011 |
| 41 | $0.04 | 153304 |
| 42 | $0.03 | 153630 |
| 43 | $0.04 | 154286 |
| 44 | $0.04 | 155003 |
| 45 | $0.03 | 155461 |
| 46 | $0.04 | 156076 |
| 47 | $0.03 | 156465 |
| 48 | $0.04 | 157145 |
| 49 | $0.04 | 157810 |
| 50 | $0.04 | 158520 |
| 51 | $0.03 | 158896 |
| 52 | $0.03 | 159130 |
| 53 | $0.04 | 159615 |
| 54 | $0.03 | 159926 |
| 55 | $0.03 | 160236 |
| 56 | $0.04 | 160631 |
| 57 | $0.07 | 165268 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 1 | 2 | 1024 | 0 | 32352 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 149 | 33 | 8 | 16 | 2696 | 211762 | 52476 | 0.18 |
| red | 3 | 1 | 0 | 0 | 142 | 50 | 12 | 22 | 5850 | 318753 | 86306 | 0.31 |
| pin | 1 | 1 | 0 | 0 | 47 | 17 | 4 | 8 | 1598 | 93501 | 33881 | 0.11 |
| green | 2 | 1 | 0 | 0 | 280 | 42 | 14 | 28 | 3690 | 444526 | 37851 | 0.18 |
| refactor | 1 | 0 | 0 | 0 | 11 | 7 | 2 | 4 | 279 | 49131 | 16437 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 356 | 73 | 20 | 40 | 6875 | 534598 | 116532 | 0.41 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 286 | 86 | 21 | 40 | 8262 | 583075 | 142771 | 0.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The existing --graded-only cases of test_rebase_graded_only_process.py whose assertions expect a branch GRADED row kept (the adjacent-units, one-hunk-changed-on-both-sides and two-commits cases) also have their branch commits change the file of each unit whose branch row they expect kept, so they still pass once only units the branch changed keep the branch's row; their assertions and every production file unchanged (test-only, medium process cases) ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 8 | 16 | 2696 | 211762 | 52476 | 0.18 | 680 | n/a | n/a | n/a |  |  | full |
| A --graded-only rebase whose branch changed a unit's file and its GRADED row, while main holds a different row for that unit, exits 0 and keeps the branch's row for that unit, pinned by a new medium (real git process) case in skills/tdd/scripts/tests/py/test_rebase_graded_only_process.py ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 9 | 16 | 4334 | 210450 | 77766 | 0.26 | unknown | unknown | unknown | unknown |  |  | pin |
| A --graded-only rebase whose branch carries a stale GRADED row for a unit whose file the branch never changed, while main holds a newer row for it, exits 0 with main's row for that unit, pinned by a new medium (real git process) case in skills/tdd/scripts/tests/py/test_rebase_graded_only_process.py ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 80 | 23 | 46 | 7083 | 695461 | 96709 | 0.38 | 932 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A --graded-only rebase whose branch carries a stale GRADED row for a unit whose file the branch never changed, while main holds a newer row for it, exits 0 with main's row for that unit, pinned by a new medium (real git process) case in skills/tdd/scripts/tests/py/test_rebase_graded_only_process.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 39 | 43 | 51 | 52 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 12 | 12 | 9 | 11 | 9 | 32 | 11 | 5 | 5 | 11 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 3 | 6 | 7 | 6 | 6 | 4 | 5 | 6 | 6 | 4 | 7 | 5 | 6 | 5 | 6 | 4 | 5 | 6 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 6 | 3 | 3 | 6 | 5 | 5 | 4 | 4 | 4 | 4 | 3 | 5 | 5 | 9 | 15 | 10 | 5 | 4 | 6 | 4 | 4 | 4 | 4 | 5 | 4 | 3 | 4 | 5 | 3 | 3 | 4 | 4 | 3 | 5 | 4 | 4 | 5 | 5 | 6 | 5 | 4 | 5 | 5 | 4 | 4 | 8 | 6 | 5 | 3 | 4 | 4 | 5 | 4 | 4 | 4 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 41 | 80 | 15137 | 1117673 | 259303 | 3.65 (estimate) |
