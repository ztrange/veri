### 📊 Metrics — issue 2517

Wall time for the issue: 1246 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.59 over 61 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89269 tokens, largest 159194 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89269 |
| 2 | $0.02 | 89645 |
| 3 | $0.03 | 91563 |
| 4 | $0.03 | 93523 |
| 5 | $0.02 | 93818 |
| 6 | $0.02 | 94229 |
| 7 | $0.02 | 94487 |
| 8 | $0.02 | 94796 |
| 9 | $0.02 | 95019 |
| 10 | $0.02 | 95291 |
| 11 | $0.03 | 96125 |
| 12 | $0.02 | 96494 |
| 13 | $0.05 | 100621 |
| 14 | $0.04 | 102615 |
| 15 | $0.02 | 103027 |
| 16 | $0.03 | 103801 |
| 17 | $0.03 | 104377 |
| 18 | $0.03 | 104988 |
| 19 | $0.02 | 105431 |
| 20 | $0.04 | 107436 |
| 21 | $0.03 | 108558 |
| 22 | $0.04 | 110977 |
| 23 | $0.03 | 111722 |
| 24 | $0.02 | 112033 |
| 25 | $0.03 | 112696 |
| 26 | $0.03 | 113478 |
| 27 | $0.03 | 114011 |
| 28 | $0.03 | 114662 |
| 29 | $0.03 | 115260 |
| 30 | $0.03 | 115835 |
| 31 | $0.03 | 116559 |
| 32 | $0.03 | 117318 |
| 33 | $0.03 | 118026 |
| 34 | $0.03 | 118789 |
| 35 | $0.03 | 119475 |
| 36 | $0.03 | 120180 |
| 37 | $0.04 | 121637 |
| 38 | $0.03 | 122947 |
| 39 | $0.03 | 123661 |
| 40 | $0.09 | 131413 |
| 41 | $0.03 | 132485 |
| 42 | $0.04 | 134298 |
| 43 | $0.03 | 134929 |
| 44 | $0.04 | 135997 |
| 45 | $0.03 | 136832 |
| 46 | $0.04 | 138529 |
| 47 | $0.04 | 139882 |
| 48 | $0.04 | 141101 |
| 49 | $0.03 | 141713 |
| 50 | $0.04 | 143086 |
| 51 | $0.04 | 144160 |
| 52 | $0.04 | 145141 |
| 53 | $0.04 | 145970 |
| 54 | $0.04 | 147487 |
| 55 | $0.04 | 148251 |
| 56 | $0.04 | 150001 |
| 57 | $0.04 | 151392 |
| 58 | $0.04 | 152622 |
| 59 | $0.04 | 153552 |
| 60 | $0.04 | 154412 |
| 61 | $0.07 | 159194 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 2 | 4 | 1145 | 33927 | 34704 | 0.10 |
| red | 7 | 2 | 1 | 0 | 151 | 121 | 30 | 58 | 12663 | 895707 | 164092 | 0.72 |
| pin | 2 | 2 | 0 | 0 | 36 | 25 | 9 | 18 | 2766 | 261488 | 34126 | 0.14 |
| green | 7 | 0 | 3 | 0 | 505 | 184 | 46 | 92 | 17018 | 1565289 | 148602 | 0.96 |
| red-missing | 1 | 0 | 0 | 0 | 23 | 18 | 4 | 8 | 2189 | 131460 | 24441 | 0.10 |
| exhausted | 1 | 0 | 0 | 0 | 24 | 21 | 4 | 8 | 1871 | 116387 | 18933 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 5 | 4 | 0 | 230 | 121 | 32 | 64 | 12032 | 903004 | 157160 | 0.60 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 359 | 164 | 42 | 82 | 16466 | 1427727 | 180770 | 0.91 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 162 | 94 | 21 | 42 | 9154 | 673527 | 86968 | 0.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 95 | 0.47 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 505 | 0.96 |
| red-missing | 0 | 0.00 | 23 | 0.10 |
| exhausted | 0 | 0.00 | 24 | 0.16 |
| verify-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| add-ledger-step.sh still accepts, unmarked, a step whose text adds a case for behaviour that already holds (the pin step of SKILL.md:606-609): it exits 0 and inserts the step, pinned by a small case in tests/py/unit/test_add_ledger_step.py ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 10 | 18 | 4375 | 271411 | 60459 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| add-ledger-step.sh still accepts a step whose text describes a change confined to test files when the step is marked ⟦diff-checked⟧: it exits 0 and inserts the step, pinned by a small case in tests/py/unit/test_add_ledger_step.py ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 10 | 20 | 3671 | 315765 | 40045 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| add-ledger-step.sh exits 2, writing nothing to the ledger and a refusal naming PL18 and the ⟦diff-checked⟧ marker on stderr, when a step text it is given describes a change confined to test files (for example a timeout bound inside a test helper) and the step is not marked ⟦diff-checked⟧; reproduced by a small case in tests/py/unit/test_add_ledger_step.py that fails on the current code ⟦criterion 1⟧ | 14 | 2 | 4 | 0 | 0 | 0 | 299 | 73 | 146 | 28461 | 2383155 | 289690 | 1.68 | unknown | green 2/2, red 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 |
| target | 1 | 2 | 1 | 1 | 2 | 1 | 0 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 16 | 16 | 17 | 17 | 16 | 17 | 17 | 17 | 16 | 17 | 16 | 17 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 95 | 188 | 37652 | 3004258 | 424898 | 4.76 (estimate) |
