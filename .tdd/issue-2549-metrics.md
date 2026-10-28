### 📊 Metrics — issue 2549

Wall time for the issue: 4138 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2629.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.26 over 80 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 84177 tokens, largest 166673 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.53 | 84177 |
| 2 | $0.07 | 90797 |
| 3 | $0.04 | 93784 |
| 4 | $0.03 | 95445 |
| 5 | $0.02 | 96059 |
| 6 | $0.02 | 96780 |
| 7 | $0.02 | 97178 |
| 8 | $0.02 | 97441 |
| 9 | $0.02 | 97669 |
| 10 | $0.02 | 97940 |
| 11 | $0.02 | 98253 |
| 12 | $0.02 | 98906 |
| 13 | $0.02 | 99214 |
| 14 | $0.04 | 101279 |
| 15 | $0.04 | 103890 |
| 16 | $0.05 | 107464 |
| 17 | $0.03 | 108181 |
| 18 | $0.03 | 109397 |
| 19 | $0.02 | 109764 |
| 20 | $0.04 | 111776 |
| 21 | $0.03 | 112146 |
| 22 | $0.03 | 112896 |
| 23 | $0.03 | 113419 |
| 24 | $0.03 | 114061 |
| 25 | $0.03 | 114657 |
| 26 | $0.03 | 115893 |
| 27 | $0.03 | 116729 |
| 28 | $0.03 | 117295 |
| 29 | $0.03 | 118307 |
| 30 | $0.03 | 119057 |
| 31 | $0.03 | 119651 |
| 32 | $0.03 | 120271 |
| 33 | $0.03 | 121397 |
| 34 | $0.03 | 122298 |
| 35 | $0.03 | 123034 |
| 36 | $0.03 | 123716 |
| 37 | $0.03 | 124298 |
| 38 | $0.04 | 126102 |
| 39 | $0.03 | 127311 |
| 40 | $0.03 | 128208 |
| 41 | $0.04 | 129776 |
| 42 | $0.03 | 130596 |
| 43 | $0.04 | 131995 |
| 44 | $0.03 | 132945 |
| 45 | $0.04 | 134518 |
| 46 | $0.03 | 135280 |
| 47 | $0.04 | 136458 |
| 48 | $0.04 | 137521 |
| 49 | $0.03 | 137855 |
| 50 | $0.03 | 138239 |
| 51 | $0.04 | 139294 |
| 52 | $0.03 | 139935 |
| 53 | $0.04 | 141060 |
| 54 | $0.04 | 142185 |
| 55 | $0.05 | 144582 |
| 56 | $0.03 | 145288 |
| 57 | $0.03 | 145523 |
| 58 | $0.03 | 146144 |
| 59 | $0.03 | 146665 |
| 60 | $0.03 | 147067 |
| 61 | $0.04 | 148339 |
| 62 | $0.03 | 148965 |
| 63 | $0.03 | 149370 |
| 64 | $0.04 | 150536 |
| 65 | $0.09 | 158271 |
| 66 | $0.05 | 159985 |
| 67 | $0.04 | 160680 |
| 68 | $0.04 | 161914 |
| 69 | $0.04 | 162382 |
| 70 | $0.04 | 163142 |
| 71 | $0.04 | 163527 |
| 72 | $0.03 | 163787 |
| 73 | $0.03 | 163975 |
| 74 | $0.03 | 164213 |
| 75 | $0.04 | 164761 |
| 76 | $0.04 | 165572 |
| 77 | $0.03 | 165788 |
| 78 | $0.04 | 166053 |
| 79 | $0.04 | 166376 |
| 80 | $0.04 | 166673 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 948 | 0 | 33935 | 0.09 |
| red | 5 | 2 | 0 | 0 | 205 | 104 | 29 | 58 | 8638 | 978446 | 127881 | 0.50 |
| green | 4 | 2 | 0 | 0 | 349 | 68 | 21 | 42 | 5177 | 651608 | 72185 | 0.30 |
| refactor | 3 | 1 | 0 | 0 | 91 | 25 | 8 | 16 | 1579 | 215449 | 48736 | 0.16 |
| cover | 1 | 0 | 0 | 0 | 32 | 13 | 5 | 10 | 1038 | 146524 | 16178 | 0.07 |
| structural | 1 | 0 | 0 | 0 | 47 | 25 | 5 | 10 | 887 | 142635 | 14125 | 0.06 |
| pin | 1 | 1 | 0 | 0 | 31 | 15 | 4 | 8 | 1359 | 115345 | 17682 | 0.07 |
| prose | 5 | 0 | 0 | 0 | 531 | 516 | 5 | 10 | 81419 | 110374 | 419780 | 1.87 |
| skill-edit | 1 | 0 | 0 | 0 | 13 | 10 | 3 | 6 | 791 | 245977 | 123809 | 0.34 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 347 | 94 | 22 | 44 | 6842 | 587713 | 134060 | 0.46 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 419 | 164 | 51 | 102 | 12784 | 1662294 | 196662 | 0.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With `.tdd/stop` holding `at-leaf`, `supervise.sh <leaf> …` starts no leaf process: it exits 2, writes `2` to `.tdd/<leaf>.exit`, writes no `.tdd/<leaf>.pid`, appends a `launch-refused` event naming the stop, and prints `supervise: refusing to launch <leaf>: a stop (at-leaf) is pending` on stderr; reproduced by a case in `skills/tdd/scripts/tests/py/test_supervise.py` ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 77 | 23 | 46 | 6117 | 747689 | 120371 | 0.44 | 418 | unknown | 0/5 | nothing-left |  |  | full |
| With `.tdd/stop` holding `now`, `supervise.sh <leaf> …` likewise starts no leaf process: exit 2, `2` in `.tdd/<leaf>.exit`, no `.tdd/<leaf>.pid`, a `launch-refused` event naming the stop, and `supervise: refusing to launch <leaf>: a stop (now) is pending` on stderr; reproduced by a case in `skills/tdd/scripts/tests/py/test_supervise.py` ⟦criterion 1⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 130 | 37 | 74 | 8437 | 1107033 | 136300 | 0.54 | 599 | unknown | 1/5 | nothing-left |  |  | full |
| With `.tdd/stop` holding `at-ledger`, `supervise.sh <leaf> …` launches the leaf as today (exit and completion file are the leaf's own, a `.tdd/<leaf>.pid` is written, no `launch-refused` event), as it already does with no `.tdd/stop`; reproduced by a case in `skills/tdd/scripts/tests/py/test_supervise.py` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 12 | 24 | 4124 | 395285 | 40116 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| skill-edit step for the unit `skills/tdd/SKILL.md#Launching a leaf — detach, then wait in the foreground`: row LL17 in `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md` is rewritten in place exactly as the issue's `## Requirements` states it (one row rewritten, none added), and the *Launching a leaf* paragraph on reading a leaf's exit 2 says that a pending `at-leaf` or `now` stop makes `supervise.sh` refuse the launch with exit 2, that either pending mode explains the 2 and routes the run to *Stopping* instead of a bail, and that any other answer leaves the 2 to be read as the phase reads it; the unit grades PASS against its whole list and is signed in `skills/tdd/GRADED` inside this step ⟦skill-edit⟧ ⟦criterion 2⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 425 | 7 | 14 | 66609 | 355702 | 438185 | 1.80 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With `.tdd/stop` holding `at-leaf`, `supervise.sh <leaf> …` starts no leaf process: it exits 2, writes `2` to `.tdd/<leaf>.exit`, writes no `.tdd/<leaf>.pid`, appends a `launch-refused` event naming the stop, and prints `supervise: refusing to launch <leaf>: a stop (at-leaf) is pending` on stderr; reproduced by a case in `skills/tdd/scripts/tests/py/test_supervise.py` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.05 |
| With `.tdd/stop` holding `now`, `supervise.sh <leaf> …` likewise starts no leaf process: exit 2, `2` in `.tdd/<leaf>.exit`, no `.tdd/<leaf>.pid`, a `launch-refused` event naming the stop, and `supervise: refusing to launch <leaf>: a stop (now) is pending` on stderr; reproduced by a case in `skills/tdd/scripts/tests/py/test_supervise.py` ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 80 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 16 | 18 | 18 | 18 | 15 | 14 | 15 | 14 | 17 | 16 | 18 |
| fast | 38 | 39 | 31 | 31 | 38 |  |  |  |  |  |  |  |
| target | 5 | 4 | 5 | 5 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 162 | 101836 | 2606358 | 874311 | 6.73 (estimate) |
