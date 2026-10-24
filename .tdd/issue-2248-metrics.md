### 📊 Metrics — issue 2248

Wall time for the issue: 751 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2282.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.21 over 83 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89786 |
| 2 | $0.03 | 90228 |
| 3 | $0.03 | 91189 |
| 4 | $0.05 | 93173 |
| 5 | $0.03 | 93635 |
| 6 | $0.03 | 94014 |
| 7 | $0.03 | 94372 |
| 8 | $0.03 | 94952 |
| 9 | $0.05 | 96943 |
| 10 | $0.05 | 99602 |
| 11 | $0.04 | 101118 |
| 12 | $0.03 | 101529 |
| 13 | $0.04 | 102120 |
| 14 | $0.03 | 102651 |
| 15 | $0.04 | 103323 |
| 16 | $0.03 | 103783 |
| 17 | $0.04 | 105189 |
| 18 | $0.04 | 106118 |
| 19 | $0.04 | 107517 |
| 20 | $0.04 | 107886 |
| 21 | $0.03 | 108588 |
| 22 | $0.04 | 109464 |
| 23 | $0.04 | 109899 |
| 24 | $0.04 | 111091 |
| 25 | $0.04 | 111959 |
| 26 | $0.03 | 112892 |
| 27 | $0.04 | 113565 |
| 28 | $0.04 | 113984 |
| 29 | $0.04 | 114804 |
| 30 | $0.04 | 115772 |
| 31 | $0.04 | 116738 |
| 32 | $0.04 | 117420 |
| 33 | $0.04 | 118665 |
| 34 | $0.05 | 121097 |
| 35 | $0.04 | 121890 |
| 36 | $0.04 | 122185 |
| 37 | $0.04 | 122937 |
| 38 | $0.03 | 123288 |
| 39 | $0.04 | 123591 |
| 40 | $0.04 | 124051 |
| 41 | $0.04 | 124574 |
| 42 | $0.04 | 125105 |
| 43 | $0.04 | 126013 |
| 44 | $0.04 | 126582 |
| 45 | $0.58 | 89786 |
| 46 | $0.03 | 91014 |
| 47 | $0.02 | 91479 |
| 48 | $0.03 | 93181 |
| 49 | $0.03 | 94385 |
| 50 | $0.24 | 121572 |
| 51 | $0.03 | 122016 |
| 52 | $0.03 | 122554 |
| 53 | $0.03 | 122911 |
| 54 | $0.03 | 123241 |
| 55 | $0.03 | 123601 |
| 56 | $0.03 | 124361 |
| 57 | $0.03 | 125283 |
| 58 | $0.03 | 125969 |
| 59 | $0.03 | 126871 |
| 60 | $0.04 | 128269 |
| 61 | $0.03 | 129177 |
| 62 | $0.03 | 129603 |
| 63 | $0.03 | 130169 |
| 64 | $0.03 | 131254 |
| 65 | $0.04 | 132645 |
| 66 | $0.03 | 133680 |
| 67 | $0.03 | 134697 |
| 68 | $0.03 | 135231 |
| 69 | $0.03 | 135588 |
| 70 | $0.03 | 136102 |
| 71 | $0.03 | 136825 |
| 72 | $0.04 | 137820 |
| 73 | $0.03 | 138361 |
| 74 | $0.03 | 138937 |
| 75 | $0.03 | 139361 |
| 76 | $0.03 | 140022 |
| 77 | $0.03 | 140809 |
| 78 | $0.03 | 141470 |
| 79 | $0.03 | 141901 |
| 80 | $0.03 | 142254 |
| 81 | $0.03 | 142813 |
| 82 | $0.03 | 143181 |
| 83 | $0.03 | 143635 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 3 | 6 | 915 | 80466 | 14680 | 0.05 |
| red | 5 | 2 | 0 | 0 | 104 | 81 | 26 | 50 | 9755 | 771701 | 94264 | 0.41 |
| green | 4 | 2 | 0 | 0 | 141 | 60 | 26 | 52 | 6528 | 775743 | 66084 | 0.31 |
| refactor | 4 | 2 | 0 | 0 | 61 | 23 | 12 | 24 | 2351 | 313406 | 55962 | 0.19 |
| pin | 1 | 1 | 0 | 0 | 19 | 13 | 5 | 10 | 1462 | 139203 | 14953 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 171 | 85 | 33 | 66 | 9335 | 909356 | 121089 | 0.49 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 166 | 102 | 39 | 76 | 11676 | 1171163 | 124854 | 0.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A ledger holding the step line `- [ ] ⟦human-owed⟧ measure X once deployed` (the mark before the text, no criterion tag) has that step read by `ledger.py`'s `ledger_steps` as kind human-owed, so the step selector (`next-unchecked`) never returns it as the next coding step, agreeing with `run_finished.py`'s `carries_mark` reading of the same line; pinned by a small unit case, no git or subprocess ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 68 | 27 | 54 | 7906 | 788029 | 98528 | 0.40 | 240 | unknown | 0/5 | nothing-structural |  |  | full |
| The same line carrying a criterion tag, `- [ ] ⟦human-owed⟧ measure X once deployed ⟦criterion 2⟧`, is read by `ledger_steps` as kind human-owed with criterion 2, and is likewise never returned by the step selector; pinned by a small unit case, no git or subprocess ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 13 | 24 | 4665 | 367183 | 35311 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| A ledger step whose ⟦human-owed⟧ mark trails the prose with no ⟦criterion N⟧ tag (`- [ ] measure X ⟦human-owed⟧`) is read as kind human-owed by ledger_steps, never returned as a coding step, and agrees with run_finished.py's carries_mark: pinned by a small unit case in tests/py/unit/test_ledger_steps.py; the #1450 mid-prose quote guard stays green ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 71 | 29 | 58 | 7525 | 844841 | 97424 | 0.40 | 264 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A ledger holding the step line `- [ ] ⟦human-owed⟧ measure X once deployed` (the mark before the text, no criterion tag) has that step read by `ledger.py`'s `ledger_steps` as kind human-owed, so the step selector (`next-unchecked`) never returns it as the next coding step, agreeing with `run_finished.py`'s `carries_mark` reading of the same line; pinned by a small unit case, no git or subprocess ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 31 | 0.10 |
| A ledger step whose ⟦human-owed⟧ mark trails the prose with no ⟦criterion N⟧ tag (`- [ ] measure X ⟦human-owed⟧`) is read as kind human-owed by ledger_steps, never returned as a coding step, and agrees with run_finished.py's carries_mark: pinned by a small unit case in tests/py/unit/test_ledger_steps.py; the #1450 mid-prose quote guard stays green ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 30 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 1 |
| fast | 12 | 12 | 12 | 12 | 12 | 12 | 11 |  |  |  |  |
| target | 1 | 1 | 2 | 1 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 72 | 142 | 21011 | 2080519 | 245943 | 1.03 |
