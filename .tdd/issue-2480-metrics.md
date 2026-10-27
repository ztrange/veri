### 📊 Metrics — issue 2480

Wall time for the issue: 1469 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2503.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.68 over 32 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88644 tokens, largest 137606 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88644 |
| 2 | $0.02 | 89178 |
| 3 | $0.03 | 90652 |
| 4 | $0.03 | 92233 |
| 5 | $0.02 | 92814 |
| 6 | $0.02 | 93506 |
| 7 | $0.02 | 94046 |
| 8 | $0.02 | 94361 |
| 9 | $0.02 | 95122 |
| 10 | $0.02 | 95484 |
| 11 | $0.02 | 95908 |
| 12 | $0.11 | 107247 |
| 13 | $0.04 | 109050 |
| 14 | $0.03 | 110459 |
| 15 | $0.03 | 112042 |
| 16 | $0.04 | 113697 |
| 17 | $0.03 | 114132 |
| 18 | $0.03 | 114966 |
| 19 | $0.03 | 115516 |
| 20 | $0.03 | 116261 |
| 21 | $0.03 | 116863 |
| 22 | $0.14 | 131830 |
| 23 | $0.03 | 132665 |
| 24 | $0.03 | 133459 |
| 25 | $0.04 | 134573 |
| 26 | $0.03 | 135248 |
| 27 | $0.03 | 135961 |
| 28 | $0.03 | 136247 |
| 29 | $0.03 | 136522 |
| 30 | $0.03 | 136769 |
| 31 | $0.03 | 137169 |
| 32 | $0.03 | 137606 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 922 | 0 | 32196 | 0.09 |
| diff | 4 | 2 | 0 | 0 | 273 | 89 | 20 | 40 | 10249 | 598067 | 94439 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 115 | 30 | 8 | 16 | 3445 | 190633 | 64337 | 0.21 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 168 | 66 | 13 | 26 | 7726 | 407434 | 62298 | 0.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| test_2380_a_leaf_queued_on_the_full_suite_lock_past_the_hard_timeout_is_not_killed_stuck in skills/tdd/scripts/tests/py/test_supervise_process.py releases the full-suite lock only on an observed state — the queued leaf having reached the lock wait and the supervisor's hard timeout having passed while it waits, read from a file, an event, the lock-wait marker or the lock's holder record (an injected clock the case controls is allowed) — with no threading.Timer, sleep or fixed headroom constant governing its verdict; it stays a process case with a real supervise.sh and a real leaf, and no production file changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 12 | 24 | 7742 | 376223 | 62892 | 0.27 | 242 | n/a | n/a | n/a |  |  | full |
| test_2380_a_leaf_queued_on_the_full_suite_lock_past_the_silence_window_is_not_killed_for_silence in skills/tdd/scripts/tests/py/test_supervise_process.py releases the full-suite lock only on an observed state — the queued leaf having reached the lock wait and the supervisor's silence window having passed while it waits, read from a file, an event, the lock-wait marker or the lock's holder record (an injected clock the case controls is allowed) — with no threading.Timer, sleep or fixed headroom constant governing its verdict; it stays a process case with a real supervise.sh and a real leaf, and no production file changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 16 | 2507 | 221844 | 31547 | 0.13 | 169 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| fast | 26 | 27 |
| affected | 13 | 14 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 21 | 42 | 11171 | 598067 | 126635 | 0.49 |
