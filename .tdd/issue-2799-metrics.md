### 📊 Metrics — issue 2799

Wall time for the issue: 1643 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2801.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.67 over 29 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87299 tokens, largest 144724 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87299 |
| 2 | $0.08 | 95175 |
| 3 | $0.04 | 97614 |
| 4 | $0.03 | 98341 |
| 5 | $0.02 | 98813 |
| 6 | $0.02 | 99141 |
| 7 | $0.02 | 99421 |
| 8 | $0.03 | 101183 |
| 9 | $0.03 | 102586 |
| 10 | $0.02 | 103061 |
| 11 | $0.04 | 104886 |
| 12 | $0.03 | 105712 |
| 13 | $0.03 | 106899 |
| 14 | $0.04 | 108799 |
| 15 | $0.03 | 109682 |
| 16 | $0.09 | 117800 |
| 17 | $0.04 | 119793 |
| 18 | $0.04 | 121733 |
| 19 | $0.05 | 125252 |
| 20 | $0.04 | 126810 |
| 21 | $0.04 | 128858 |
| 22 | $0.03 | 129929 |
| 23 | $0.04 | 131649 |
| 24 | $0.10 | 140480 |
| 25 | $0.04 | 141848 |
| 26 | $0.04 | 143058 |
| 27 | $0.03 | 143426 |
| 28 | $0.03 | 144150 |
| 29 | $0.03 | 144724 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 606 | 0 | 31397 | 0.08 |
| red | 4 | 1 | 0 | 0 | 116 | 55 | 17 | 34 | 6396 | 522822 | 108064 | 0.39 |
| green | 5 | 1 | 1 | 0 | 326 | 65 | 22 | 44 | 6780 | 607615 | 98342 | 0.49 |
| pin | 2 | 2 | 0 | 0 | 40 | 18 | 6 | 12 | 2138 | 154539 | 29125 | 0.11 |
| refactor | 1 | 0 | 0 | 0 | 6 | 2 | 2 | 4 | 149 | 48457 | 13634 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 250 | 55 | 19 | 38 | 5901 | 483127 | 106249 | 0.37 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 246 | 90 | 29 | 58 | 10168 | 850306 | 174313 | 0.74 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 326 | 0.49 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tests-frozen.sh record` on a `_test.go` file holding `func TestX(t *testing.T)` records it as case `TestX` ⟦criterion 1⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 109 | 38 | 76 | 11632 | 1062698 | 212869 | 0.87 | 668 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| Editing the body of a recorded Go test function `func TestX(t *testing.T)` makes `tests-frozen.sh check-earlier` refuse it, naming case `TestX` and its step ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 18 | 3831 | 270735 | 36296 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tests-frozen.sh record` on a `_test.go` file holding `func TestX(t *testing.T)` records it as case `TestX` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 4 | 4 | 5 | 3 | 18 | 3 |
| fast | 30 | 32 | 30 | 34 | 31 |  |  |  |  |
| target | 3 | 3 | 4 | 4 | 3 | 2 | 2 | 3 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 96 | 16069 | 1333433 | 280562 | 2.78 (estimate) |
