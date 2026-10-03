### 📊 Metrics — issue 717

Wall time for the issue: 3561 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 9 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/780.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 3 | 6 | 1474 | 118598 | 43224 | 0.40 |
| red | 10 | 3 | 0 | 0 | 489 | 386 | 83 | 164 | 37236 | 4396302 | 509696 | 5.70 |
| green | 8 | 3 | 1 | 0 | 1021 | 341 | 78 | 154 | 34569 | 4317185 | 385465 | 4.64 |
| refactor | 6 | 3 | 0 | 0 | 272 | 106 | 30 | 60 | 9943 | 1373719 | 279114 | 2.71 |
| pin | 4 | 4 | 0 | 0 | 154 | 115 | 21 | 42 | 9532 | 961592 | 179998 | 1.82 |
| diff | 4 | 2 | 0 | 0 | 128 | 64 | 17 | 34 | 6456 | 774807 | 185085 | 1.76 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 17 | 16 | 1 | 0 | 1137 | 491 | 109 | 218 | 45914 | 5400488 | 764609 | 8.12 |
| developer | claude-opus-5-5 | 16 | 0 | 0 | 0 | 948 | 537 | 123 | 242 | 53296 | 6541715 | 817973 | 8.92 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 555 | 2.43 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| veri.harvest_usage.main([]) returns 2 with exactly `usage: harvest-usage.sh <leaf-name>` on stderr and nothing on stdout (tests/py/test_harvest_usage.py), and harvest-usage.sh is removed from migration slice 3's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 2749 | 397883 | 87065 | 0.83 | 460 | unknown | 0/5 | nothing-structural |  |  | full |
| veri.harvest_usage.main([<name>]), run in a directory whose .tdd/<name>.log ends in a closing result record, calls event.sh once as `usage` with the eight numbers, model= and the actor/phase/attempt leaf_role derives from the name in its environment, and returns 0; and harvest-usage.sh is a /bin/sh shim that execs python3 on veri/harvest_usage.py once per invocation, holding no Python source, keeping its lowercase `usage: harvest-usage.sh <leaf-name>` header line and citing no issue number in any comment; every case in tests/harvest-usage.test.sh passes with its assertions unmodified, the commit touching that suite only in copy lines and stub libs ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 335 | 72 | 140 | 32361 | 3935410 | 385529 | 4.52 | 823 | 1/2 | 0/5 | nothing-left |  |  | full |
| harvest-usage.sh, run through a symlink to the skill directory and from another working directory, appends the same usage event and exits as when run in place (a case in tests/harvest-usage.test.sh) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 93 | 15 | 30 | 9447 | 812040 | 103482 | 1.18 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/harvest-usage.test.sh holds a case per exit code it lacks: no `.tdd/<name>.log` exits 1 with no usage event appended, a log with no closing result record exits 3, and no argument exits 2 with exactly `usage: harvest-usage.sh <leaf-name>` on stderr ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 15 | 30 | 6336 | 811052 | 100207 | 1.09 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_harvest_usage.py asserts through veri.harvest_usage.main what 'a closing result record whose modelUsage lists one model: the usage event carries a model key naming that model' and 'a closing result record whose modelUsage names two models: the usage event's model key lists every one of them' assert, faking only the event.sh subprocess call ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 14 | 28 | 5547 | 711671 | 97633 | 1.03 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_harvest_usage.py asserts through veri.harvest_usage.main what 'a closing result record whose modelUsage names two models: the usage event keeps each model's own token and cost figures alongside the sums' and 'a closing result record with no modelUsage: the harvester still appends a usage event, its model key empty, and exits 0 with nothing on stderr' assert — model_usage= passed only when the record has modelUsage ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 13 | 26 | 6016 | 646229 | 93887 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_harvest_usage.py pins the ported quirks through veri.harvest_usage.main: an unknown leaf name with a log holding no closing record returns 3 and with no log file returns 1, never 2; a closing record missing `usage` or one of the eight keys returns 1, not 2; the closing record is the last `type: result` record even when a later non-record line follows it; each number reaches event.sh as Python's %s of the parsed value; the no-record diagnostic is `harvest-usage.sh: no closing result record in .tdd/<name>.log — no usage event appended for <name>` ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 179 | 44 | 88 | 17317 | 2250700 | 302928 | 3.22 | 502 | unknown | 0/5 | nothing-left |  |  | full |
| tests/harvest-usage.test.sh keeps only the floor and survivors — the exit-0 'a finished leaf …' case, the exit-2 'a leaf name leaf-role.sh refuses …' case, the no-record case, the exit-1, exit-3 and no-argument cases and the symlink case — with the four modelUsage cases replaced by tests/py/test_harvest_usage.py removed, and no remaining case's assertions changed ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 11 | 22 | 4439 | 545576 | 103820 | 1.03 | 85 | unknown | unknown | unknown |  |  | full |
| skills/tdd/scripts/veri/leaf_log.py, tests/supervise.test.sh, tests/supervise-retry.test.sh, tests/unit/emitted-text.test.sh and tests/unit/comment-class.test.sh are unchanged by the branch, and tests/unit/missing-argument-exit.test.sh is changed only by the removal of harvest-usage.sh from migration slice 3's list ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 18 | 6 | 12 | 2017 | 229231 | 81265 | 0.74 | 85 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.harvest_usage.main([]) returns 2 with exactly `usage: harvest-usage.sh <leaf-name>` on stderr and nothing on stdout (tests/py/test_harvest_usage.py), and harvest-usage.sh is removed from migration slice 3's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 94 | 0.83 |
| veri.harvest_usage.main([<name>]), run in a directory whose .tdd/<name>.log ends in a closing result record, calls event.sh once as `usage` with the eight numbers, model= and the actor/phase/attempt leaf_role derives from the name in its environment, and returns 0; and harvest-usage.sh is a /bin/sh shim that execs python3 on veri/harvest_usage.py once per invocation, holding no Python source, keeping its lowercase `usage: harvest-usage.sh <leaf-name>` header line and citing no issue number in any comment; every case in tests/harvest-usage.test.sh passes with its assertions unmodified, the commit touching that suite only in copy lines and stub libs ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 95 | 0.95 |
| tests/py/test_harvest_usage.py pins the ported quirks through veri.harvest_usage.main: an unknown leaf name with a log holding no closing record returns 3 and with no log file returns 1, never 2; a closing record missing `usage` or one of the eight keys returns 1, not 2; the closing record is the last `type: result` record even when a later non-record line follows it; each number reaches event.sh as Python's %s of the parsed value; the no-record diagnostic is `harvest-usage.sh: no closing result record in .tdd/<name>.log — no usage event appended for <name>` ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.93 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 0 | 3 | 1 | 5 | 0 | 11 | 17 | 8 | 1 | 1 | 3 | 59 | 2 | 3 | 3 | 3 | 3 | 0 | 1 | 1 | 0 | 1 | 4 | 3 | 3 | 1 | 37 |
| fast | 49 | 44 | 40 | 41 | 41 | 40 | 40 | 40 | 36 | 36 | 35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 2 | 2 | 3 | 3 | 3 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 232 | 460 | 99210 | 11942203 | 1582582 | 17.04 |
