### 📊 Metrics — issue 2814

Wall time for the issue: 6128 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2821.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.93 over 37 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87561 tokens, largest 146971 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87561 |
| 2 | $0.08 | 95814 |
| 3 | $0.04 | 98138 |
| 4 | $0.03 | 98809 |
| 5 | $0.02 | 99255 |
| 6 | $0.02 | 99592 |
| 7 | $0.02 | 99882 |
| 8 | $0.02 | 100222 |
| 9 | $0.03 | 100906 |
| 10 | $0.04 | 102948 |
| 11 | $0.03 | 104581 |
| 12 | $0.02 | 105056 |
| 13 | $0.11 | 116511 |
| 14 | $0.03 | 117484 |
| 15 | $0.04 | 119630 |
| 16 | $0.03 | 120670 |
| 17 | $0.04 | 122249 |
| 18 | $0.04 | 123723 |
| 19 | $0.05 | 127174 |
| 20 | $0.04 | 129134 |
| 21 | $0.04 | 130532 |
| 22 | $0.03 | 131484 |
| 23 | $0.04 | 133642 |
| 24 | $0.05 | 136410 |
| 25 | $0.04 | 138044 |
| 26 | $0.04 | 139422 |
| 27 | $0.03 | 140228 |
| 28 | $0.04 | 141598 |
| 29 | $0.03 | 142391 |
| 30 | $0.03 | 142779 |
| 31 | $0.03 | 143115 |
| 32 | $0.03 | 143494 |
| 33 | $0.03 | 144107 |
| 34 | $0.03 | 144675 |
| 35 | $0.04 | 145808 |
| 36 | $0.03 | 146396 |
| 37 | $0.03 | 146971 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 622 | 0 | 32079 | 0.09 |
| red | 3 | 1 | 0 | 0 | 139 | 49 | 14 | 28 | 6319 | 414724 | 80436 | 0.31 |
| green | 5 | 2 | 1 | 0 | 388 | 55 | 19 | 38 | 6189 | 553006 | 66210 | 0.28 |
| red-missing | 1 | 0 | 0 | 0 | 47 | 20 | 5 | 10 | 2424 | 155595 | 18676 | 0.09 |
| pin | 2 | 2 | 0 | 0 | 69 | 28 | 7 | 14 | 2669 | 194653 | 33799 | 0.13 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 3 | 4 | 446 | 49165 | 16645 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 390 | 79 | 24 | 48 | 8690 | 663946 | 117664 | 0.45 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 268 | 82 | 25 | 48 | 9979 | 703197 | 130181 | 0.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 388 | 0.28 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A mutations record whose command begins with a `timed-test-run.sh` path that no longer exists is replayed through the current skill's `timed-test-run.sh`, and a pin that still catches its mutant is not reported "needs a look" ⟦criterion 1⟧ | 10 | 4 | 1 | 0 | 0 | 0 | 120 | 39 | 76 | 13768 | 1091006 | 175290 | 0.69 | 844 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| A mutations record whose command still cannot run prints "needs a look" as today, whether or not its command begins with a `timed-test-run.sh` path that no longer exists ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 9 | 18 | 4279 | 276137 | 40476 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A mutations record whose command begins with a `timed-test-run.sh` path that no longer exists is replayed through the current skill's `timed-test-run.sh`, and a pin that still catches its mutant is not reported "needs a look" ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 8 | 11 | 11 | 10 | 10 |  |  |  |
| fast | 42 | 45 | 36 | 34 | 34 |  |  |  |  |
| target | 10 | 7 | 8 | 7 | 7 | 5 | 8 | 7 | 7 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 49 | 96 | 18669 | 1367143 | 247845 | 2.87 (estimate) |
