### 📊 Metrics — issue 1198

Wall time for the issue: 4695 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1222.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1132 | 12385 | 31132 | 0.14 |
| red | 15 | 7 | 0 | 0 | 456 | 391 | 104 | 198 | 42865 | 4880189 | 706532 | 6.29 |
| green | 14 | 7 | 0 | 0 | 1183 | 348 | 112 | 220 | 36701 | 5124873 | 598511 | 5.29 |
| refactor | 14 | 7 | 0 | 0 | 802 | 279 | 82 | 160 | 28783 | 3505999 | 572707 | 4.68 |
| pin | 1 | 1 | 0 | 0 | 19 | 14 | 5 | 10 | 1669 | 207632 | 40084 | 0.22 |
| predicate | 9 | 0 | 0 | 0 | 162 | 134 | 37 | 74 | 11320 | 1403204 | 337583 | 3.21 |
| structural | 4 | 0 | 0 | 0 | 282 | 136 | 36 | 72 | 11847 | 1704381 | 174254 | 1.97 |
| transform | 4 | 3 | 1 | 0 | 167 | 41 | 19 | 38 | 5003 | 749485 | 146764 | 0.79 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 27 | 26 | 1 | 0 | 1299 | 374 | 137 | 272 | 43582 | 5573898 | 1037418 | 5.70 |
| developer | claude-opus-5-5 | 35 | 0 | 0 | 0 | 1782 | 977 | 259 | 502 | 95738 | 12014250 | 1570149 | 16.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 167 | 0.79 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A `VERI_HEARTBEAT` with leading zeros is read as decimal: `010` is a 10-second silence window, not an 8-second one, and `08` is an 8-second window that fires rather than an arithmetic error that never kills ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 41 | 82 | 15812 | 2032793 | 277261 | 2.41 | 403 | unknown | 0/5 | structural-owed |  |  | full |
| A `VERI_TIMEOUT` with leading zeros is read as decimal: `010` is a 10-second hard cap, not 8, and `08` is an 8-second cap that fires rather than an arithmetic error that never kills ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 142 | 42 | 82 | 14765 | 1909531 | 262940 | 2.26 | 384 | unknown | 1/5 | structural-owed |  |  | full |
| A settled `.tdd/issue-<n>-timeout` holding a value with leading zeros (`010`) is read as a decimal hard cap of 10 seconds, not 8 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 16 | 32 | 7335 | 793667 | 91034 | 0.86 | unknown | unknown | unknown | unknown |  |  | pin |
| A `VERI_STUCK_RETRIES` with leading zeros is read as decimal: `08` allows exactly 8 retries after killed-stuck and then reports killed-stuck (exit 2), never retrying without end ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 34 | 66 | 12331 | 1470285 | 256299 | 2.08 | 328 | unknown | 0/5 | structural-owed |  |  | full |
| A `VERI_HEARTBEAT` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_HEARTBEAT is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 42 | 80 | 15062 | 1883884 | 263126 | 2.26 | 343 | unknown | 0/5 | structural-owed |  |  | full |
| A `VERI_TIMEOUT` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_TIMEOUT is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 42 | 80 | 14412 | 1821826 | 254418 | 2.17 | 376 | unknown | 1/5 | structural-owed |  |  | full |
| A settled `.tdd/issue-<n>-timeout` holding a value that is not a non-negative decimal integer (`abc`, `1.5`) is refused with exit 2 before the leaf is launched, stderr `supervise: <settled file path> is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 42 | 80 | 14870 | 1809468 | 252229 | 2.15 | 420 | unknown | 1/5 | nothing-structural |  |  | full |
| A `VERI_STUCK_RETRIES` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_STUCK_RETRIES is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 23 | 6 | 1 | 0 | 0 | 0 | 465 | 136 | 270 | 43601 | 5854309 | 919128 | 8.24 | 397 | unknown | 1/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A `VERI_HEARTBEAT` with leading zeros is read as decimal: `010` is a 10-second silence window, not an 8-second one, and `08` is an 8-second window that fires rather than an arithmetic error that never kills ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 92 | 0.62 |
| A `VERI_TIMEOUT` with leading zeros is read as decimal: `010` is a 10-second hard cap, not 8, and `08` is an 8-second cap that fires rather than an arithmetic error that never kills ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 127 | 0.68 |
| A `VERI_STUCK_RETRIES` with leading zeros is read as decimal: `08` allows exactly 8 retries after killed-stuck and then reports killed-stuck (exit 2), never retrying without end ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 56 | 0.57 |
| A `VERI_HEARTBEAT` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_HEARTBEAT is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 84 | 0.60 |
| A `VERI_TIMEOUT` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_TIMEOUT is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 138 | 0.73 |
| A settled `.tdd/issue-<n>-timeout` holding a value that is not a non-negative decimal integer (`abc`, `1.5`) is refused with exit 2 before the leaf is launched, stderr `supervise: <settled file path> is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 158 | 0.68 |
| A `VERI_STUCK_RETRIES` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_STUCK_RETRIES is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 147 | 0.80 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 3/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 27 | 28 | 0 | 1 | 27 | 27 | 28 | 26 | 1 | 1 | 1 | 1 | 25 | 26 | 0 | 0 | 1 | 0 | 1 | 25 | 26 | 26 | 1 | 1 | 26 | 0 | 0 | 26 | 2 | 25 | 28 | 1 | 1 | 1 | 27 | 0 | 29 | 26 | 28 | 0 | 1 | 28 | 0 | 0 | 27 | 1 | 0 | 1 | 24 | 0 | 0 | 0 | 25 | 2 | 53 | 27 | 0 | 29 | 27 | 29 | 28 | 29 |
| fast | 25 | 27 | 26 | 25 | 26 | 26 | 26 | 25 | 26 | 25 | 26 | 25 | 25 | 26 | 27 | 25 | 26 | 26 | 27 | 26 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 396 | 774 | 139320 | 17588148 | 2607567 | 22.58 |
