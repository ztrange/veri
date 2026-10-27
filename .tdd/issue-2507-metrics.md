### 📊 Metrics — issue 2507

Wall time for the issue: 1655 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2509.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.44 over 33 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88650 tokens, largest 114674 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88650 |
| 2 | $0.02 | 89090 |
| 3 | $0.02 | 89799 |
| 4 | $0.03 | 91462 |
| 5 | $0.02 | 92089 |
| 6 | $0.02 | 92717 |
| 7 | $0.02 | 93312 |
| 8 | $0.02 | 93695 |
| 9 | $0.02 | 94033 |
| 10 | $0.02 | 94701 |
| 11 | $0.03 | 95568 |
| 12 | $0.03 | 96959 |
| 13 | $0.05 | 101135 |
| 14 | $0.03 | 102266 |
| 15 | $0.02 | 102619 |
| 16 | $0.03 | 103370 |
| 17 | $0.03 | 103918 |
| 18 | $0.03 | 104568 |
| 19 | $0.02 | 105040 |
| 20 | $0.03 | 106385 |
| 21 | $0.03 | 107478 |
| 22 | $0.03 | 108427 |
| 23 | $0.03 | 109134 |
| 24 | $0.03 | 110013 |
| 25 | $0.03 | 110772 |
| 26 | $0.03 | 111322 |
| 27 | $0.03 | 111954 |
| 28 | $0.03 | 112734 |
| 29 | $0.03 | 113099 |
| 30 | $0.03 | 113409 |
| 31 | $0.03 | 113900 |
| 32 | $0.03 | 114200 |
| 33 | $0.03 | 114674 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 928 | 0 | 31466 | 0.09 |
| diff | 4 | 2 | 0 | 0 | 228 | 68 | 17 | 34 | 7584 | 460498 | 89240 | 0.35 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 120 | 36 | 8 | 16 | 3492 | 187439 | 65097 | 0.22 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 118 | 39 | 10 | 20 | 5020 | 273059 | 55609 | 0.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| test_2380_a_leaf_whose_full_run_queues_on_the_lock_from_its_own_process_group_past_the_hard_timeout_is_not_killed_stuck in skills/tdd/scripts/tests/py/test_supervise_process.py releases the full-suite lock only on an observed state — its own-session full run having reached the lock wait and the supervisor's hard timeout having passed while it waits, read from a file, an event, the lock-wait marker or the lock's holder record (an injected clock the case controls, as #2480's shared helper uses, is allowed) — with no threading.Timer, sleep or fixed headroom constant governing its verdict; it stays a process case with a real supervise.sh and a real leaf whose full run runs in a session of its own, and no production file changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 3681 | 241201 | 54016 | 0.20 | 213 | n/a | n/a | n/a |  |  | full |
| test_2380_a_leaf_that_hangs_after_acquiring_the_full_suite_lock_is_still_killed_stuck in skills/tdd/scripts/tests/py/test_supervise_process.py releases the full-suite lock only on an observed state — the leaf having reached the lock wait, read from a file, an event, the lock-wait marker or the lock's holder record (an injected clock the case controls is allowed) — so that the leaf acquires the lock, hangs holding it and is killed stuck (exit 2, the acquired file written), with no threading.Timer, sleep or fixed headroom constant governing its verdict; it stays a process case with a real supervise.sh and a real leaf, and no production file changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 8 | 16 | 3903 | 219297 | 35224 | 0.15 | 178 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 25 | 26 | 24 | 25 |
| affected | 13 | 14 | 8 | 8 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 18 | 36 | 8512 | 460498 | 120706 | 0.43 |
