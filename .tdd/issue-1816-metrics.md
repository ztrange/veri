### 📊 Metrics — issue 1816

Wall time for the issue: 1455 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1849.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 36 | 33 | 3 | 6 | 1736 | 65042 | 26621 | 0.09 |
| red | 5 | 2 | 0 | 0 | 138 | 120 | 22 | 40 | 8058 | 584787 | 88406 | 0.36 |
| green | 4 | 2 | 0 | 0 | 97 | 64 | 19 | 32 | 4923 | 432788 | 55137 | 0.23 |
| refactor | 4 | 2 | 0 | 0 | 86 | 66 | 22 | 38 | 4878 | 563450 | 62939 | 0.26 |
| diff | 2 | 1 | 0 | 0 | 130 | 33 | 13 | 24 | 2903 | 328031 | 26026 | 0.13 |
| pin | 1 | 1 | 0 | 0 | 18 | 14 | 4 | 8 | 1261 | 106547 | 13925 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 265 | 173 | 36 | 72 | 11624 | 945975 | 138213 | 0.56 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 240 | 157 | 47 | 76 | 12135 | 1134670 | 134841 | 0.57 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| stop-reason.sh on an issue whose run directory .tdd/wt/<n> exists but holds no .tdd/events.jsonl exits 2 with a stderr diagnostic naming that missing events log, nothing on stdout and no traceback (a small in-process run_cli case in tests/py/unit/test_stop_reason.py; the shim's exit line and SCRIPTS.md's stop-reason entry name this exit 2) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 122 | 27 | 48 | 7260 | 675469 | 91287 | 0.37 | 242 | unknown | 0/5 | nothing-left |  |  | full |
| stop-reason.sh's shim header exit line and its SCRIPTS.md entry name the missing events log as an exit 2 case ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 13 | 24 | 2903 | 328031 | 26026 | 0.13 | 163 | n/a | n/a | n/a |  |  | full |
| stop-reason.sh on a run with no end event and no live conductor whose .tdd/conductor-<n>.log holds no result record exits 2 with a stderr diagnostic naming that log and the missing result record, nothing on stdout and no traceback (a small in-process run_cli case in tests/py/unit/test_stop_reason.py; the shim's exit line and SCRIPTS.md's stop-reason entry name this exit 2) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 101 | 32 | 54 | 8720 | 787363 | 97092 | 0.41 | 213 | unknown | 1/5 | nothing-left |  |  | full |
| Pin, as a regression case, that stop-reason.sh on a run whose .tdd/conductor.pid names a process that is no longer alive, with no end event in the events log, does not print running but falls through to the usage-limit/unknown report: the behaviour already exists (the liveness gate in stop_reason.py), so this step adds no production code — its Red reports AGAINST_UNMODIFIED: PASSES and the pin is watched to fail under verify-pin's mutation of that gate (a small in-process run_cli case in tests/py/unit/test_stop_reason.py starting no process) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 8 | 16 | 3140 | 224740 | 32028 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| stop-reason.sh on an issue whose run directory .tdd/wt/<n> exists but holds no .tdd/events.jsonl exits 2 with a stderr diagnostic naming that missing events log, nothing on stdout and no traceback (a small in-process run_cli case in tests/py/unit/test_stop_reason.py; the shim's exit line and SCRIPTS.md's stop-reason entry name this exit 2) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.11 |
| stop-reason.sh on a run with no end event and no live conductor whose .tdd/conductor-<n>.log holds no result record exits 2 with a stderr diagnostic naming that log and the missing result record, nothing on stdout and no traceback (a small in-process run_cli case in tests/py/unit/test_stop_reason.py; the shim's exit line and SCRIPTS.md's stop-reason entry name this exit 2) ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 52 | 0.16 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 0 | 1 | 41 | 42 | 0 | 0 | 1 | 1 | 1 | 0 |
| fast | 5 | 5 | 4 | 4 | 5 | 5 | 5 |  |  |  |  |  |  |
| target | 5 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 83 | 148 | 23759 | 2080645 | 273054 | 1.13 |
