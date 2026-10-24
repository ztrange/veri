### 📊 Metrics — issue 2201

Wall time for the issue: 589 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2251.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.23 over 25 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89491 |
| 2 | $0.02 | 90277 |
| 3 | $0.03 | 92330 |
| 4 | $0.02 | 92762 |
| 5 | $0.02 | 93090 |
| 6 | $0.02 | 93398 |
| 7 | $0.02 | 93995 |
| 8 | $0.03 | 95029 |
| 9 | $0.03 | 96228 |
| 10 | $0.03 | 97077 |
| 11 | $0.02 | 97763 |
| 12 | $0.02 | 98246 |
| 13 | $0.03 | 98942 |
| 14 | $0.02 | 99376 |
| 15 | $0.06 | 104836 |
| 16 | $0.03 | 105448 |
| 17 | $0.03 | 106104 |
| 18 | $0.03 | 106794 |
| 19 | $0.03 | 107488 |
| 20 | $0.03 | 108121 |
| 21 | $0.03 | 108796 |
| 22 | $0.02 | 109045 |
| 23 | $0.02 | 109281 |
| 24 | $0.03 | 109676 |
| 25 | $0.02 | 109985 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 5 | 1 | 2 | 550 | 17442 | 13064 | 0.04 |
| diff | 4 | 2 | 0 | 0 | 103 | 47 | 16 | 32 | 3727 | 415147 | 48157 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 66 | 29 | 8 | 16 | 2150 | 193954 | 37049 | 0.13 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 49 | 23 | 9 | 18 | 2127 | 238635 | 24172 | 0.11 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The case test_a_resume_after_a_done_keeps_the_run_landed in skills/tdd/scripts/tests/py/test_metrics.py is renamed to a name saying what it pins — a resume after a done, with no live conductor, reads unknown — and its body and assertion are unchanged (test-only rename, no production change) ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 7 | 14 | 1833 | 180356 | 24600 | 0.10 | 86 | n/a | n/a | n/a |  |  | full |
| No case under skills/tdd/scripts/tests/ keeps "landed" in its name while asserting another outcome: every test function whose name holds "landed" asserts a landed outcome or uses "landed" for something other than the run's outcome (a green commit that never landed), with the grep that checks it recorded for the PR body (no production change) ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 9 | 18 | 1894 | 234791 | 23557 | 0.10 | 85 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 6 | 6 | 5 | 5 |
| affected | 3 | 3 | 3 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 17 | 34 | 4277 | 432589 | 61221 | 0.24 |
