### 📊 Metrics — issue 2940

Wall time for the issue: 2897 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 4 planned.
Outcome: the run bailed — revise-impossible, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.70 over 34 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89756 tokens, largest 137200 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89756 |
| 2 | $0.07 | 96738 |
| 3 | $0.04 | 98895 |
| 4 | $0.03 | 100489 |
| 5 | $0.02 | 100889 |
| 6 | $0.03 | 101593 |
| 7 | $0.02 | 101946 |
| 8 | $0.02 | 102239 |
| 9 | $0.02 | 102499 |
| 10 | $0.02 | 102842 |
| 11 | $0.02 | 103145 |
| 12 | $0.02 | 103459 |
| 13 | $0.03 | 104559 |
| 14 | $0.03 | 105097 |
| 15 | $0.05 | 108368 |
| 16 | $0.05 | 111419 |
| 17 | $0.03 | 111864 |
| 18 | $0.03 | 112769 |
| 19 | $0.03 | 113312 |
| 20 | $0.03 | 113938 |
| 21 | $0.04 | 115505 |
| 22 | $0.03 | 116188 |
| 23 | $0.03 | 117160 |
| 24 | $0.03 | 117502 |
| 25 | $0.03 | 118212 |
| 26 | $0.03 | 118865 |
| 27 | $0.03 | 119110 |
| 28 | $0.03 | 119795 |
| 29 | $0.03 | 120989 |
| 30 | $0.03 | 121463 |
| 31 | $0.09 | 129997 |
| 32 | $0.03 | 131077 |
| 33 | $0.04 | 132528 |
| 34 | $0.06 | 137200 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 1 | 2 | 1314 | 0 | 33027 | 0.10 |
| red | 2 | 1 | 0 | 0 | 112 | 19 | 9 | 12 | 2119 | 146232 | 51364 | 0.16 |
| green | 2 | 0 | 0 | 0 | 125 | 26 | 8 | 14 | 2728 | 189548 | 60738 | 0.30 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 100 | 20 | 4 | 8 | 2014 | 79651 | 48730 | 0.15 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 27 | 10 | 6 | 6 | 1419 | 66581 | 35661 | 0.11 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 125 | 26 | 8 | 14 | 2728 | 189548 | 60738 | 0.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 112 | 0.16 |
| green | 0 | 0.00 | 125 | 0.30 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A leaf that dies after more than the old 30 s bound (say at 45 s on the fake clock) reads as gone from `leaf_left` called with its default bound: a small unit case in `skills/tdd/scripts/tests/py/unit/test_supervise_leaf_waits.py` driven by the fake clock, no real wait ⟦criterion 2⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 45 | 17 | 26 | 4847 | 335780 | 112102 | 0.47 | unknown | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 9 | 8 | 20 |
| fast | 66 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 18 | 28 | 6161 | 335780 | 145129 | 2.26 (estimate) |
