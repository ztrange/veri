### 📊 Metrics — issue 2635

Wall time for the issue: 2012 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2636.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.86 over 44 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 84244 tokens, largest 129524 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.53 | 84244 |
| 2 | $0.07 | 90696 |
| 3 | $0.03 | 91945 |
| 4 | $0.04 | 94060 |
| 5 | $0.02 | 94334 |
| 6 | $0.02 | 94748 |
| 7 | $0.02 | 95186 |
| 8 | $0.02 | 95496 |
| 9 | $0.02 | 95770 |
| 10 | $0.03 | 96572 |
| 11 | $0.03 | 97919 |
| 12 | $0.03 | 99757 |
| 13 | $0.04 | 101753 |
| 14 | $0.04 | 103734 |
| 15 | $0.03 | 104749 |
| 16 | $0.03 | 105427 |
| 17 | $0.03 | 105958 |
| 18 | $0.03 | 106441 |
| 19 | $0.03 | 107092 |
| 20 | $0.04 | 108900 |
| 21 | $0.03 | 109722 |
| 22 | $0.03 | 110620 |
| 23 | $0.03 | 111571 |
| 24 | $0.03 | 112604 |
| 25 | $0.03 | 113477 |
| 26 | $0.03 | 114279 |
| 27 | $0.03 | 114971 |
| 28 | $0.03 | 115371 |
| 29 | $0.03 | 116451 |
| 30 | $0.03 | 117793 |
| 31 | $0.04 | 120188 |
| 32 | $0.03 | 120894 |
| 33 | $0.03 | 121175 |
| 34 | $0.03 | 121637 |
| 35 | $0.04 | 123241 |
| 36 | $0.03 | 124028 |
| 37 | $0.04 | 125749 |
| 38 | $0.03 | 126498 |
| 39 | $0.03 | 127677 |
| 40 | $0.03 | 127954 |
| 41 | $0.03 | 128180 |
| 42 | $0.03 | 128433 |
| 43 | $0.03 | 128978 |
| 44 | $0.03 | 129524 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 794 | 0 | 31847 | 0.09 |
| red | 5 | 1 | 0 | 0 | 151 | 108 | 37 | 72 | 12695 | 1161964 | 123746 | 0.55 |
| green | 2 | 1 | 0 | 0 | 118 | 25 | 12 | 22 | 2539 | 326195 | 33339 | 0.14 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 3 | 6 | 278 | 80236 | 14987 | 0.05 |
| pin | 3 | 3 | 0 | 0 | 74 | 45 | 21 | 42 | 4713 | 617582 | 51139 | 0.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 159 | 76 | 31 | 62 | 7490 | 870511 | 114981 | 0.45 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 201 | 113 | 43 | 82 | 13529 | 1315466 | 140077 | 0.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| watch-runs keeps watching, with no exit 2 and no traceback, when the run's newest leaf log under its .tdd holds stream-json lines followed by blank and plain-text prose lines, and reports that run's exit normally once its conductor exits; reproduced by a small in-process unit case in skills/tdd/scripts/tests/py/unit/test_watch_runs.py ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 69 | 29 | 54 | 7347 | 812207 | 108645 | 0.43 | 307 | unknown | 0/5 | nothing-left |  |  | full |
| watch-runs keeps watching, with no exit 2 and no traceback, when the run's newest leaf log holds only a partial first line, and reports that run's exit normally once its conductor exits; reproduced by a small in-process unit case in skills/tdd/scripts/tests/py/unit/test_watch_runs.py ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 13 | 26 | 3898 | 404997 | 37984 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| status --json renders, without raising and exiting 0, a run whose newest leaf log holds stream-json lines followed by blank and plain-text prose lines; reproduced by a case in the status suite with the same fixture ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 16 | 32 | 4786 | 510949 | 40819 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| status --json renders, without raising and exiting 0, a run whose newest leaf log holds only a partial first line; reproduced by a case in the status suite with the same fixture ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 15 | 30 | 4194 | 457824 | 35763 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| watch-runs keeps watching, with no exit 2 and no traceback, when the run's newest leaf log under its .tdd holds stream-json lines followed by blank and plain-text prose lines, and reports that run's exit normally once its conductor exits; reproduced by a small in-process unit case in skills/tdd/scripts/tests/py/unit/test_watch_runs.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 4 | 4 | 3 | 3 | 5 |  |
| fast | 33 | 30 |  |  |  |  |  |
| target | 3 | 2 | 2 | 2 | 2 | 3 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 74 | 144 | 21019 | 2185977 | 255058 | 2.93 (estimate) |
