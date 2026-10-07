### 📊 Metrics — issue 1125

Wall time for the issue: 7010 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1139.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 18 | 2 | 4 | 1812 | 63436 | 42446 | 0.39 |
| red | 9 | 4 | 0 | 0 | 362 | 298 | 66 | 128 | 28389 | 3411007 | 481078 | 5.10 |
| green | 8 | 4 | 0 | 0 | 739 | 261 | 62 | 118 | 21847 | 2900122 | 367176 | 3.95 |
| refactor | 8 | 4 | 0 | 0 | 426 | 166 | 46 | 90 | 16748 | 2143592 | 370489 | 3.73 |
| pin | 1 | 1 | 0 | 0 | 36 | 29 | 7 | 14 | 2679 | 336439 | 45323 | 0.48 |
| rebase | 3 | 1 | 0 | 0 | 2744 | 91 | 28 | 56 | 8669 | 1485153 | 121951 | 1.45 |
| predicate | 2 | 0 | 0 | 0 | 58 | 49 | 6 | 12 | 2607 | 231075 | 82090 | 0.76 |
| structural | 1 | 0 | 0 | 0 | 117 | 107 | 8 | 16 | 5993 | 413724 | 48993 | 0.59 |
| transform | 1 | 0 | 1 | 0 | 27 | 21 | 4 | 8 | 1871 | 166919 | 42147 | 0.41 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 17 | 15 | 1 | 0 | 2757 | 506 | 117 | 230 | 44601 | 5547991 | 743505 | 7.95 |
| developer | claude-opus-5-5 | 17 | 0 | 0 | 0 | 1775 | 534 | 112 | 216 | 46014 | 5603476 | 858188 | 8.91 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 27 | 0.41 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| clear-refactor-pending.sh: when the in-place open really truncates the ledger, the write fails, the write-back fails and restoring the backup fails, the run exits 2 with no traceback, keeps the backup beside the ledger holding the ledger's old bytes, and names that backup in exactly one `clear-refactor-pending.sh: …` stderr line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 212 | 40 | 76 | 16760 | 1854587 | 287206 | 3.00 | 496 | unknown | 0/5 | nothing-left |  |  | full |
| clear-refactor-pending.sh: when the in-place write fails after leaving more bytes in the ledger than its old contents hold, the write-back restores exactly the old bytes (no trailing remnant), the run exits 2 with no traceback and nothing is left beside the ledger ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 154 | 37 | 74 | 14429 | 1841829 | 289427 | 2.97 | 397 | unknown | 0/5 | nothing-left |  |  | full |
| clear-refactor-pending.sh: when the in-place open really truncates the ledger, the write fails, the write-back fails and restoring the backup succeeds, the run exits 2 with no traceback, the ledger holds its old bytes and nothing is left beside it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 17 | 32 | 7039 | 914987 | 113382 | 1.23 | unknown | unknown | unknown | unknown |  |  | pin |
| clear-refactor-pending.sh: when removing the backup raises without deleting it, the run exits 2 with no traceback and names the leftover backup in exactly one `clear-refactor-pending.sh: …` stderr line, so nothing is left beside the ledger unannounced ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 161 | 44 | 84 | 16587 | 2103397 | 295365 | 3.12 | 404 | unknown | 1/5 | structural-owed |  |  | full |
| tick-ledger.sh: when putting the ticked ledger in place fails and removing its temporary file raises without deleting it, the run exits 2 with no traceback, the ledger is byte-identical, and the leftover temporary file is named in exactly one `tick-ledger.sh: …` stderr line ⟦criterion 2⟧ | 13 | 4 | 1 | 0 | 0 | 1 | 422 | 89 | 176 | 33988 | 4373231 | 573867 | 6.15 | 399 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| clear-refactor-pending.sh: when the in-place open really truncates the ledger, the write fails, the write-back fails and restoring the backup fails, the run exits 2 with no traceback, keeps the backup beside the ledger holding the ledger's old bytes, and names that backup in exactly one `clear-refactor-pending.sh: …` stderr line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 104 | 0.88 |
| clear-refactor-pending.sh: when the in-place write fails after leaving more bytes in the ledger than its old contents hold, the write-back restores exactly the old bytes (no trailing remnant), the run exits 2 with no traceback and nothing is left beside the ledger ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 88 | 0.86 |
| clear-refactor-pending.sh: when removing the backup raises without deleting it, the run exits 2 with no traceback and names the leftover backup in exactly one `clear-refactor-pending.sh: …` stderr line, so nothing is left beside the ledger unannounced ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 122 | 1.00 |
| tick-ledger.sh: when putting the ticked ledger in place fails and removing its temporary file raises without deleting it, the run exits 2 with no traceback, the ledger is byte-identical, and the leftover temporary file is named in exactly one `tick-ledger.sh: …` stderr line ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 112 | 0.99 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 0 | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 0 | 4 | 0 | 1 | 0 | 1 | 1 | 1 | 2 | 1 | 2 | 2 | 3 |
| fast | 51 | 50 | 51 | 48 | 48 | 48 | 47 | 49 | 49 | 48 | 54 | 50 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 928 | 932 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 229 | 446 | 90615 | 11151467 | 1601693 | 16.86 |
