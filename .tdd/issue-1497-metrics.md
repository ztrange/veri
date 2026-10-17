### 📊 Metrics — issue 1497

Wall time for the issue: 2175 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1680.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 2 | 4 | 1055 | 60429 | 36158 | 0.16 |
| red | 8 | 4 | 0 | 0 | 401 | 153 | 43 | 86 | 17833 | 1903610 | 336830 | 1.72 |
| green | 9 | 3 | 0 | 0 | 364 | 122 | 43 | 76 | 12116 | 1541664 | 346361 | 2.01 |
| exhausted | 1 | 0 | 0 | 0 | 17 | 15 | 2 | 4 | 1004 | 58518 | 36030 | 0.32 |
| refactor | 6 | 3 | 0 | 0 | 546 | 90 | 33 | 64 | 9449 | 1361104 | 232229 | 1.16 |
| predicate | 1 | 0 | 0 | 0 | 10 | 8 | 4 | 8 | 692 | 151024 | 34335 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 11 | 0 | 0 | 753 | 161 | 52 | 104 | 17074 | 2128960 | 418166 | 2.06 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 506 | 176 | 59 | 110 | 20508 | 2403008 | 449705 | 2.24 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 91 | 60 | 16 | 28 | 4567 | 544381 | 154072 | 1.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 96 | 0.43 |
| green | 0 | 0.00 | 74 | 0.90 |
| exhausted | 0 | 0.00 | 17 | 0.32 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A log whose closing `result` record has no `usage` key: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the closing result record carries no usage; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins `KeyError: 'usage'` as a traceback to the new line, since Green may not edit tests ⟦criterion 1⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 99 | 27 | 50 | 8887 | 1031784 | 237590 | 1.65 | unknown | 2/2 | unknown | unknown |  |  | full |
| A log whose closing `result` record has no `usage` key: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the closing result record carries no usage; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins `KeyError: 'usage'` as a traceback to the new line, and the `no-usage-1` row of `tests/py/unit/test_harvest_usage.py` (which pins exit 1 for a closing result record with no `usage` key) to exit 2 with the new stderr line, since Green may not edit tests; rows for other missing keys (`no-num-turns-1`, `no-output-tokens-1`) stay as they are unless the fix changes their behaviour too, in which case Red moves them in the same way ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 81 | 26 | 50 | 9062 | 1027036 | 238721 | 1.15 | 629 | unknown | 0/5 | nothing-left |  |  | full |
| A log that is not valid UTF-8: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the log is not valid UTF-8; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins the `UnicodeDecodeError` traceback to the new line, since Green may not edit tests ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 101 | 34 | 64 | 11526 | 1390261 | 241352 | 1.22 | 389 | unknown | 1/5 | structural-owed |  |  | full |
| A log path `.tdd/<leaf-name>.log` that is a directory: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the log is a directory; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins the `IsADirectoryError` traceback to the new line, since Green may not edit tests ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 107 | 38 | 74 | 11619 | 1566839 | 268122 | 1.35 | 355 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A log whose closing `result` record has no `usage` key: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the closing result record carries no usage; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins `KeyError: 'usage'` as a traceback to the new line, and the `no-usage-1` row of `tests/py/unit/test_harvest_usage.py` (which pins exit 1 for a closing result record with no `usage` key) to exit 2 with the new stderr line, since Green may not edit tests; rows for other missing keys (`no-num-turns-1`, `no-output-tokens-1`) stay as they are unless the fix changes their behaviour too, in which case Red moves them in the same way ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 323 | 0.35 |
| A log that is not valid UTF-8: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the log is not valid UTF-8; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins the `UnicodeDecodeError` traceback to the new line, since Green may not edit tests ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 124 | 0.40 |
| A log path `.tdd/<leaf-name>.log` that is a directory: `harvest-usage.sh <leaf-name>` exits 2, appends no usage event, prints no traceback, and prints exactly one stderr line naming `harvest-usage.sh`, the log path and that the log is a directory; a supervised leaf whose log is that leaves that line and no traceback on the supervisor's stderr. Red adds the case (in-process through `run_cli`, in `tests/py/unit/test_harvest_usage.py`) and moves the existing `tests/py/test_supervise.py` expectation that pins the `IsADirectoryError` traceback to the new line, since Green may not edit tests ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 99 | 0.41 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 26 | 1 | 25 | 25 | 26 | 26 | 0 | 0 | 25 | 0 | 0 | 25 | 25 | 27 | 1 | 25 | 0 | 25 | 24 | 25 | 0 | 0 | 0 | 1 |
| fast | 6 | 7 | 7 | 7 | 7 | 6 | 7 | 7 | 6 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 127 | 242 | 42149 | 5076349 | 1021943 | 5.52 |
