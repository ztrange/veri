### 📊 Metrics — issue 1955

Wall time for the issue: 4036 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 13 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2153.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 34 | 30 | 7 | 14 | 3334 | 195963 | 31936 | 0.13 |
| red | 23 | 11 | 0 | 0 | 509 | 374 | 108 | 216 | 38702 | 3130096 | 391387 | 1.68 |
| green | 26 | 11 | 2 | 0 | 1224 | 460 | 119 | 230 | 34745 | 3248011 | 384908 | 1.83 |
| refactor | 22 | 11 | 0 | 0 | 351 | 206 | 65 | 126 | 11737 | 1582912 | 284612 | 0.99 |
| pin | 1 | 1 | 0 | 0 | 28 | 20 | 5 | 10 | 1463 | 137538 | 15573 | 0.07 |
| diff | 2 | 1 | 0 | 0 | 35 | 15 | 7 | 14 | 1631 | 175402 | 23542 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 39 | 36 | 3 | 0 | 1265 | 481 | 132 | 262 | 35844 | 3390601 | 508040 | 1.97 |
| developer | claude-sonnet-5-5 | 33 | 0 | 0 | 0 | 752 | 515 | 152 | 296 | 46307 | 4270641 | 531953 | 2.22 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 164 | 109 | 27 | 52 | 9461 | 808680 | 91965 | 0.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 719 | 0.80 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `report-cache.sh` (a new `/bin/sh` shim exec'ing `python3` on a new module `veri/report_cache.py`, its usage line in the shim's header) called with no subcommand, or with an unknown one, exits 2 with its usage on stderr ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 84 | 24 | 46 | 6031 | 629377 | 85033 | 0.34 | 202 | unknown | 0/5 | nothing-left |  |  | full |
| `report-cache.sh refresh` with no cache yet, `gh` faked, writes `.tdd/report-cache.json` in the main working tree holding every issue, open and closed, each with its number, title, state, labels, `closedAt` and `updatedAt`, plus a top-level `fetched_at`, and exits 0 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 24 | 46 | 7367 | 628544 | 91061 | 0.36 | 190 | unknown | 0/5 | nothing-left |  |  | full |
| `report-cache.sh refresh` run from a linked git worktree writes `.tdd/report-cache.json` under the repository's main working tree, not under the worktree it was run from ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 137 | 31 | 60 | 10131 | 819488 | 107090 | 0.54 | 269 | 1/2 | 0/5 | nothing-left |  |  | full |
| Each issue in the cache a first refresh writes carries the issue numbers listed under its body's `## Blocked by` section, an empty list when it names none ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 20 | 40 | 6076 | 521757 | 83569 | 0.32 | 164 | unknown | 0/5 | nothing-left |  |  | full |
| Each issue in the cache a first refresh writes carries the wall-time seconds read from its last `### 📊 Metrics` comment (the `Wall time for the issue: <n> s` line), and a null wall time and null lane when it has no such comment ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 71 | 21 | 42 | 6521 | 557119 | 84308 | 0.33 | 173 | unknown | 0/5 | nothing-left |  |  | full |
| A refresh reads the wall-time seconds from a comment that carries its `### 📊 Metrics` block under another heading, as the `### ✅ Done` and bail comments veri posts do, not only from a comment that opens with that heading ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 57 | 22 | 42 | 4849 | 552007 | 81027 | 0.31 | 142 | unknown | 0/5 | nothing-left |  |  | full |
| A refresh run when `.tdd/report-cache.json` already exists asks `gh` only for the issues updated since its `fetched_at` (an `updated:>=<fetched_at>` query), merges the issues it receives into the file by number, keeps every issue it did not receive unchanged, and moves `fetched_at` forward ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 80 | 24 | 48 | 7148 | 656583 | 89756 | 0.36 | 170 | unknown | 1/5 | nothing-left |  |  | full |
| A refresh whose `gh` read fails exits 2 with exactly one stderr line naming the failure and leaves `.tdd/report-cache.json` byte-identical ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 80 | 23 | 44 | 7382 | 606229 | 89566 | 0.36 | 170 | unknown | 0/5 | nothing-left |  |  | full |
| A refresh whose `gh` read answers with something unparseable exits 2 with exactly one stderr line naming the failure and leaves `.tdd/report-cache.json` byte-identical ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 13 | 26 | 4518 | 397244 | 37498 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| The verbatim `OLD_REPORT` comparison in `test_issue_454_every_by_step_column_that_existed_before_and_every_other_section_reads_the_same_for_an_existing_log` (`skills/tdd/scripts/tests/py/test_metrics.py`) drops a `Lane: <label>` line from the report before comparing, so that case keeps passing once the report gains that line; a test-only change, no production change ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 15 | 7 | 14 | 1631 | 175402 | 23542 | 0.09 | 55 | n/a | n/a | n/a |  |  | full |
| The `### 📊 Metrics` report `metrics.sh` writes for an issue carries a `Lane: <label>` line naming the opt-in label the run ran under, `VERI_LABEL`, or `ready-for-agent` when it is unset ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 75 | 26 | 52 | 5306 | 734965 | 90779 | 0.35 | 167 | unknown | 0/5 | nothing-left |  |  | full |
| A refresh reads the `Lane: <label>` line of an issue's last `### 📊 Metrics` comment into that issue's `lane` in the cache ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 89 | 24 | 48 | 6957 | 657839 | 90334 | 0.36 | 178 | unknown | 1/5 | nothing-left |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_no_graphql_gh_calls.py — FAILED test_no_module_but_github_py_starts_a_gh_process_1974 (report_cache.py starts a gh process itself rather than through the GitHub port veri/github.py); skills/tdd/scripts/tests/py/unit/test_tunable_reads.py — FAILED test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment and test_run_leaf_run_verdict_and_stop_run_take_their_veri_values_from_the_one_reader_and_no_module_is_exempt (metrics.py:451 reads VERI_LABEL from os.environ rather than through the one tunables reader) ⟦suite-repair⟧ ⟦criterion 4⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 184 | 45 | 88 | 14361 | 1337405 | 146459 | 0.76 | 722 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `report-cache.sh` (a new `/bin/sh` shim exec'ing `python3` on a new module `veri/report_cache.py`, its usage line in the shim's header) called with no subcommand, or with an unknown one, exits 2 with its usage on stderr ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 24 | 0.08 |
| `report-cache.sh refresh` with no cache yet, `gh` faked, writes `.tdd/report-cache.json` in the main working tree holding every issue, open and closed, each with its number, title, state, labels, `closedAt` and `updatedAt`, plus a top-level `fetched_at`, and exits 0 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 31 | 0.09 |
| `report-cache.sh refresh` run from a linked git worktree writes `.tdd/report-cache.json` under the repository's main working tree, not under the worktree it was run from ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 36 | 0.09 |
| Each issue in the cache a first refresh writes carries the issue numbers listed under its body's `## Blocked by` section, an empty list when it names none ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 22 | 0.08 |
| Each issue in the cache a first refresh writes carries the wall-time seconds read from its last `### 📊 Metrics` comment (the `Wall time for the issue: <n> s` line), and a null wall time and null lane when it has no such comment ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 26 | 0.08 |
| A refresh reads the wall-time seconds from a comment that carries its `### 📊 Metrics` block under another heading, as the `### ✅ Done` and bail comments veri posts do, not only from a comment that opens with that heading ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 33 | 0.08 |
| A refresh run when `.tdd/report-cache.json` already exists asks `gh` only for the issues updated since its `fetched_at` (an `updated:>=<fetched_at>` query), merges the issues it receives into the file by number, keeps every issue it did not receive unchanged, and moves `fetched_at` forward ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 40 | 0.10 |
| A refresh whose `gh` read fails exits 2 with exactly one stderr line naming the failure and leaves `.tdd/report-cache.json` byte-identical ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 29 | 0.09 |
| The `### 📊 Metrics` report `metrics.sh` writes for an issue carries a `Lane: <label>` line naming the opt-in label the run ran under, `VERI_LABEL`, or `ready-for-agent` when it is unset ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 29 | 0.09 |
| A refresh reads the `Lane: <label>` line of an issue's last `### 📊 Metrics` comment into that issue's `lane` in the cache ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 46 | 0.10 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_no_graphql_gh_calls.py — FAILED test_no_module_but_github_py_starts_a_gh_process_1974 (report_cache.py starts a gh process itself rather than through the GitHub port veri/github.py); skills/tdd/scripts/tests/py/unit/test_tunable_reads.py — FAILED test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment and test_run_leaf_run_verdict_and_stop_run_take_their_veri_values_from_the_one_reader_and_no_module_is_exempt (metrics.py:451 reads VERI_LABEL from os.environ rather than through the one tunables reader) ⟦suite-repair⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 4 | 3 | 4 | 2 | 3 | 3 | 3 | 2 | 3 | 4 | 4 | 3 | 2 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 4 | 4 |
| fast | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 7 | 6 | 5 | 5 | 5 | 5 | 6 | 5 | 5 | 6 | 5 | 5 | 7 | 5 | 6 | 6 | 5 | 4 | 4 | 4 | 5 | 6 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 7 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 2 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 311 | 610 | 91612 | 8469922 | 1131958 | 4.79 |
