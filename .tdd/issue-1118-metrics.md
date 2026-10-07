### 📊 Metrics — issue 1118

Wall time for the issue: 4078 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1135.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 18 | 2 | 4 | 1787 | 62845 | 42319 | 0.39 |
| red | 6 | 3 | 0 | 0 | 199 | 162 | 39 | 76 | 14612 | 1879122 | 284005 | 2.94 |
| green | 6 | 3 | 0 | 0 | 516 | 152 | 42 | 84 | 13954 | 1974322 | 260348 | 2.76 |
| refactor | 6 | 3 | 0 | 0 | 298 | 101 | 29 | 58 | 9477 | 1285541 | 266933 | 2.58 |
| diff | 4 | 2 | 0 | 0 | 442 | 109 | 29 | 58 | 9399 | 1370002 | 173463 | 1.85 |
| predicate | 1 | 0 | 0 | 0 | 18 | 13 | 3 | 6 | 1205 | 116012 | 41966 | 0.38 |
| structural | 1 | 0 | 0 | 0 | 19 | 12 | 3 | 6 | 1190 | 114588 | 40239 | 0.37 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 12 | 12 | 0 | 0 | 858 | 296 | 74 | 148 | 27438 | 3391521 | 520755 | 5.39 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 657 | 271 | 73 | 144 | 24186 | 3410911 | 588518 | 5.87 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-ledger.sh exits 2 with one `tick-ledger.sh: <path>: <reason>` stderr line and no traceback, writing nothing, when reading the ledger fails with an OSError other than a missing file or a directory — a ledger path running through a regular file ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 140 | 36 | 72 | 12229 | 1676733 | 263547 | 2.69 | 443 | unknown | 0/5 | nothing-structural |  |  | full |
| tick-ledger.sh exits 2 with one `tick-ledger.sh: <path>: <reason>` stderr line and no traceback, leaving the ledger byte-identical, when the ledger holds bytes that do not decode under a UTF-8 locale ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 137 | 35 | 70 | 13567 | 1681780 | 279215 | 2.84 | 408 | unknown | 0/5 | nothing-structural |  |  | full |
| clear-refactor-pending.sh exits 2 with one `clear-refactor-pending.sh: <path>: <reason>` stderr line and no traceback, writing nothing, when reading the ledger fails with an OSError other than a missing file or a directory — a ledger path running through a regular file ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 39 | 76 | 12247 | 1780472 | 268524 | 2.75 | 405 | unknown | 0/5 | structural-owed |  |  | full |
| no case this branch adds forces a ledger read failure with permission bits or a system path: each forces it by the path's type or shape inside its scratch tree (a path through a regular file, a symlink loop, undecodable bytes), or by faking the read at the process boundary in tests/py/ ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 18 | 36 | 5639 | 879197 | 88596 | 1.00 | 270 | n/a | n/a | n/a |  |  | full |
| the Exit lines of tick-ledger.sh and clear-refactor-pending.sh name a ledger that could not be read under exit 2, not exit 1 ⟦diff-checked⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 71 | 17 | 34 | 6155 | 721405 | 167072 | 1.60 | 228 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tick-ledger.sh exits 2 with one `tick-ledger.sh: <path>: <reason>` stderr line and no traceback, writing nothing, when reading the ledger fails with an OSError other than a missing file or a directory — a ledger path running through a regular file ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 115 | 0.87 |
| tick-ledger.sh exits 2 with one `tick-ledger.sh: <path>: <reason>` stderr line and no traceback, leaving the ledger byte-identical, when the ledger holds bytes that do not decode under a UTF-8 locale ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 92 | 0.85 |
| clear-refactor-pending.sh exits 2 with one `clear-refactor-pending.sh: <path>: <reason>` stderr line and no traceback, writing nothing, when reading the ledger fails with an OSError other than a missing file or a directory — a ledger path running through a regular file ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 91 | 0.86 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 2 | 2 | 3 | 1 | 0 | 1 | 2 | 2 | 2 | 1 | 1 | 0 | 2 | 6 | 2 | 0 | 17 | 18 | 0 | 1 | 1 | 1 | 0 | 2 | 0 | 1 | 1 | 2 |
| fast | 53 | 49 | 61 | 49 | 54 | 50 | 49 | 52 | 49 | 50 | 51 | 48 | 48 | 49 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 147 | 292 | 51624 | 6802432 | 1109273 | 11.27 |
