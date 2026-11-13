### 📊 Metrics — issue 3743

Wall time for the issue: 20180 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3754.
Lane: ready-for-agent
Suite flakes: skills/tdd/scripts/tests/py/unit/test_pytest_leg_passes.py::test_a_subset_leg_started_inside_the_directory_holding_its_serial_case_with_no_ini_file_leaves_none_unselected_and_exits_0.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.25 over 41 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 80538 tokens, largest 91918 tokens
Conductor context: first turn 80488 tokens, largest 124338 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 80538 |
| 2 | $0.07 | 87367 |
| 3 | $0.03 | 88719 |
| 4 | $0.03 | 90600 |
| 5 | $0.02 | 90986 |
| 6 | $0.02 | 91353 |
| 7 | $0.02 | 91918 |
| 8 | unpriced | 0 |
| 9 | $0.50 | 80488 |
| 10 | $0.07 | 87341 |
| 11 | $0.03 | 88758 |
| 12 | $0.03 | 90339 |
| 13 | $0.02 | 91176 |
| 14 | $0.03 | 92055 |
| 15 | $0.02 | 92637 |
| 16 | $0.02 | 92972 |
| 17 | $0.02 | 93376 |
| 18 | $0.02 | 93804 |
| 19 | $0.03 | 94661 |
| 20 | $0.03 | 96069 |
| 21 | $0.02 | 96753 |
| 22 | $0.03 | 98165 |
| 23 | $0.02 | 98687 |
| 24 | $0.02 | 99294 |
| 25 | $0.03 | 100217 |
| 26 | $0.03 | 101646 |
| 27 | $0.02 | 102010 |
| 28 | $0.02 | 102530 |
| 29 | $0.03 | 103532 |
| 30 | $0.03 | 104171 |
| 31 | $0.02 | 104416 |
| 32 | $0.03 | 105636 |
| 33 | $0.08 | 112463 |
| 34 | $0.02 | 112771 |
| 35 | $0.03 | 113116 |
| 36 | $0.03 | 113453 |
| 37 | $0.03 | 114134 |
| 38 | $0.03 | 114806 |
| 39 | $0.03 | 115154 |
| 40 | $0.09 | 123850 |
| 41 | $0.03 | 124338 |

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
| 🗺️ Plan | 0 | 0 | $0.00 |
| 🗺️ verify-plan | 0 | 0 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 0 | 0 | $0.00 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 552 | 0 | 19734 | 0.05 |
| prose | 5 | 0 | 0 | 0 | 76 | 60 | 5 | 10 | 6326 | 16632 | 48796 | 0.19 |
| skill-edit | 1 | 0 | 0 | 0 | 8 | 5 | 2 | 4 | 667 | 17752 | 18254 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 552 | 0 | 19734 | 0.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/vbail/SKILL.md`'s *A first real bail: resume once* makes the first-bail resume take a slot like any launch: it runs only when the live conductors, counted fresh at that moment with `kill -0`, number fewer than N (an unexpired timed N included, as read from the dev role state); otherwise the resume is held and the next freed slot goes to it ahead of the solvable queue — graded against requirement B14 ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 42 | 6 | 12 | 4954 | 33735 | 53900 | 0.19 | 105 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| issue | 1 | ? | ? | nothing-structural 1 |

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 8 | 16 | 7545 | 34384 | 86784 | 2.54 (estimate) |
