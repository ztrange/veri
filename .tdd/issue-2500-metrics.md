### 📊 Metrics — issue 2500

Wall time for the issue: 2629 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2510.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.98 over 57 turns, in 2 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88647 tokens, largest 112102 tokens
Conductor context: first turn 88645 tokens, largest 131092 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88647 |
| 2 | $0.03 | 89007 |
| 3 | $0.04 | 92027 |
| 4 | $0.04 | 93691 |
| 5 | $0.04 | 94341 |
| 6 | $0.02 | 94696 |
| 7 | $0.03 | 95090 |
| 8 | $0.03 | 95368 |
| 9 | $0.03 | 95911 |
| 10 | $0.03 | 96400 |
| 11 | $0.04 | 97827 |
| 12 | $0.03 | 98301 |
| 13 | $0.09 | 105980 |
| 14 | $0.06 | 110018 |
| 15 | $0.04 | 110512 |
| 16 | $0.03 | 111182 |
| 17 | $0.04 | 112102 |
| 18 | $0.57 | 88645 |
| 19 | $0.05 | 92390 |
| 20 | $0.03 | 94352 |
| 21 | $0.02 | 94818 |
| 22 | $0.03 | 95932 |
| 23 | $0.02 | 96288 |
| 24 | $0.02 | 96624 |
| 25 | $0.02 | 96885 |
| 26 | $0.03 | 97733 |
| 27 | $0.02 | 98037 |
| 28 | $0.04 | 100633 |
| 29 | $0.06 | 104992 |
| 30 | $0.04 | 107080 |
| 31 | $0.02 | 107471 |
| 32 | $0.03 | 108440 |
| 33 | $0.03 | 108927 |
| 34 | $0.02 | 109107 |
| 35 | $0.03 | 110179 |
| 36 | $0.08 | 116822 |
| 37 | $0.03 | 117484 |
| 38 | $0.03 | 118766 |
| 39 | $0.04 | 120799 |
| 40 | $0.03 | 121008 |
| 41 | $0.03 | 122154 |
| 42 | $0.04 | 123640 |
| 43 | $0.03 | 124257 |
| 44 | $0.04 | 125901 |
| 45 | $0.03 | 126116 |
| 46 | $0.03 | 126739 |
| 47 | $0.03 | 126978 |
| 48 | $0.03 | 127699 |
| 49 | $0.03 | 127960 |
| 50 | $0.03 | 129106 |
| 51 | $0.03 | 129337 |
| 52 | $0.03 | 129718 |
| 53 | $0.03 | 130197 |
| 54 | $0.03 | 130464 |
| 55 | $0.03 | 130782 |
| 56 | $0.03 | 131092 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 985 | 0 | 36362 | 0.10 |
| diff | 12 | 6 | 0 | 0 | 585 | 175 | 48 | 90 | 14998 | 1337376 | 245632 | 0.90 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 304 | 86 | 23 | 44 | 7430 | 616762 | 146951 | 0.50 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 292 | 97 | 26 | 48 | 8553 | 720614 | 135043 | 0.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `start_conductor` in test_watch_runs_process.py waits, with a bound, for the stub's pid file to exist and be non-empty before reading it, and fails naming the path it waited for if the file never appears, replacing the flat `time.sleep(0.3)`; test-only, no production change, every case keeps its real processes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 16 | 2776 | 225101 | 55754 | 0.19 | 164 | n/a | n/a | n/a |  |  | full |
| `test_a_running_run_exits_1_and_prints_a_not_done_line_naming_the_running_state` in test_run_finished_process.py waits, with a bound, for its claude pid file to exist and be non-empty before reading it, and fails naming the path rather than raising `FileNotFoundError`; test-only, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 7 | 14 | 2205 | 205642 | 36361 | 0.13 | 107 | n/a | n/a | n/a |  |  | full |
| `test_it_prints_exactly_one_exit_line_when_a_conductor_whose_leaf_reaps_children_exits_2249` asserts the watcher's observation of the conductor's exit without depending on it falling inside a fixed wall-clock window, and a watcher `timeout` result fails with its own message rather than as an equality failure against `(0, ["exited 201 stale"])`; its pid-file wait also fails naming the path; test-only, real processes kept ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 7 | 14 | 2566 | 206435 | 37510 | 0.14 | 139 | n/a | n/a | n/a |  |  | full |
| `test_target_slot_is_free_only_below_target_asking_for_not_running_issues_1930` asserts the watcher's `slot-free 1/2 next 777` observation after the second conductor exits without depending on it falling inside a fixed wall-clock window, and a watcher `timeout` result there fails with its own message rather than as an equality failure; test-only, real processes kept ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 9 | 18 | 3353 | 284040 | 38827 | 0.16 | 131 | n/a | n/a | n/a |  |  | full |
| Every case named in the issue still asserts exactly what it asserted before this branch — the same outputs, exit codes and line counts — with no assertion weakened, skipped or deleted and no case newly marked `serial` ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 7 | 12 | 1952 | 173955 | 38480 | 0.13 | 113 | n/a | n/a | n/a |  |  | full |
| No bare `sleep` is added anywhere on this branch: every wait it adds is on a condition, with a bound that fails loudly when it is not met ⟦diff-checked⟧ ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 8 | 16 | 2146 | 242203 | 38700 | 0.14 | 121 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 18 | 18 | 17 | 18 | 17 | 18 | 0 | 17 | 17 | 17 | 18 | 17 | 17 |
| affected | 13 | 12 | 4 | 3 | 13 | 14 | 0 | 12 | 13 | 14 | 13 | 13 | 14 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 49 | 92 | 15983 | 1337376 | 281994 | 1.00 |
