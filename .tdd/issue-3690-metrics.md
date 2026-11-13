### 📊 Metrics — issue 3690

Wall time for the issue: 1272 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 3 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Suite flakes: skills/tdd/scripts/tests/py/unit/test_pytest_leg_passes.py::test_a_subset_leg_started_inside_the_directory_holding_its_serial_case_with_no_ini_file_leaves_none_unselected_and_exits_0.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.28 over 27 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 80536 tokens, largest 114104 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 80536 |
| 2 | $0.07 | 87397 |
| 3 | $0.03 | 88660 |
| 4 | $0.03 | 90626 |
| 5 | $0.02 | 91006 |
| 6 | $0.02 | 91424 |
| 7 | $0.02 | 91978 |
| 8 | $0.02 | 92310 |
| 9 | $0.02 | 92625 |
| 10 | $0.02 | 92941 |
| 11 | $0.02 | 93489 |
| 12 | $0.02 | 94231 |
| 13 | $0.03 | 95878 |
| 14 | $0.03 | 97637 |
| 15 | $0.03 | 99012 |
| 16 | $0.02 | 99440 |
| 17 | $0.03 | 100693 |
| 18 | $0.02 | 101239 |
| 19 | $0.02 | 101769 |
| 20 | $0.03 | 102613 |
| 21 | $0.04 | 104796 |
| 22 | $0.03 | 105808 |
| 23 | $0.03 | 106308 |
| 24 | $0.03 | 107036 |
| 25 | $0.03 | 107882 |
| 26 | $0.03 | 108843 |
| 27 | $0.06 | 114104 |

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
| plan | 1 | 1 | 0 | 0 | 19 | 11 | 1 | 2 | 618 | 0 | 19811 | 0.06 |
| red | 3 | 0 | 0 | 0 | 218 | 86 | 17 | 30 | 5662 | 430076 | 37429 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 19 | 11 | 1 | 2 | 618 | 0 | 19811 | 0.06 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 206 | 86 | 15 | 30 | 5662 | 430076 | 37429 | 0.19 |
| verifier | not recorded | 2 | 0 | 0 | 0 | 12 | 0 | 2 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 218 | 0.19 |
| verify-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| dispatch's overlap guard ignores the candidate issue's own run draft PR: with an open draft PR whose head branch is `tdd/<issue>-x` changing a path the issue names, dispatch prints no `skip` line for that issue and `launchable` is true (a small unit case in `skills/tdd/scripts/tests/py/unit/test_dispatch.py`, no real process) ⟦criterion 1⟧ | 3 | 0 | 0 | 0 | 0 | 1 | 86 | 17 | 30 | 5662 | 430076 | 37429 | 0.19 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 36 | 39 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 18 | 32 | 6280 | 430076 | 57240 | 1.53 (estimate) |
