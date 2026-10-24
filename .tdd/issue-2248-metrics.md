### 📊 Metrics — issue 2248

Wall time for the issue: 720 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2282.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.73 over 41 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89786 |
| 2 | $0.02 | 90228 |
| 3 | $0.03 | 91189 |
| 4 | $0.03 | 93173 |
| 5 | $0.02 | 93635 |
| 6 | $0.02 | 94014 |
| 7 | $0.02 | 94372 |
| 8 | $0.02 | 94952 |
| 9 | $0.03 | 96943 |
| 10 | $0.04 | 99602 |
| 11 | $0.03 | 101118 |
| 12 | $0.02 | 101529 |
| 13 | $0.03 | 102120 |
| 14 | $0.02 | 102651 |
| 15 | $0.03 | 103323 |
| 16 | $0.02 | 103783 |
| 17 | $0.03 | 105189 |
| 18 | $0.03 | 106118 |
| 19 | $0.03 | 107517 |
| 20 | $0.02 | 107886 |
| 21 | $0.03 | 108588 |
| 22 | $0.03 | 109464 |
| 23 | $0.03 | 109899 |
| 24 | $0.03 | 111091 |
| 25 | $0.03 | 111959 |
| 26 | $0.03 | 112892 |
| 27 | $0.03 | 113565 |
| 28 | $0.03 | 113984 |
| 29 | $0.03 | 114804 |
| 30 | $0.03 | 115772 |
| 31 | $0.03 | 116738 |
| 32 | $0.03 | 117420 |
| 33 | $0.03 | 118665 |
| 34 | $0.04 | 121097 |
| 35 | $0.03 | 121890 |
| 36 | $0.03 | 122185 |
| 37 | $0.03 | 122937 |
| 38 | $0.03 | 123288 |
| 39 | $0.03 | 123591 |
| 40 | $0.03 | 124051 |
| 41 | $0.03 | 124574 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 3 | 6 | 915 | 80466 | 14680 | 0.05 |
| red | 3 | 1 | 0 | 0 | 67 | 52 | 17 | 32 | 6583 | 504403 | 57986 | 0.26 |
| green | 2 | 1 | 0 | 0 | 75 | 30 | 12 | 24 | 3282 | 355109 | 32645 | 0.15 |
| refactor | 2 | 1 | 0 | 0 | 31 | 11 | 6 | 12 | 1244 | 156497 | 28255 | 0.10 |
| pin | 1 | 1 | 0 | 0 | 19 | 13 | 5 | 10 | 1462 | 139203 | 14953 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 100 | 54 | 20 | 40 | 5838 | 545558 | 74219 | 0.30 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 104 | 62 | 23 | 44 | 7648 | 690120 | 74300 | 0.33 |

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

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A ledger holding the step line `- [ ] ⟦human-owed⟧ measure X once deployed` (the mark before the text, no criterion tag) has that step read by `ledger.py`'s `ledger_steps` as kind human-owed, so the step selector (`next-unchecked`) never returns it as the next coding step, agreeing with `run_finished.py`'s `carries_mark` reading of the same line; pinned by a small unit case, no git or subprocess ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 31 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 1 | 1 | 1 | 1 |
| fast | 12 | 12 | 12 | 12 |  |  |
| target | 1 | 1 | 2 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 84 | 13486 | 1235678 | 148519 | 0.63 |
