### 📊 Metrics — issue 2008

Wall time for the issue: 1930 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2200.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 15 | 2 | 4 | 2037 | 31879 | 34378 | 0.11 |
| diff | 6 | 3 | 0 | 0 | 189 | 102 | 32 | 62 | 10148 | 889052 | 114665 | 0.48 |
| red | 11 | 4 | 0 | 0 | 310 | 219 | 68 | 136 | 28476 | 2220080 | 231620 | 1.09 |
| green | 8 | 4 | 0 | 0 | 234 | 98 | 44 | 82 | 10447 | 1209765 | 128371 | 0.55 |
| refactor | 8 | 4 | 0 | 0 | 110 | 46 | 25 | 48 | 3941 | 612226 | 102553 | 0.36 |
| pin | 3 | 3 | 0 | 0 | 70 | 33 | 13 | 26 | 3977 | 347175 | 42095 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 19 | 19 | 0 | 0 | 435 | 205 | 75 | 146 | 20993 | 1920155 | 289931 | 1.13 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 496 | 308 | 109 | 212 | 38033 | 3390022 | 363751 | 1.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Test-only, no production change: every existing case in `skills/tdd/scripts/tests/py/test_dashboard.py` whose run is expected to be recomputed as live (runs 31, 36 and 7 of the `/api/metrics` cases) gains a live-conductor fixture — the run's `.tdd/conductor.pid` holding a pid that answers `kill -0` (the test's own), and `run_end`'s command-line function replaced to answer `run-conductor.sh <issue>` for that run's issue — keeping its name and its outcome under both the current code and `run_end`'s rule ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 9 | 18 | 3028 | 236421 | 49904 | 0.18 | 106 | n/a | n/a | n/a |  |  | full |
| metrics' outcome line comes from `run_end` (asked of the run directory holding the `.tdd/events.jsonl` it reads): a run whose events are `bail`, then `resume`, then `launch` events, with a live conductor (pid answering `kill -0`, `run_end`'s command-line function replaced to answer run-conductor for its issue), prints `Outcome: none yet — the run is still going.` and not `bailed`; this step's Red also rewrites, keeping their names, the existing cases of `tests/py/test_metrics.py` whose outcome `run_end`'s rule changes (such as `test_a_resume_after_a_done_keeps_the_run_landed`, whose `done` then `resume` with no live conductor and no conductor log now reads `Outcome: unknown — the log carries no mark ending the run.`) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 32 | 62 | 9622 | 954645 | 108770 | 0.46 | 236 | unknown | 0/5 | nothing-left |  |  | full |
| metrics, for a run with no standing mark and no live conductor whose conductor log's latest launch ends in a usage-limit result (`run_end`'s cause `usage-limit`), prints `Outcome: the run hit a usage limit.` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 66 | 27 | 54 | 7648 | 780855 | 96069 | 0.39 | 189 | unknown | 0/5 | nothing-left |  |  | full |
| metrics, for a run with no standing mark and no live conductor whose conductor log's latest launch has no result record (`run_end`'s cause `killed`), prints `Outcome: the run was killed — its conductor's latest launch left no result.` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 52 | 24 | 46 | 6134 | 644947 | 91177 | 0.35 | 184 | unknown | 0/5 | nothing-left |  |  | full |
| The dashboard's `/api/metrics` recomputes the report of a run whose events are `bail`, then `resume`, then `launch` events, with a live conductor, instead of quoting its committed `issue-<n>-metrics.md`; this step's Red also rewrites, keeping its name, `test_get_api_metrics_recomputes_run_35_whose_log_carries_a_stop_mark_and_no_done_or_bail` to its outcome under `run_end` (a `stop` mark ends the run, so its committed report, or the missing-report marker, is served) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 28 | 52 | 9373 | 771284 | 97984 | 0.42 | 234 | unknown | 0/5 | nothing-left |  |  | full |
| The dashboard's `/api/metrics` quotes the committed `issue-<n>-metrics.md` of a run with no standing mark and no live conductor (`run_end` says it has ended, cause `killed`), instead of recomputing it ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 13 | 26 | 4430 | 411983 | 37522 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| metrics answers whether a run has ended only from `run_end`: with `run_end`'s `run_end` function replaced by a spy answering not ended over a log carrying `done`, the outcome is `none yet`; answering ended with cause `bailed` and a `bail` standing mark over a log carrying no mark, the outcome is that bail's cause and classification ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 13 | 26 | 4537 | 413273 | 37488 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| The dashboard answers whether a run has ended only from `run_end`: with `run_end`'s `run_end` function replaced by a spy answering not ended over a log carrying `done`, `/api/metrics` recomputes the report; answering ended over a log carrying no mark, it quotes the committed report ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 13 | 26 | 5097 | 412259 | 35629 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| Neither `veri/metrics.py` nor `veri/dashboard.py` keeps a rule of its own for whether a run has ended: metrics' scan of `done`/`bail`/`stop`/`resume` events for its ending mark and the dashboard's `run_ended` over `done`/`bail` marks are gone, their outcome, wall-time end, structural-pass default and report-finality read from `run_end`'s answer and standing mark; no existing case of `tests/py/test_metrics.py` or `tests/py/test_dashboard.py` is renamed or deleted by the branch, and a case's expected outcome changes only where `run_end`'s rule answers differently ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 16 | 30 | 4803 | 471376 | 37622 | 0.19 | 113 | n/a | n/a | n/a |  |  | full |
| Combine, don't replace: every signal metrics and the dashboard read to decide whether a run has ended — the events, and now the conductor pid and the conductor log — reaches them as an input to `run_end`; neither module read the exit code, the PR state or `.tdd/parked/` for that decision before the branch, and the branch adds none and drops none; metrics keeps answering the outcome (the `done` mark's PR, the `bail` mark's cause and classification, the `stop` mark's mode and at, read from `run_end`'s standing mark) and the dashboard whether a report is final ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 21 | 7 | 14 | 2317 | 181255 | 27139 | 0.11 | 79 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| metrics' outcome line comes from `run_end` (asked of the run directory holding the `.tdd/events.jsonl` it reads): a run whose events are `bail`, then `resume`, then `launch` events, with a live conductor (pid answering `kill -0`, `run_end`'s command-line function replaced to answer run-conductor for its issue), prints `Outcome: none yet — the run is still going.` and not `bailed`; this step's Red also rewrites, keeping their names, the existing cases of `tests/py/test_metrics.py` whose outcome `run_end`'s rule changes (such as `test_a_resume_after_a_done_keeps_the_run_landed`, whose `done` then `resume` with no live conductor and no conductor log now reads `Outcome: unknown — the log carries no mark ending the run.`) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 27 | 0.10 |
| metrics, for a run with no standing mark and no live conductor whose conductor log's latest launch ends in a usage-limit result (`run_end`'s cause `usage-limit`), prints `Outcome: the run hit a usage limit.` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 28 | 0.10 |
| metrics, for a run with no standing mark and no live conductor whose conductor log's latest launch has no result record (`run_end`'s cause `killed`), prints `Outcome: the run was killed — its conductor's latest launch left no result.` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 25 | 0.08 |
| The dashboard's `/api/metrics` recomputes the report of a run whose events are `bail`, then `resume`, then `launch` events, with a live conductor, instead of quoting its committed `issue-<n>-metrics.md`; this step's Red also rewrites, keeping its name, `test_get_api_metrics_recomputes_run_35_whose_log_carries_a_stop_mark_and_no_done_or_bail` to its outcome under `run_end` (a `stop` mark ends the run, so its committed report, or the missing-report marker, is served) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 30 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 5 | 6 | 5 | 5 | 5 | 6 | 6 | 5 | 6 | 6 | 7 | 11 | 10 | 10 | 8 | 7 | 6 |  |  |  |  |  |  |  |  |  |  |  |
| affected | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 4 | 4 | 0 | 4 | 4 | 5 | 4 |
| target | 3 | 0 | 3 | 4 | 6 | 3 | 3 | 4 | 4 | 5 | 5 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 184 | 358 | 59026 | 5310177 | 653682 | 2.76 |
