### 📊 Metrics — issue 1973

Wall time for the issue: 1479 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2159.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1054 | 17051 | 13858 | 0.05 |
| red | 14 | 7 | 0 | 0 | 306 | 190 | 59 | 106 | 19271 | 1464021 | 224348 | 0.90 |
| green | 14 | 7 | 0 | 0 | 658 | 171 | 57 | 110 | 16209 | 1490020 | 200494 | 0.81 |
| refactor | 12 | 6 | 0 | 0 | 189 | 76 | 33 | 62 | 5888 | 762381 | 159337 | 0.53 |
| diff | 2 | 1 | 0 | 0 | 69 | 25 | 6 | 12 | 1475 | 146891 | 23143 | 0.09 |
| rebase | 2 | 1 | 0 | 0 | 222 | 24 | 10 | 20 | 2370 | 271217 | 27114 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 23 | 23 | 0 | 0 | 826 | 208 | 72 | 140 | 19513 | 1753694 | 309132 | 1.14 |
| developer | claude-sonnet-5-5 | 22 | 0 | 0 | 0 | 630 | 287 | 94 | 172 | 26754 | 2397887 | 339162 | 1.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `reorder-ledger-steps.sh` refuses to move a ticked step written `  - [X] …` (indented, capital X), exiting 1 as it does for `- [x] …`, and refuses to move another step relative to it; pinned by a case in `tests/py/unit/test_reorder_ledger_steps.py` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 75 | 24 | 38 | 6211 | 494670 | 90049 | 0.34 | 241 | unknown | 0/5 | nothing-structural |  |  | full |
| `reorder-ledger-steps.sh` matches its step and anchor substrings only in step lines (the lines `ledger-steps.sh` reads as steps), never in a heading or a prose line: a substring found once in a step and once in a heading or prose line moves that step; pinned by a case in `tests/py/unit/test_reorder_ledger_steps.py` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 52 | 22 | 38 | 4958 | 500392 | 86849 | 0.32 | 190 | unknown | 0/5 | nothing-structural |  |  | full |
| `supervise.sh`'s ci-repair check numbers steps as `ledger-steps.sh` does: given a ledger holding a non-step `- [-]` line before the steps, step number `n` names the same step text in both, so a `⟦ci-repair⟧` step `n` is recognised by its `ledger-steps.sh` number; pinned by a case in `tests/py/test_supervise.py` ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 63 | 24 | 44 | 6598 | 591942 | 90325 | 0.35 | 242 | unknown | 0/5 | nothing-structural |  |  | full |
| `ledger.py` exposes `ledger_path(run_dir, issue)`, the path of issue `n`'s ledger `.tdd/issue-<n>.md` under the run directory `run_dir`; pinned by a case in `tests/py/unit/test_ledger.py` ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 55 | 18 | 36 | 3830 | 456536 | 80075 | 0.28 | 184 | unknown | 0/5 | nothing-structural |  |  | full |
| `run_finished`, `preserve_attempt`, `supervise`, `metrics`, `status` and `dashboard` take the ledger path from `ledger.ledger_path` and no module under `skills/tdd/scripts/veri/` other than `ledger.py` spells the ledger file name `issue-<n>.md` itself (other `issue-<n>-*` files such as `-metrics.md`, `-spec.md`, `-timeout` are not the ledger); pinned by a case, no behaviour of those modules changing ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 89 | 23 | 46 | 8467 | 632519 | 92801 | 0.38 | 266 | unknown | 0/5 | nothing-structural |  |  | full |
| Every existing case in `tests/py/unit/test_reorder_ledger_steps.py`, `tests/py/test_supervise.py`, `tests/py/test_run_finished_process.py`, `tests/py/test_preserve_attempt.py`, `tests/py/test_metrics.py`, `tests/py/test_status.py` and `tests/py/test_dashboard.py` keeps its name and its outcome on this branch: no case in those files is renamed, deleted or changed in what it asserts, and all pass ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 6 | 12 | 1475 | 146891 | 23143 | 0.09 | 100 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: tests/py/test_fast_tier_guard.py — FAIL - test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it and test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table: 'test_ledger_path_single_source.py: guard-clean, outside the tier' ⟦suite-repair⟧ ⟦criterion 5⟧ | 12 | 6 | 0 | 0 | 0 | 0 | 127 | 48 | 96 | 13674 | 1311580 | 171194 | 0.70 | 295 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `reorder-ledger-steps.sh` refuses to move a ticked step written `  - [X] …` (indented, capital X), exiting 1 as it does for `- [x] …`, and refuses to move another step relative to it; pinned by a case in `tests/py/unit/test_reorder_ledger_steps.py` ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 28 | 0.09 |
| `reorder-ledger-steps.sh` matches its step and anchor substrings only in step lines (the lines `ledger-steps.sh` reads as steps), never in a heading or a prose line: a substring found once in a step and once in a heading or prose line moves that step; pinned by a case in `tests/py/unit/test_reorder_ledger_steps.py` ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 26 | 0.09 |
| `supervise.sh`'s ci-repair check numbers steps as `ledger-steps.sh` does: given a ledger holding a non-step `- [-]` line before the steps, step number `n` names the same step text in both, so a `⟦ci-repair⟧` step `n` is recognised by its `ledger-steps.sh` number; pinned by a case in `tests/py/test_supervise.py` ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 31 | 0.09 |
| `ledger.py` exposes `ledger_path(run_dir, issue)`, the path of issue `n`'s ledger `.tdd/issue-<n>.md` under the run directory `run_dir`; pinned by a case in `tests/py/unit/test_ledger.py` ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 37 | 0.09 |
| `run_finished`, `preserve_attempt`, `supervise`, `metrics`, `status` and `dashboard` take the ledger path from `ledger.ledger_path` and no module under `skills/tdd/scripts/veri/` other than `ledger.py` spells the ledger file name `issue-<n>.md` itself (other `issue-<n>-*` files such as `-metrics.md`, `-spec.md`, `-timeout` are not the ledger); pinned by a case, no behaviour of those modules changing ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 43 | 0.10 |
| fix the full-suite failure: tests/py/test_fast_tier_guard.py — FAIL - test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it and test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table: 'test_ledger_path_single_source.py: guard-clean, outside the tier' ⟦suite-repair⟧ ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 24 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 3 | 4 | 4 | 4 | 5 | 4 | 3 | 3 | 4 | 8 | 9 | 10 | 8 | 9 | 4 | 3 | 3 | 3 | 4 | 4 | 5 | 12 | 13 | 0 | 10 | 13 | 13 | 5 | 6 | 5 | 5 | 6 | 6 | 5 | 4 | 5 | 4 | 4 |
| fast | 10 | 7 | 8 | 6 | 7 | 6 | 7 | 6 | 7 | 6 | 6 | 6 | 8 | 8 | 9 | 7 | 6 | 6 | 7 | 6 | 6 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 4 | 3 | 3 | 8 | 6 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 93 | 99 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 166 | 312 | 46267 | 4151581 | 648294 | 2.50 |
