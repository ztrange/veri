### 📊 Metrics — issue 2977

Wall time for the issue: 4899 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3083.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.21 over 47 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90489 tokens, largest 147767 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90489 |
| 2 | $0.08 | 97788 |
| 3 | $0.04 | 100031 |
| 4 | $0.04 | 101975 |
| 5 | $0.02 | 102340 |
| 6 | $0.02 | 102771 |
| 7 | $0.02 | 103099 |
| 8 | $0.02 | 103388 |
| 9 | $0.02 | 103643 |
| 10 | $0.03 | 104499 |
| 11 | $0.03 | 105463 |
| 12 | $0.03 | 106778 |
| 13 | $0.05 | 110032 |
| 14 | $0.03 | 111472 |
| 15 | $0.03 | 112679 |
| 16 | $0.05 | 116632 |
| 17 | $0.04 | 119256 |
| 18 | $0.03 | 120092 |
| 19 | $0.03 | 121043 |
| 20 | $0.03 | 121402 |
| 21 | $0.03 | 122158 |
| 22 | $0.03 | 122751 |
| 23 | $0.03 | 123429 |
| 24 | $0.03 | 124167 |
| 25 | $0.03 | 125325 |
| 26 | $0.03 | 126024 |
| 27 | $0.03 | 126478 |
| 28 | $0.03 | 127255 |
| 29 | $0.03 | 128302 |
| 30 | $0.03 | 128897 |
| 31 | $0.03 | 129626 |
| 32 | $0.09 | 137121 |
| 33 | $0.03 | 137928 |
| 34 | $0.03 | 138278 |
| 35 | $0.03 | 138495 |
| 36 | $0.03 | 138904 |
| 37 | $0.03 | 139605 |
| 38 | $0.07 | 144606 |
| 39 | $0.03 | 145105 |
| 40 | $0.03 | 145693 |
| 41 | $0.03 | 145901 |
| 42 | $0.03 | 146218 |
| 43 | $0.03 | 146638 |
| 44 | $0.03 | 146861 |
| 45 | $0.03 | 147125 |
| 46 | $0.03 | 147489 |
| 47 | $0.03 | 147767 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1251 | 0 | 33162 | 0.10 |
| prose | 7 | 0 | 0 | 0 | 98 | 80 | 7 | 14 | 12375 | 19321 | 75264 | 0.31 |
| skill-edit | 1 | 0 | 0 | 0 | 17 | 13 | 4 | 8 | 1999 | 98594 | 35851 | 0.12 |
| rebase | 2 | 1 | 0 | 0 | 1566 | 49 | 19 | 34 | 3874 | 429537 | 151723 | 0.46 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 1514 | 31 | 7 | 10 | 2932 | 29885 | 148802 | 0.40 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 64 | 27 | 13 | 26 | 2193 | 399652 | 36083 | 0.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/tdd/STRUCTURAL.md applies row DP91: for each candidate the `develop-predicate` leaf runs before the `develop-cover` leaf, its report recorded with `structural-predicate.sh` (exit 1 records the candidate applied at the current HEAD with `refactor-owed.sh applied` and launches neither the cover nor the transform leaf; exit 3 records `no-predicate`; exit 0 goes on to the cover leaf and the transform; exit 2 bails `no-verdict`), with rows DP34 and DP35 of skills/tdd/REQUIREMENTS.md reworded in that same step so the cover leaf follows the predicate rather than the predicate following a covered candidate, and the grader passes the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 51 | 8 | 16 | 7578 | 114234 | 72397 | 0.27 | 106 | unknown | unknown | unknown |  |  | full |
| Rows DP34 and DP35 of skills/tdd/REQUIREMENTS.md state the order DP91 states (predicate leaf first, cover leaf only after a predicate exit 0), and the grader passes skills/tdd/STRUCTURAL.md ⟦skill-edit⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 13 | 1 | 2 | 1993 | 1516 | 12612 | 0.05 | 44 | unknown | unknown | unknown |  |  | full |
| skills/tdd/STRUCTURAL.md says a candidate whose predicate exits 1 before the cover leaf launches no `develop-cover` and no `develop-structural` leaf and is recorded with `refactor-owed.sh applied` at the current HEAD, so `refactor-owed.sh render` shows it under `### Applied` with that HEAD, and the grader passes the unit on DP91 ⟦skill-edit⟧ ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 65 | 20 | 36 | 6625 | 431053 | 164341 | 0.52 | 42 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| all | 31 | 516 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 31 | 58 | 19499 | 547452 | 296000 | 3.20 (estimate) |
