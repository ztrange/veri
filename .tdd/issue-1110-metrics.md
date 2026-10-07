### 📊 Metrics — issue 1110

Wall time for the issue: 5568 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1117.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 57 | 50 | 7 | 14 | 4704 | 283548 | 90477 | 0.87 |
| red | 13 | 6 | 0 | 0 | 459 | 371 | 75 | 148 | 34930 | 3653926 | 657917 | 6.69 |
| green | 12 | 6 | 0 | 0 | 1049 | 315 | 83 | 160 | 29585 | 3818042 | 535963 | 5.64 |
| refactor | 12 | 6 | 0 | 0 | 604 | 217 | 54 | 108 | 18649 | 2374392 | 536764 | 5.14 |
| pin | 1 | 1 | 0 | 0 | 22 | 15 | 3 | 6 | 1367 | 114299 | 41552 | 0.38 |
| diff | 4 | 2 | 0 | 0 | 450 | 159 | 34 | 60 | 10308 | 1432969 | 179949 | 1.93 |
| predicate | 4 | 0 | 0 | 0 | 105 | 84 | 13 | 26 | 5535 | 515503 | 166344 | 1.54 |
| structural | 1 | 0 | 0 | 0 | 52 | 42 | 10 | 18 | 4531 | 457269 | 47198 | 0.56 |
| transform | 1 | 1 | 0 | 0 | 38 | 26 | 6 | 12 | 2791 | 272470 | 43068 | 0.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 24 | 23 | 1 | 0 | 1542 | 623 | 142 | 282 | 55680 | 6494110 | 1067594 | 10.95 |
| developer | claude-opus-5-5 | 26 | 0 | 0 | 0 | 1294 | 656 | 143 | 270 | 56720 | 6428308 | 1231638 | 12.27 |

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
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| clear-refactor-pending.sh exits 2 with no traceback, leaving the ledger byte-identical and no backup or temp file beside it, when opening the ledger for writing fails — replacing the existing pytest case test_main_raises_rather_than_returning_a_code_on_a_refused_write_back_leaving_the_ledger_byte_identical, which pins the traceback this issue removes ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 140 | 34 | 66 | 12354 | 1519335 | 268735 | 2.70 | 436 | unknown | 0/5 | structural-owed |  |  | full |
| clear-refactor-pending.sh exits 2 with no traceback, leaving the ledger byte-identical and no backup or temp file beside it, when every write it attempts fails, the restore of its backup over the ledger included ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 32 | 62 | 13247 | 1435920 | 277804 | 2.77 | 437 | unknown | 0/5 | nothing-structural |  |  | full |
| clear-refactor-pending.sh exits 2 with no traceback and leaves no backup beside the ledger when removing its backup fails, after a failed open of the ledger for writing or after a failed restore of the backup ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 173 | 37 | 74 | 16383 | 1797068 | 285554 | 2.97 | 438 | unknown | 0/5 | nothing-structural |  |  | full |
| clear-refactor-pending.sh exits 2 with no traceback and leaves no backup beside the ledger when removing its backup fails after the cleared ledger was written, or after a failed write whose old contents were written back ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 38 | 74 | 15391 | 1829589 | 294702 | 3.03 | 464 | unknown | 0/5 | nothing-structural |  |  | full |
| tick-ledger.sh exits 2 with no traceback, leaving the ledger byte-identical and no temp file beside it, when putting the ticked ledger in place fails and removing its temporary file beside the ledger fails too ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 34 | 68 | 13041 | 1622559 | 287684 | 2.89 | 408 | unknown | 0/5 | nothing-structural |  |  | full |
| tick-ledger.sh, given a ledger path that is a symlink, ticks the step in the link's target and leaves the link a symlink, with no temp file left beside either ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 31 | 62 | 10406 | 1405409 | 265394 | 2.61 | 379 | unknown | 0/5 | nothing-structural |  |  | full |
| tick-ledger.sh, given a ledger path that is a dangling symlink, exits 2 with no traceback, leaving the link a link and no temp file beside it ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 9 | 16 | 3709 | 350779 | 92323 | 0.88 | unknown | unknown | unknown | unknown |  |  | pin |
| no case this branch adds forces a ledger write failure with permission bits or a system path: each forces it by the path's type or shape inside its scratch tree, or by faking the call at the process boundary in tests/py/ ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 81 | 18 | 32 | 5468 | 780339 | 93352 | 1.01 | 271 | n/a | n/a | n/a |  |  | full |
| the Exit lines of tick-ledger.sh and clear-refactor-pending.sh name a ledger that could not be written under exit 2, not exit 1 ⟦diff-checked⟧ | 8 | 2 | 0 | 0 | 0 | 0 | 230 | 45 | 84 | 17697 | 1897872 | 343207 | 3.48 | 225 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| clear-refactor-pending.sh exits 2 with no traceback, leaving the ledger byte-identical and no backup or temp file beside it, when opening the ledger for writing fails — replacing the existing pytest case test_main_raises_rather_than_returning_a_code_on_a_refused_write_back_leaving_the_ledger_byte_identical, which pins the traceback this issue removes ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 99 | 0.84 |
| clear-refactor-pending.sh exits 2 with no traceback, leaving the ledger byte-identical and no backup or temp file beside it, when every write it attempts fails, the restore of its backup over the ledger included ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 107 | 0.87 |
| clear-refactor-pending.sh exits 2 with no traceback and leaves no backup beside the ledger when removing its backup fails, after a failed open of the ledger for writing or after a failed restore of the backup ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 96 | 0.88 |
| clear-refactor-pending.sh exits 2 with no traceback and leaves no backup beside the ledger when removing its backup fails after the cleared ledger was written, or after a failed write whose old contents were written back ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 105 | 0.86 |
| tick-ledger.sh exits 2 with no traceback, leaving the ledger byte-identical and no temp file beside it, when putting the ticked ledger in place fails and removing its temporary file beside the ledger fails too ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 103 | 0.89 |
| tick-ledger.sh, given a ledger path that is a symlink, ticks the step in the link's target and leaves the link a symlink, with no temp file left beside either ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 94 | 0.80 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 0 | 1 | 1 | 0 | 3 | 1 | 0 | 0 | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 2 | 1 | 19 | 3 | 1 | 1 | 1 | 0 | 9 | 1 | 4 | 0 | 2 | 3 | 2 |
| fast | 54 | 53 | 52 | 53 | 56 | 52 | 48 | 47 | 50 | 51 | 52 | 56 | 50 | 49 | 49 | 49 | 49 | 52 | 56 | 54 | 50 | 50 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 285 | 552 | 112400 | 12922418 | 2299232 | 23.23 |
