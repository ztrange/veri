### 📊 Metrics — issue 775

Wall time for the issue: 4258 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/855.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 48 | 37 | 6 | 12 | 3423 | 229275 | 83444 | 0.78 |
| red | 13 | 6 | 0 | 0 | 944 | 491 | 121 | 232 | 43742 | 6468313 | 686039 | 7.66 |
| pin | 1 | 1 | 0 | 0 | 34 | 23 | 6 | 12 | 2032 | 274875 | 44707 | 0.45 |
| green | 9 | 3 | 0 | 1 | 1411 | 353 | 87 | 172 | 33988 | 4576200 | 404641 | 4.83 |
| refactor | 6 | 3 | 0 | 0 | 361 | 135 | 36 | 70 | 10766 | 1616361 | 262272 | 2.64 |
| diff | 2 | 1 | 0 | 0 | 252 | 105 | 15 | 28 | 7893 | 682909 | 96228 | 1.06 |
| predicate | 1 | 0 | 0 | 0 | 20 | 15 | 4 | 8 | 1220 | 164078 | 39833 | 0.38 |
| structural | 1 | 0 | 0 | 0 | 55 | 30 | 8 | 16 | 1761 | 377208 | 42172 | 0.45 |
| transform | 1 | 1 | 0 | 0 | 44 | 20 | 6 | 12 | 1784 | 269751 | 42313 | 0.43 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 17 | 16 | 1 | 0 | 1384 | 473 | 118 | 228 | 44772 | 5392387 | 755841 | 8.02 |
| developer | claude-opus-5-5 | 19 | 0 | 0 | 1 | 1785 | 736 | 171 | 334 | 61837 | 9266583 | 945808 | 10.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-issue-criterion.sh, when gh fails on the body edit with any non-zero status (1, 3 and 5 alike), exits 2 and the issue body is left unchanged ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 90 | 21 | 42 | 7941 | 1172082 | 102097 | 1.21 | unknown | unknown | unknown | unknown |  |  | pin |
| refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 233 | 69 | 134 | 22566 | 3545226 | 445953 | 4.73 | 416 | unknown | 0/5 | nothing-left |  |  | full |
| wait-ci.sh given a non-numeric slice or a non-numeric total exits 2 and names the bad argument on stderr, never 1 ⟦criterion 3⟧ | 12 | 5 | 0 | 1 | 0 | 0 | 404 | 97 | 186 | 35267 | 4848361 | 541645 | 6.01 | 1031 | unknown | 0/5 | nothing-left |  |  | full |
| workqueue.sh with a missing worker, a missing issue or a missing park reason exits 2 with its usage text on stderr and leaves no .tdd/workqueue.tmp.* file ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 275 | 63 | 124 | 24754 | 3370080 | 307964 | 3.63 | 755 | unknown | 1/5 | structural-owed |  |  | full |
| no assertion of a case the four scripts' existing suites already held is changed by this branch, except those the issue's 2026-10-04 amendment names (refactor-overflow.test.sh:299; the ("1", 1, 1, …) and ("1", 4, 4, …) rows of test_refactor_overflow.py; test_wait_ci.py:331-332; test_workqueue.py:276, :414 and :419), each changing only to its criterion's expected outcome — the exit code, and the stderr where the criterion names it ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 5⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 170 | 33 | 64 | 12658 | 1493946 | 220546 | 2.32 | 288 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 79 | 0.84 |
| wait-ci.sh given a non-numeric slice or a non-numeric total exits 2 and names the bad argument on stderr, never 1 ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 126 | 0.85 |
| workqueue.sh with a missing worker, a missing issue or a missing park reason exits 2 with its usage text on stderr and leaves no .tdd/workqueue.tmp.* file ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 156 | 0.95 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 42 | 41 | 50 | 47 | 47 | 52 | 52 | 48 | 42 | 16 | 17 | 17 | 48 | 1 | 18 | 18 | 65 | 19 | 19 |
| target | 2 | 3 | 2 | 47 | 17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 37 | 37 | 36 | 38 | 40 | 41 | 40 | 39 | 36 | 35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 289 | 562 | 106609 | 14658970 | 1701649 | 18.68 |
