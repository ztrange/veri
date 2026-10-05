### 📊 Metrics — issue 894

Wall time for the issue: 1876 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/905.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 10 | 2 | 4 | 1088 | 53180 | 35333 | 0.16 |
| red | 4 | 1 | 0 | 0 | 346 | 205 | 43 | 80 | 18392 | 2124201 | 202050 | 2.24 |
| green | 2 | 1 | 0 | 0 | 162 | 59 | 19 | 38 | 4911 | 893091 | 81678 | 0.77 |
| refactor | 2 | 1 | 0 | 0 | 74 | 36 | 10 | 20 | 2900 | 401380 | 76595 | 0.59 |
| pin | 2 | 2 | 0 | 0 | 108 | 26 | 8 | 16 | 2688 | 295224 | 73834 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 267 | 81 | 24 | 48 | 8424 | 891688 | 222754 | 1.15 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 434 | 255 | 58 | 110 | 21555 | 2875388 | 246736 | 2.98 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| wait-ci.sh called on a draft PR whose checks are pending records no .tdd/ci-deadline-<sha> file and exits 3 when its slice runs out ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 44 | 86 | 14220 | 1977065 | 251774 | 2.19 | 437 | unknown | 0/5 | nothing-left |  |  | full |
| after a draft call left no deadline, a call on the same PR once it is ready with the same head sha records the deadline counted from that call, and checks turning green within it exit 0 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 17 | 32 | 7767 | 813259 | 91792 | 0.89 | unknown | unknown | unknown | unknown |  |  | pin |
| a ready PR whose checks stay pending past a deadline already recorded for its head still exits 2 ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 19 | 36 | 6904 | 923572 | 90591 | 0.89 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| wait-ci.sh called on a draft PR whose checks are pending records no .tdd/ci-deadline-<sha> file and exits 3 when its slice runs out ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 74 | 0.59 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 17 | 18 | 0 | 18 | 19 | 20 |
| fast | 16 | 16 | 15 |  |  |  |  |
| target | 18 | 19 | 19 | 19 | 20 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 82 | 158 | 29979 | 3767076 | 469490 | 4.13 |
