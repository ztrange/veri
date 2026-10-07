### 📊 Metrics — issue 1116

Wall time for the issue: 2448 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1121.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 16 | 3 | 6 | 1448 | 115670 | 41903 | 0.39 |
| red | 4 | 2 | 0 | 0 | 143 | 117 | 25 | 50 | 9895 | 1222807 | 194500 | 2.00 |
| green | 4 | 2 | 0 | 0 | 404 | 156 | 35 | 68 | 12344 | 1728911 | 190108 | 2.11 |
| refactor | 4 | 2 | 0 | 0 | 286 | 152 | 30 | 60 | 12595 | 1560720 | 190044 | 2.08 |
| predicate | 3 | 0 | 0 | 0 | 47 | 30 | 10 | 20 | 2666 | 398864 | 123739 | 1.12 |
| structural | 1 | 0 | 0 | 0 | 36 | 27 | 7 | 14 | 1863 | 328458 | 42382 | 0.44 |
| transform | 1 | 1 | 0 | 0 | 41 | 34 | 5 | 10 | 2246 | 213925 | 42671 | 0.43 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 8 | 8 | 0 | 0 | 504 | 232 | 51 | 102 | 18698 | 2409249 | 357467 | 3.72 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 476 | 300 | 64 | 126 | 24359 | 3160106 | 467880 | 4.86 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| criterion-finished.sh <k>, for any k, on a ledger in which any step line carries two criterion tags exits 2 with a stderr line naming that step's text and saying one step serves one criterion, while ledgers with at most one tag per step keep their exit codes ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 39 | 78 | 14944 | 1886117 | 280012 | 2.92 | 475 | unknown | 0/5 | structural-owed |  |  | full |
| add-ledger-step.sh on a ledger in which any step line carries two criterion tags — the anchor or another step — exits 2 with a stderr line naming that step's text and saying one step serves one criterion, and leaves the ledger file byte-for-byte unchanged ⟦criterion 1⟧ | 11 | 4 | 0 | 0 | 0 | 0 | 340 | 73 | 144 | 26665 | 3567568 | 503432 | 5.27 | 534 | unknown | 2/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| criterion-finished.sh <k>, for any k, on a ledger in which any step line carries two criterion tags exits 2 with a stderr line naming that step's text and saying one step serves one criterion, while ledgers with at most one tag per step keep their exit codes ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 110 | 0.87 |
| add-ledger-step.sh on a ledger in which any step line carries two criterion tags — the anchor or another step — exits 2 with a stderr line naming that step's text and saying one step serves one criterion, and leaves the ledger file byte-for-byte unchanged ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 176 | 1.21 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 7 | 2 | 1 | 1 | 1 | 2 | 0 | 3 | 1 | 4 | 3 | 1 | 2 |
| fast | 50 | 53 | 54 | 51 | 49 | 48 |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 115 | 228 | 43057 | 5569355 | 825347 | 8.58 |
