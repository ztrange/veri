### 📊 Metrics — issue 2837

Wall time for the issue: 3716 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2844.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.45 over 63 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87691 tokens, largest 166108 tokens
Conductor context: first turn 87722 tokens, largest 168292 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 87691 |
| 2 | $0.11 | 96746 |
| 3 | $0.05 | 98863 |
| 4 | $0.05 | 99379 |
| 5 | $0.04 | 99748 |
| 6 | $0.04 | 100125 |
| 7 | $0.04 | 100445 |
| 8 | $0.08 | 105532 |
| 9 | $0.07 | 109104 |
| 10 | $0.16 | 124408 |
| 11 | $0.06 | 125262 |
| 12 | $0.04 | 125502 |
| 13 | $0.06 | 127450 |
| 14 | $0.05 | 128333 |
| 15 | $0.07 | 130619 |
| 16 | $0.05 | 131404 |
| 17 | $0.12 | 141636 |
| 18 | $0.07 | 144530 |
| 19 | $0.09 | 149116 |
| 20 | $0.07 | 152439 |
| 21 | $0.06 | 153308 |
| 22 | $0.07 | 155206 |
| 23 | $0.06 | 156376 |
| 24 | $0.06 | 158247 |
| 25 | $0.10 | 163788 |
| 26 | $0.07 | 166108 |
| 27 | $0.56 | 87722 |
| 28 | $0.07 | 94725 |
| 29 | $0.04 | 96854 |
| 30 | $0.05 | 100782 |
| 31 | $0.16 | 118254 |
| 32 | $0.04 | 120240 |
| 33 | $0.03 | 120999 |
| 34 | $0.03 | 121401 |
| 35 | $0.03 | 121737 |
| 36 | $0.04 | 123788 |
| 37 | $0.06 | 128752 |
| 38 | $0.06 | 132691 |
| 39 | $0.03 | 133593 |
| 40 | $0.05 | 135926 |
| 41 | $0.05 | 138931 |
| 42 | $0.04 | 140999 |
| 43 | $0.04 | 142978 |
| 44 | $0.04 | 143824 |
| 45 | $0.05 | 146097 |
| 46 | $0.04 | 147524 |
| 47 | $0.04 | 148824 |
| 48 | $0.06 | 152166 |
| 49 | $0.06 | 155578 |
| 50 | $0.04 | 157069 |
| 51 | $0.04 | 157808 |
| 52 | $0.04 | 158338 |
| 53 | $0.04 | 159041 |
| 54 | $0.03 | 159333 |
| 55 | $0.06 | 163040 |
| 56 | $0.04 | 164435 |
| 57 | $0.04 | 165260 |
| 58 | $0.04 | 166285 |
| 59 | $0.04 | 167689 |
| 60 | $0.04 | 168292 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 959 | 0 | 33651 | 0.09 |
| red | 6 | 2 | 0 | 0 | 382 | 129 | 38 | 76 | 15849 | 1353132 | 171275 | 0.72 |
| pin | 3 | 3 | 0 | 0 | 83 | 38 | 11 | 22 | 4042 | 309450 | 52179 | 0.20 |
| green | 10 | 2 | 3 | 0 | 1155 | 157 | 48 | 92 | 16484 | 1363797 | 222203 | 1.09 |
| red-missing | 1 | 0 | 0 | 0 | 46 | 33 | 8 | 16 | 3858 | 280450 | 23961 | 0.13 |
| refactor | 3 | 1 | 0 | 0 | 106 | 23 | 10 | 20 | 2306 | 247876 | 84641 | 0.26 |
| cover | 1 | 0 | 0 | 0 | 51 | 17 | 6 | 12 | 1995 | 157828 | 33660 | 0.12 |
| predicate | 1 | 0 | 0 | 0 | 12 | 10 | 3 | 6 | 467 | 77317 | 12495 | 0.04 |
| structural | 1 | 0 | 0 | 0 | 67 | 16 | 6 | 12 | 2210 | 175667 | 16026 | 0.08 |
| transform | 1 | 1 | 0 | 0 | 40 | 11 | 5 | 10 | 1083 | 121051 | 31127 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 10 | 3 | 0 | 1051 | 174 | 52 | 102 | 17322 | 1421968 | 260242 | 0.97 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 439 | 191 | 58 | 116 | 23475 | 1913697 | 290621 | 1.15 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 464 | 78 | 26 | 50 | 8456 | 750903 | 130355 | 0.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 1928 | 1.77 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a refactor deletes a frozen Go case's `t.Fatal` line without moving it anywhere, `rerecord-refactored` leaves the record and `check-earlier` for a later step still exits 1 naming the case: the weakening guard of #2626 holds, and with the guard removed this case goes red (a pin in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process, no production change) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 10 | 20 | 4065 | 311311 | 61736 | 0.23 | unknown | unknown | unknown | unknown |  |  | pin |
| After a refactor moves a frozen Go case's `t.Fatal` lines into a helper that the case calls, `rerecord-refactored` rewrites the case's record and `check-earlier` for a later step exits 0 (in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process) ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 201 | 58 | 112 | 21523 | 1768360 | 273405 | 1.19 | 2920 | 1/2 | 0/5 | structural-owed |  |  | already-satisfied |
| After a refactor moves a frozen case's `assert` or `require.` line into a helper that the case calls, in a non-Go test file, `rerecord-refactored` rewrites the case's record and `check-earlier` for a later step exits 0, so the fix is not Go-only (in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process) ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 108 | 36 | 72 | 11584 | 1082116 | 171605 | 0.77 | 839 | 1/2 | 1/5 | nothing-structural |  |  | full |
| After a refactor moves a frozen case's `t.Fatal` lines into a helper the case calls, and the verified-green commit's helper keeps them, a later commit that deletes one of those lines from the helper leaves the record and `check-earlier` for a later step still exits 1 naming the case; with only the case body inspected, or with the guard removed, this case goes red (in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process) ⟦criterion 3⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 93 | 31 | 62 | 11122 | 924781 | 140821 | 0.56 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After a refactor moves a frozen Go case's `t.Fatal` lines into a helper that the case calls, `rerecord-refactored` rewrites the case's record and `check-earlier` for a later step exits 0 (in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 9 | 0.10 |
| After a refactor moves a frozen case's `assert` or `require.` line into a helper that the case calls, in a non-Go test file, `rerecord-refactored` rewrites the case's record and `check-earlier` for a later step exits 0, so the fix is not Go-only (in skills/tdd/scripts/tests/py/test_tests_frozen_process.py: a git repo in tmp_path, a medium case marked process) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 97 | 0.16 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 8 | 27 | 33 | 28 | 19 | 24 | 22 | 9 | 1 | 30 | 26 | 3 | 26 | 19 | 16 | 19 | 19 | 24 | 19 | 0 | 6 | 30 | 22 | 25 | 0 | 26 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 6 | 7 | 3 | 4 | 24 | 5 | 5 | 5 | 6 | 4 | 5 | 5 | 6 | 7 | 6 | 6 | 8 | 6 | 3 | 4 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 4 | 5 | 5 | 3 | 5 | 5 | 6 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 5 | 4 | 4 | 5 |
| fast | 32 | 31 | 36 | 39 | 46 | 52 | 44 | 29 | 33 | 43 | 30 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 136 | 268 | 49253 | 4086568 | 681218 | 7.29 (estimate) |
