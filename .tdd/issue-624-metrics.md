### 📊 Metrics — issue 624

Wall time for the issue: 2661 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/668.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 2 | 4 | 1037 | 59227 | 42618 | 0.37 |
| red | 12 | 4 | 0 | 0 | 414 | 328 | 95 | 184 | 29214 | 4312944 | 506711 | 5.50 |
| green | 8 | 4 | 0 | 0 | 475 | 222 | 59 | 116 | 18204 | 2598583 | 325713 | 3.49 |
| refactor | 8 | 4 | 0 | 0 | 302 | 137 | 37 | 72 | 11951 | 1485603 | 319234 | 3.09 |
| pin | 4 | 4 | 0 | 0 | 84 | 54 | 13 | 26 | 4997 | 479999 | 153831 | 1.43 |
| structural | 1 | 0 | 0 | 0 | 19 | 12 | 4 | 8 | 1035 | 157897 | 38221 | 0.36 |
| transform | 1 | 1 | 0 | 0 | 30 | 19 | 5 | 10 | 1800 | 203067 | 37911 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 18 | 18 | 0 | 0 | 711 | 363 | 97 | 190 | 33473 | 4002406 | 717393 | 7.21 |
| developer | claude-opus-5-5 | 17 | 0 | 0 | 0 | 628 | 419 | 118 | 230 | 34765 | 5294914 | 706846 | 7.41 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| given a log whose result record carries `IMPL_PATH:` and `SUITE:` lines, followed by a later result record carrying neither, `extract-result.sh` prints the earlier record's text and exits 0 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 162 | 36 | 70 | 11782 | 1532025 | 245656 | 2.51 | 358 | unknown | 0/5 | structural-owed |  |  | full |
| given a log whose result record carries `SPLIT:` lines, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 43 | 82 | 12362 | 1861165 | 245215 | 2.58 | 326 | unknown | 0/5 | structural-owed |  |  | full |
| given a log whose result record carries a `TEST_PATH:` line, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 126 | 38 | 74 | 11663 | 1633674 | 244301 | 2.51 | 313 | unknown | 0/5 | structural-owed |  |  | full |
| given a log whose result record carries only a `SUITE:` line, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 130 | 38 | 74 | 11872 | 1624874 | 241842 | 2.50 | 347 | unknown | 0/5 | structural-owed |  |  | full |
| given two result records that both carry a report line, `extract-result.sh` prints the later one ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 12 | 24 | 3937 | 541928 | 81598 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| given result records none of which carries a report line or a `VERDICT:` line, `extract-result.sh` prints the last record's text ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 11 | 22 | 3712 | 488989 | 81847 | 0.83 | unknown | unknown | unknown | unknown |  |  | pin |
| a result record carrying a `VERDICT:` line, followed by a later record without one, still yields the `VERDICT:` record ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 11 | 22 | 3813 | 487728 | 81137 | 0.82 | unknown | unknown | unknown | unknown |  |  | pin |
| input containing no result record is passed through to stdout unchanged ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 15 | 30 | 5225 | 706746 | 83893 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| given a log whose result record carries `IMPL_PATH:` and `SUITE:` lines, followed by a later result record carrying neither, `extract-result.sh` prints the earlier record's text and exits 0 ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 75 | 0.78 |
| given a log whose result record carries `SPLIT:` lines, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 68 | 0.77 |
| given a log whose result record carries a `TEST_PATH:` line, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 68 | 0.78 |
| given a log whose result record carries only a `SUITE:` line, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 91 | 0.76 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 2 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 2 | 2 |
| fast | 24 | 23 | 24 | 23 | 22 | 23 | 21 | 23 | 23 | 24 | 25 | 24 | 24 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 215 | 420 | 68238 | 9297320 | 1424239 | 14.62 |
