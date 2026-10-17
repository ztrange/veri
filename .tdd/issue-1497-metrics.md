### 📊 Metrics — issue 1497

Wall time for the issue: 287 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 3 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 2 | 4 | 1055 | 60429 | 36158 | 0.16 |
| red | 2 | 1 | 0 | 0 | 96 | 39 | 11 | 22 | 4320 | 487403 | 83518 | 0.43 |
| green | 3 | 0 | 0 | 0 | 74 | 45 | 14 | 24 | 3563 | 485863 | 118042 | 0.90 |
| exhausted | 1 | 0 | 0 | 0 | 17 | 15 | 2 | 4 | 1004 | 58518 | 36030 | 0.32 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 55 | 24 | 7 | 14 | 2423 | 267785 | 75615 | 0.35 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 53 | 24 | 6 | 12 | 2952 | 280047 | 44061 | 0.23 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 91 | 60 | 16 | 28 | 4567 | 544381 | 154072 | 1.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 96 | 0.43 |
| green | 0 | 0.00 | 74 | 0.90 |
| exhausted | 0 | 0.00 | 17 | 0.32 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A log whose closing `result` record has no `usage` key: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the closing result record carries no usage; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins `KeyError: 'usage'` as a traceback to the new line, since Green may not edit tests ⟦criterion 1⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 99 | 27 | 50 | 8887 | 1031784 | 237590 | 1.65 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 26 | 1 |
| fast | 6 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 29 | 54 | 9942 | 1092213 | 273748 | 1.81 |
