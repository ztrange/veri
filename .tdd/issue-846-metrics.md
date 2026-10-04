### 📊 Metrics — issue 846

Wall time for the issue: 1546 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 8 planned.
Outcome: the run bailed — step-too-big, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 16 | 2 | 4 | 1532 | 62973 | 41812 | 0.38 |
| red | 5 | 1 | 1 | 0 | 345 | 295 | 46 | 92 | 21229 | 2532083 | 249274 | 2.93 |
| pin | 1 | 1 | 0 | 0 | 39 | 28 | 6 | 12 | 2630 | 275208 | 44162 | 0.46 |
| green | 6 | 0 | 3 | 0 | 915 | 259 | 50 | 98 | 22989 | 2575295 | 257892 | 3.04 |
| exhausted | 1 | 0 | 0 | 0 | 33 | 29 | 6 | 12 | 2408 | 283237 | 46350 | 0.48 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 7 | 3 | 4 | 0 | 737 | 303 | 47 | 92 | 22574 | 2287809 | 287096 | 3.21 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 614 | 324 | 63 | 126 | 28214 | 3440987 | 352394 | 4.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 210 | 1.56 | 135 | 1.36 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 915 | 3.04 |
| exhausted | 0 | 0.00 | 33 | 0.48 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| status.test.sh's "exits 2 on a failure veri/status.py turns into exit 2" case forces the ledger read to fail by a means permission bits play no part in (e.g. `$run/.tdd/issue-9.md` made a directory, so the read raises IsADirectoryError), with no `chmod` and no skip when `$EUID` is 0, and asserts exit 2 with a non-empty stderr instead of the literal `PermissionError` ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 205 | 31 | 62 | 12788 | 1532516 | 182746 | 2.02 | unknown | 1/2 | unknown | unknown |  |  | pin |
| A guard suite fails the run naming `<suite>:<line>` for a suite that forces a read or write failure through permission bits by `chmod 000`, `chmod a-r`, `chmod u-w` or `chmod -w`, and passes on today's tree ⟦criterion 2⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 406 | 77 | 152 | 36468 | 4133307 | 414932 | 4.88 | unknown | 2/2 | unknown | unknown |  | exhausted | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 7 | 2 | 0 | 1 | 0 | 0 | 2 | 36 | 1 | 8 | 2 | 58 | 1 | 1 | 39 | 0 | 2 | 146 | 120 |
| target | 3 | 3 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 39 | 36 | 34 | 34 | 33 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 110 | 218 | 50788 | 5728796 | 639490 | 7.28 |
