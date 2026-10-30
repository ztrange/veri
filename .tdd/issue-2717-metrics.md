### 📊 Metrics — issue 2717

Wall time for the issue: 3940 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2731.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.54 over 24 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86646 tokens, largest 139889 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86646 |
| 2 | $0.07 | 93649 |
| 3 | $0.03 | 94702 |
| 4 | $0.04 | 96938 |
| 5 | $0.02 | 97564 |
| 6 | $0.10 | 108221 |
| 7 | $0.02 | 108530 |
| 8 | $0.02 | 108797 |
| 9 | $0.06 | 112973 |
| 10 | $0.04 | 114919 |
| 11 | $0.03 | 115860 |
| 12 | $0.03 | 116887 |
| 13 | $0.11 | 127334 |
| 14 | $0.04 | 129649 |
| 15 | $0.06 | 133945 |
| 16 | $0.05 | 136397 |
| 17 | $0.03 | 137081 |
| 18 | $0.03 | 137435 |
| 19 | $0.03 | 137992 |
| 20 | $0.03 | 138541 |
| 21 | $0.03 | 138765 |
| 22 | $0.03 | 138980 |
| 23 | $0.03 | 139205 |
| 24 | $0.03 | 139889 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 9 | 1 | 2 | 1094 | 0 | 31813 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 235 | 49 | 15 | 30 | 6065 | 464570 | 53866 | 0.24 |
| red | 1 | 0 | 0 | 0 | 71 | 32 | 6 | 12 | 3819 | 198760 | 23270 | 0.12 |
| pin | 1 | 1 | 0 | 0 | 95 | 42 | 13 | 26 | 4287 | 455354 | 24466 | 0.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 180 | 63 | 18 | 36 | 6729 | 562560 | 70950 | 0.30 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 234 | 69 | 17 | 34 | 8536 | 556124 | 62465 | 0.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| test_2380_a_leaf_that_hangs_after_acquiring_the_full_suite_lock_is_still_killed_stuck's hard timeout starts only once the leaf is known to hold the lock (or is otherwise independent of start-up time), still asserting (2, True) on a medium case with a real supervise.sh and a real leaf; only tests change, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 15 | 30 | 6065 | 464570 | 53866 | 0.24 | 362 | n/a | n/a | n/a |  |  | full |
| A medium case in test_supervise_process.py, with a real supervise.sh and a real leaf, whose leaf's start-up is delayed past 4 s before it reaches the lock still ends (2, True); no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 19 | 38 | 8106 | 654114 | 47736 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 41 |  |  |  |
| affected | 16 | 24 |  |  |
| target | 12 | 13 | 11 | 10 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 35 | 70 | 15265 | 1118684 | 133415 | 2.13 (estimate) |
