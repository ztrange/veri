### 📊 Metrics — issue 3518

Wall time for the issue: 1172 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3553.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.51 over 49 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78372 tokens, largest 93700 tokens
Conductor context: first turn 78403 tokens, largest 129880 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.49 | 78372 |
| 2 | $0.07 | 84375 |
| 3 | $0.03 | 85577 |
| 4 | $0.03 | 85903 |
| 5 | $0.04 | 87739 |
| 6 | $0.02 | 88115 |
| 7 | $0.03 | 88499 |
| 8 | $0.03 | 88763 |
| 9 | $0.02 | 89204 |
| 10 | $0.04 | 90797 |
| 11 | $0.04 | 93052 |
| 12 | $0.03 | 93700 |
| 13 | $0.49 | 78403 |
| 14 | $0.06 | 84428 |
| 15 | $0.03 | 85611 |
| 16 | $0.03 | 87679 |
| 17 | $0.02 | 87998 |
| 18 | $0.02 | 88356 |
| 19 | $0.02 | 88763 |
| 20 | $0.02 | 89098 |
| 21 | $0.02 | 89495 |
| 22 | $0.02 | 89832 |
| 23 | $0.02 | 90094 |
| 24 | $0.02 | 90748 |
| 25 | $0.03 | 91785 |
| 26 | $0.03 | 93465 |
| 27 | $0.05 | 96797 |
| 28 | $0.03 | 98171 |
| 29 | $0.02 | 98435 |
| 30 | $0.02 | 98722 |
| 31 | $0.03 | 99411 |
| 32 | $0.02 | 99963 |
| 33 | $0.02 | 100529 |
| 34 | $0.02 | 101093 |
| 35 | $0.03 | 102520 |
| 36 | $0.03 | 103930 |
| 37 | $0.06 | 108403 |
| 38 | $0.03 | 109160 |
| 39 | $0.02 | 109471 |
| 40 | $0.03 | 110197 |
| 41 | $0.03 | 110772 |
| 42 | $0.03 | 111132 |
| 43 | $0.03 | 112068 |
| 44 | $0.15 | 127863 |
| 45 | $0.03 | 128254 |
| 46 | $0.03 | 128553 |
| 47 | $0.03 | 129154 |
| 48 | $0.03 | 129493 |
| 49 | $0.03 | 129880 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 0 | 0 | $0.00 |
| 🟢 Green | 0 | 0 | $0.00 |
| 🛠️ Refactor | 0 | 0 | $0.00 |
| 🔎 verify-green | 0 | 0 | $0.00 |
| 🔎 verify-refactor | 0 | 0 | $0.00 |
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 1 | 16 | $0.00 |
| 🗺️ verify-plan | 1 | 16 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 2 | 32 | $0.00 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 6 | 1 | 2 | 540 | 0 | 18713 | 0.05 |
| red | 1 | 0 | 0 | 0 | 63 | 52 | 11 | 14 | 5211 | 147269 | 29103 | 0.14 |
| pin | 1 | 1 | 0 | 0 | 46 | 37 | 7 | 14 | 2766 | 118166 | 16350 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 53 | 43 | 8 | 16 | 3306 | 118166 | 35063 | 0.13 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 63 | 52 | 11 | 14 | 5211 | 147269 | 29103 | 0.14 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| At --target 3, with tick 1 live runs [5, 7, 8] and tick 2 live [5] plus run 7's restart marker held by a live pid, dispatch launches exactly [12] — added as an in-case contrast inside the existing case test_main_launches_exactly_one_at_target_3_beside_a_live_run_with_a_leftover_marker_and_a_never_seen_restarting_run_issue_3495 in skills/tdd/scripts/tests/py/unit/test_dispatch.py (case name unchanged, its existing assertions kept, a small unit case with no real process), not a new standalone case ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 89 | 18 | 28 | 7977 | 265435 | 45453 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| issue | 1 | ? | ? | nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 2 | 2 | 1 |
| target | 2 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 19 | 30 | 8517 | 265435 | 64166 | 2.78 (estimate) |
