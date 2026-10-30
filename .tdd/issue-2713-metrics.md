### 📊 Metrics — issue 2713

Wall time for the issue: 3308 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2726.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.08 over 36 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86115 tokens, largest 162684 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86115 |
| 2 | $0.07 | 93119 |
| 3 | $0.03 | 94448 |
| 4 | $0.04 | 96759 |
| 5 | $0.02 | 97252 |
| 6 | $0.02 | 97716 |
| 7 | $0.02 | 98040 |
| 8 | $0.02 | 98330 |
| 9 | $0.07 | 104070 |
| 10 | $0.04 | 106023 |
| 11 | $0.11 | 117118 |
| 12 | $0.03 | 118071 |
| 13 | $0.04 | 119946 |
| 14 | $0.04 | 122541 |
| 15 | $0.05 | 125584 |
| 16 | $0.04 | 127446 |
| 17 | $0.05 | 130075 |
| 18 | $0.04 | 131362 |
| 19 | $0.05 | 133726 |
| 20 | $0.04 | 135054 |
| 21 | $0.10 | 143569 |
| 22 | $0.06 | 147056 |
| 23 | $0.04 | 148004 |
| 24 | $0.04 | 149137 |
| 25 | $0.04 | 150943 |
| 26 | $0.04 | 152148 |
| 27 | $0.04 | 153077 |
| 28 | $0.05 | 154991 |
| 29 | $0.04 | 155896 |
| 30 | $0.05 | 157760 |
| 31 | $0.05 | 159767 |
| 32 | $0.04 | 160501 |
| 33 | $0.03 | 160842 |
| 34 | $0.04 | 161789 |
| 35 | $0.03 | 162019 |
| 36 | $0.04 | 162684 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 570 | 0 | 31706 | 0.08 |
| red | 5 | 2 | 1 | 0 | 264 | 168 | 25 | 50 | 14630 | 768406 | 142424 | 0.82 |
| green | 5 | 1 | 1 | 0 | 290 | 76 | 25 | 42 | 7301 | 626209 | 101518 | 0.46 |
| red-supersede | 1 | 0 | 0 | 0 | 34 | 25 | 5 | 10 | 2834 | 153235 | 19374 | 0.09 |
| refactor | 1 | 0 | 0 | 0 | 13 | 9 | 3 | 6 | 356 | 64926 | 34364 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 4 | 2 | 0 | 312 | 108 | 22 | 44 | 8688 | 607800 | 103587 | 0.41 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 250 | 141 | 29 | 50 | 13813 | 786815 | 172061 | 0.96 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 47 | 34 | 8 | 16 | 3190 | 218161 | 53738 | 0.19 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 264 | 0.82 | 0 | 0.00 |
| green | 290 | 0.46 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| add-ledger-step.sh given a text already holding a criterion tag exits 2, names the tag on stderr and leaves the ledger byte-identical, with or without --criterion and for any position in a batch (one bad text inserts none); pinned by a case, run in-process through run_cli (small, no real process) ⟦criterion 1⟧ | 12 | 3 | 2 | 0 | 0 | 0 | 278 | 58 | 108 | 25121 | 1612776 | 297680 | 1.47 | 947 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| add-ledger-step.sh given a text already holding a criterion tag exits 2, names the tag on stderr and leaves the ledger byte-identical, with or without --criterion and for any position in a batch (one bad text inserts none); pinned by a case, run in-process through run_cli (small, no real process) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 13 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 4 | 5 | 3 | 3 | 3 | 3 | 7 | 5 |
| fast | 24 | 25 | 39 | 32 |  |  |  |  |  |  |
| target | 3 | 4 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 59 | 110 | 25691 | 1612776 | 329386 | 3.63 (estimate) |
