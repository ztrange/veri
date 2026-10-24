### 📊 Metrics — issue 2209

Wall time for the issue: 1795 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 5 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2292.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.61 over 66 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89805 |
| 2 | $0.02 | 90255 |
| 3 | $0.03 | 92134 |
| 4 | $0.02 | 92425 |
| 5 | $0.03 | 93551 |
| 6 | $0.02 | 93900 |
| 7 | $0.02 | 94196 |
| 8 | $0.02 | 94438 |
| 9 | $0.02 | 94730 |
| 10 | $0.02 | 95363 |
| 11 | $0.04 | 98477 |
| 12 | $0.04 | 101218 |
| 13 | $0.02 | 101520 |
| 14 | $0.03 | 103303 |
| 15 | $0.03 | 104624 |
| 16 | $0.02 | 105049 |
| 17 | $0.03 | 105636 |
| 18 | $0.03 | 106199 |
| 19 | $0.03 | 107084 |
| 20 | $0.03 | 108535 |
| 21 | $0.03 | 109437 |
| 22 | $0.04 | 111130 |
| 23 | $0.03 | 111769 |
| 24 | $0.03 | 112380 |
| 25 | $0.03 | 113286 |
| 26 | $0.03 | 114571 |
| 27 | $0.03 | 115179 |
| 28 | $0.03 | 115963 |
| 29 | $0.03 | 116595 |
| 30 | $0.03 | 117150 |
| 31 | $0.03 | 117945 |
| 32 | $0.03 | 118368 |
| 33 | $0.03 | 119417 |
| 34 | $0.03 | 120133 |
| 35 | $0.04 | 121765 |
| 36 | $0.03 | 122454 |
| 37 | $0.04 | 123829 |
| 38 | $0.03 | 124445 |
| 39 | $0.03 | 125509 |
| 40 | $0.03 | 126386 |
| 41 | $0.04 | 128828 |
| 42 | $0.03 | 129445 |
| 43 | $0.03 | 129661 |
| 44 | $0.03 | 130045 |
| 45 | $0.04 | 131189 |
| 46 | $0.03 | 131867 |
| 47 | $0.04 | 133418 |
| 48 | $0.03 | 134050 |
| 49 | $0.04 | 135418 |
| 50 | $0.03 | 136343 |
| 51 | $0.03 | 137247 |
| 52 | $0.03 | 137639 |
| 53 | $0.03 | 137818 |
| 54 | $0.04 | 138950 |
| 55 | $0.04 | 140407 |
| 56 | $0.04 | 141497 |
| 57 | $0.03 | 141756 |
| 58 | $0.03 | 141930 |
| 59 | $0.03 | 142718 |
| 60 | $0.04 | 143676 |
| 61 | $0.03 | 143929 |
| 62 | $0.03 | 144409 |
| 63 | $0.03 | 145140 |
| 64 | $0.03 | 145678 |
| 65 | $0.03 | 145971 |
| 66 | $0.03 | 146357 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 2 | 4 | 846 | 31280 | 32457 | 0.09 |
| red | 7 | 3 | 0 | 0 | 148 | 95 | 26 | 50 | 8121 | 685547 | 136374 | 0.49 |
| green | 6 | 3 | 0 | 0 | 294 | 70 | 31 | 56 | 6625 | 792337 | 91446 | 0.37 |
| refactor | 4 | 1 | 0 | 0 | 78 | 37 | 15 | 26 | 3206 | 356293 | 63023 | 0.23 |
| pin | 1 | 1 | 0 | 0 | 20 | 11 | 3 | 6 | 955 | 76628 | 14636 | 0.05 |
| prose | 2 | 0 | 0 | 0 | 141 | 138 | 2 | 4 | 22374 | 1298 | 198333 | 0.72 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 234 | 83 | 30 | 60 | 6788 | 769844 | 146461 | 0.51 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 317 | 138 | 47 | 82 | 12965 | 1172241 | 191475 | 0.73 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `ledger-growth.sh <plan-ledger> <ledger>` exits 2, never 1, when a directory stands in the place of the record file `issue-<n>-added.md` beside the ledger (an `OSError` other than "no such file" reading it), and its stderr names that file — pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_growth.py over a ledger with an unrecorded new step ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 20 | 36 | 5338 | 483558 | 99787 | 0.35 | 240 | unknown | 0/5 | nothing-left |  |  | full |
| `ledger-growth.sh <plan-ledger> <ledger>` exits 2, never 1, when a directory stands in the place of `events.jsonl` beside the ledger (an `OSError` other than "no such file" reading it), and its stderr names that file — pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_growth.py over a ledger with an unrecorded new step ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 29 | 52 | 6383 | 744550 | 98807 | 0.39 | 268 | unknown | 1/5 | nothing-structural |  |  | full |
| With neither `issue-<n>-added.md` nor `events.jsonl` present beside the ledger, `ledger-growth.sh` still reads them as "no records": a new step without ⟦added⟧ exits 1 naming the step, never 2 — pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_growth.py ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 8 | 16 | 2991 | 229928 | 33460 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| `ledger-growth.sh` run with no arguments exits 2 and its usage line on stderr names the `plan-sha` subcommand beside `<plan-ledger-file> <ledger-file>` — pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_growth.py ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 44 | 18 | 34 | 4195 | 452769 | 73425 | 0.27 | 210 | unknown | 0/5 | nothing-left |  |  | full |
| skills/tdd/SKILL.md: bring the list of no-answer causes for `ledger-growth.sh` exit 2 in *Scope & plan* step 2 (around SKILL.md:661-664) up to GR-L5 in skills/tdd/REQUIREMENTS.md — "an unreadable ledger, plan file or record" — so the prose matches the row; the unit grades PASS against its whole list and is signed in skills/tdd/GRADED ⟦skill-edit⟧ ⟦criterion 3⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 63 | 1 | 2 | 10538 | 649 | 99167 | 0.35 | 93 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `ledger-growth.sh <plan-ledger> <ledger>` exits 2, never 1, when a directory stands in the place of the record file `issue-<n>-added.md` beside the ledger (an `OSError` other than "no such file" reading it), and its stderr names that file — pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_growth.py over a ledger with an unrecorded new step ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 12 | 0.06 |
| `ledger-growth.sh <plan-ledger> <ledger>` exits 2, never 1, when a directory stands in the place of `events.jsonl` beside the ledger (an `OSError` other than "no such file" reading it), and its stderr names that file — pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_growth.py over a ledger with an unrecorded new step ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 58 | 0.12 |
| `ledger-growth.sh` run with no arguments exits 2 and its usage line on stderr names the `plan-sha` subcommand beside `<plan-ledger-file> <ledger-file>` — pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_growth.py ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 2 | 1 | 1 | 2 | 3 | 3 | 1 | 1 | 4 | 3 | 3 | 3 | 4 | 4 | 3 |
| fast | 41 | 23 | 22 | 22 | 22 | 22 | 22 | 22 |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 3 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 79 | 146 | 42127 | 1943383 | 536269 | 1.96 |
