### 📊 Metrics — issue 1083

Wall time for the issue: 2341 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1091.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 904 | 12001 | 31072 | 0.14 |
| red | 9 | 4 | 0 | 0 | 196 | 171 | 50 | 98 | 17302 | 2153055 | 377250 | 3.15 |
| green | 8 | 4 | 0 | 0 | 436 | 228 | 73 | 138 | 25131 | 3266842 | 344607 | 3.18 |
| refactor | 8 | 4 | 0 | 0 | 189 | 105 | 33 | 62 | 10254 | 1196759 | 318510 | 2.32 |
| pin | 1 | 1 | 0 | 0 | 19 | 15 | 5 | 10 | 1485 | 201810 | 38832 | 0.21 |
| diff | 2 | 1 | 0 | 0 | 433 | 31 | 10 | 20 | 2888 | 404900 | 76510 | 0.58 |
| predicate | 3 | 0 | 0 | 0 | 53 | 45 | 10 | 20 | 3841 | 362481 | 113024 | 1.05 |
| structural | 1 | 0 | 0 | 0 | 15 | 12 | 3 | 6 | 1186 | 104494 | 37630 | 0.35 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 15 | 0 | 0 | 777 | 220 | 75 | 142 | 21993 | 2873018 | 576217 | 3.10 |
| developer | claude-opus-5-5 | 18 | 0 | 0 | 0 | 574 | 395 | 110 | 214 | 40998 | 4829324 | 761218 | 7.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-ledger.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 37 | 72 | 12393 | 1577373 | 245646 | 2.01 | 282 | unknown | 0/5 | nothing-left |  |  | full |
| tick-ledger.sh given a ledger path that does not exist exits 2, with one stderr line naming the path and no traceback ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 107 | 35 | 64 | 11237 | 1366521 | 243309 | 1.93 | 224 | unknown | 0/5 | nothing-left |  |  | full |
| clear-refactor-pending.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 119 | 40 | 76 | 12685 | 1704804 | 252967 | 2.10 | 251 | unknown | 0/5 | nothing-left |  |  | full |
| clear-refactor-pending.sh given a ledger path that does not exist exits 2, with one stderr line naming the path and no traceback ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 38 | 74 | 13395 | 1682916 | 251247 | 2.11 | 251 | unknown | 0/5 | structural-owed |  |  | full |
| On a readable ledger, tick-ledger.sh and clear-refactor-pending.sh still exit 3 when no step matches and 0 when they tick or clear one ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 11 | 22 | 4462 | 486852 | 86030 | 0.70 | unknown | unknown | unknown | unknown |  |  | pin |
| No case added or changed on this branch forces an unreadable ledger with permission bits (chmod, a read-only path) or a system location; each uses a directory or a missing path inside its own scratch tree ⟦diff-checked⟧ ⟦criterion 5⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 88 | 23 | 46 | 7915 | 871875 | 227164 | 1.98 | 451 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tick-ledger.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 51 | 0.60 |
| tick-ledger.sh given a ledger path that does not exist exits 2, with one stderr line naming the path and no traceback ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.56 |
| clear-refactor-pending.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 46 | 0.58 |
| clear-refactor-pending.sh given a ledger path that does not exist exits 2, with one stderr line naming the path and no traceback ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 49 | 0.58 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 368 | 0 |
| fast | 15 | 16 | 16 | 17 | 15 | 15 | 15 | 15 | 16 | 15 | 15 | 15 | 16 | 16 | 15 | 15 |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 185 | 356 | 62991 | 7702342 | 1337435 | 10.98 |
