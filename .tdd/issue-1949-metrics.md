### 📊 Metrics — issue 1949

Wall time for the issue: 2232 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2038.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.16 over 55 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84926 |
| 2 | $0.02 | 85409 |
| 3 | $0.03 | 86502 |
| 4 | $0.03 | 88445 |
| 5 | $0.02 | 88818 |
| 6 | $0.02 | 89246 |
| 7 | $0.02 | 89934 |
| 8 | $0.02 | 90488 |
| 9 | $0.02 | 90786 |
| 10 | $0.02 | 91614 |
| 11 | $0.03 | 92765 |
| 12 | $0.04 | 96049 |
| 13 | $0.04 | 99025 |
| 14 | $0.03 | 100128 |
| 15 | $0.02 | 100622 |
| 16 | $0.03 | 101455 |
| 17 | $0.02 | 101989 |
| 18 | $0.02 | 102231 |
| 19 | $0.03 | 103041 |
| 20 | $0.03 | 104479 |
| 21 | $0.03 | 105546 |
| 22 | $0.03 | 106951 |
| 23 | $0.03 | 107671 |
| 24 | $0.03 | 108439 |
| 25 | $0.02 | 108725 |
| 26 | $0.03 | 109982 |
| 27 | $0.03 | 110631 |
| 28 | $0.03 | 111506 |
| 29 | $0.04 | 113285 |
| 30 | $0.03 | 114278 |
| 31 | $0.03 | 115000 |
| 32 | $0.03 | 115375 |
| 33 | $0.03 | 116394 |
| 34 | $0.03 | 117239 |
| 35 | $0.03 | 117597 |
| 36 | $0.03 | 118093 |
| 37 | $0.03 | 119466 |
| 38 | $0.04 | 121903 |
| 39 | $0.04 | 123478 |
| 40 | $0.03 | 123787 |
| 41 | $0.03 | 124635 |
| 42 | $0.04 | 126486 |
| 43 | $0.03 | 127284 |
| 44 | $0.03 | 128182 |
| 45 | $0.04 | 129412 |
| 46 | $0.03 | 130075 |
| 47 | $0.03 | 130977 |
| 48 | $0.03 | 131492 |
| 49 | $0.03 | 131792 |
| 50 | $0.03 | 132066 |
| 51 | $0.03 | 132880 |
| 52 | $0.03 | 133222 |
| 53 | $0.03 | 133613 |
| 54 | $0.03 | 134015 |
| 55 | $0.03 | 134371 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 12 | 2 | 4 | 1169 | 30053 | 32365 | 0.10 |
| red | 4 | 1 | 0 | 0 | 130 | 97 | 22 | 44 | 9237 | 661016 | 93181 | 0.39 |
| green | 2 | 1 | 0 | 0 | 89 | 36 | 9 | 16 | 2662 | 218598 | 30021 | 0.12 |
| refactor | 2 | 1 | 0 | 0 | 47 | 20 | 7 | 12 | 1260 | 151159 | 28763 | 0.10 |
| pin | 2 | 2 | 0 | 0 | 35 | 21 | 6 | 12 | 2204 | 150886 | 28792 | 0.11 |
| diff | 2 | 1 | 0 | 0 | 74 | 20 | 6 | 12 | 1620 | 146872 | 24367 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 194 | 96 | 22 | 44 | 7169 | 538587 | 118107 | 0.42 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 195 | 110 | 30 | 56 | 10983 | 819997 | 119382 | 0.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `harvest-usage.sh author-skill-edit-1`, over a log whose closing result record carries usage, appends one `usage` event with `actor=author`, `phase=skill-edit` and `attempt=1` and exits 0 (a small in-process case in tests/py/unit/test_harvest_usage.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 25 | 46 | 6596 | 608726 | 109791 | 0.40 | 319 | unknown | 0/5 | nothing-left |  |  | full |
| `harvest-usage.sh` gives a leaf name whose attempt suffix follows a newline in the phase (e.g. `develop-red\n-2`) the same actor, phase and attempt that `leaf-role.sh` prints for that name, so every name gets leaf-role's answer (a small in-process case comparing the two over a list of names) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 10 | 20 | 4260 | 301961 | 34290 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A leading word added to `leaf_role`'s actor table (monkeypatched in-process, e.g. `plan` → `planner`) is harvested by `harvest_usage` into a `usage` event carrying that actor, with no change to `harvest_usage`: harvest_usage keeps no table or parser of its own and asks `leaf_role` for the role ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 9 | 18 | 4507 | 270972 | 36676 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| Every existing case in `tests/py/unit/test_harvest_usage.py`, `tests/py/test_harvest_usage_process.py`, `tests/py/unit/test_leaf_role.py` and `tests/py/test_leaf_role_process.py` keeps its name and its outcome, including the exact unknown-leading-word message pinned in tests/py/test_harvest_usage_process.py: the branch's diff renames, deletes or weakens none of them ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 20 | 6 | 12 | 1620 | 146872 | 24367 | 0.09 | 131 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `harvest-usage.sh author-skill-edit-1`, over a log whose closing result record carries usage, appends one `usage` event with `actor=author`, `phase=skill-edit` and `attempt=1` and exits 0 (a small in-process case in tests/py/unit/test_harvest_usage.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 47 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 3 | 1 | 3 | 2 | 1 | 2 | 2 | 4 | 4 |
| fast | 18 | 19 | 19 | 21 | 19 |  |  |  |  |  |
| target | 1 | 2 | 1 | 2 | 2 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 52 | 100 | 18152 | 1358584 | 237489 | 0.91 |
