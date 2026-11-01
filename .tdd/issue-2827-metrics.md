### 📊 Metrics — issue 2827

Wall time for the issue: 3935 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2839.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.95 over 40 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87704 tokens, largest 110891 tokens
Conductor context: first turn 87689 tokens, largest 161089 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87704 |
| 2 | $0.10 | 96008 |
| 3 | $0.06 | 98288 |
| 4 | $0.04 | 99043 |
| 5 | $0.03 | 99420 |
| 6 | $0.05 | 101168 |
| 7 | $0.06 | 103985 |
| 8 | $0.05 | 106506 |
| 9 | $0.07 | 109655 |
| 10 | $0.04 | 110891 |
| 11 | $0.56 | 87689 |
| 12 | $0.08 | 95917 |
| 13 | $0.04 | 97976 |
| 14 | $0.03 | 98967 |
| 15 | $0.03 | 100441 |
| 16 | $0.03 | 101152 |
| 17 | $0.04 | 103041 |
| 18 | $0.06 | 107391 |
| 19 | $0.12 | 119264 |
| 20 | $0.05 | 122389 |
| 21 | $0.04 | 124842 |
| 22 | $0.04 | 126376 |
| 23 | $0.03 | 127446 |
| 24 | $0.04 | 129630 |
| 25 | $0.06 | 134152 |
| 26 | $0.04 | 135233 |
| 27 | $0.10 | 143764 |
| 28 | $0.04 | 145550 |
| 29 | $0.05 | 147912 |
| 30 | $0.04 | 149785 |
| 31 | $0.04 | 151622 |
| 32 | $0.04 | 152568 |
| 33 | $0.05 | 154949 |
| 34 | $0.05 | 157234 |
| 35 | $0.04 | 158223 |
| 36 | $0.04 | 159022 |
| 37 | $0.03 | 159234 |
| 38 | $0.04 | 160128 |
| 39 | $0.04 | 161089 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 3 | 6 | 1276 | 66159 | 34338 | 0.11 |
| red | 4 | 1 | 0 | 0 | 185 | 85 | 16 | 32 | 8328 | 464019 | 95424 | 0.37 |
| pin | 2 | 2 | 0 | 0 | 68 | 34 | 10 | 20 | 3115 | 294712 | 35445 | 0.15 |
| green | 4 | 1 | 1 | 0 | 416 | 69 | 22 | 42 | 6583 | 647942 | 58435 | 0.28 |
| refactor | 2 | 1 | 0 | 0 | 93 | 22 | 7 | 14 | 1606 | 194098 | 30168 | 0.11 |
| prose | 3 | 0 | 0 | 0 | 99 | 84 | 3 | 6 | 12801 | 3681 | 134392 | 0.46 |
| skill-edit | 1 | 0 | 0 | 0 | 25 | 18 | 5 | 10 | 677 | 269977 | 45960 | 0.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 448 | 110 | 32 | 64 | 9751 | 930868 | 122626 | 0.50 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 331 | 114 | 26 | 50 | 11157 | 736062 | 131184 | 0.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 416 | 0.28 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A record whose mutated run exits non-zero and still prints a line the unmutated run printed (a real test failure) still counts as red: pin-recheck.sh prints nothing needing a look and exits 0, as today. A case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py with a real process and no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 9 | 18 | 4350 | 256615 | 58326 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| A record whose mutated run exits non-zero and prints none of the output lines the unmutated run printed, where the unmutated run printed at least one line, prints `needs a look: <file> (mutation did not build)` on stdout and pin-recheck.sh exits 1, the recorded file restored byte for byte. A case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py with a real process; a record whose unmutated run prints nothing keeps counting as red, as the existing cases pin ⟦criterion 1⟧ | 10 | 4 | 1 | 0 | 0 | 0 | 159 | 46 | 90 | 15282 | 1344156 | 161146 | 0.69 | 962 | unknown | 1/5 | nothing-structural |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A record whose mutated run exits non-zero and prints none of the output lines the unmutated run printed, where the unmutated run printed at least one line, prints `needs a look: <file> (mutation did not build)` on stdout and pin-recheck.sh exits 1, the recorded file restored byte for byte. A case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py with a real process; a record whose unmutated run prints nothing keeps counting as red, as the existing cases pin ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 93 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 9 | 8 | 12 | 8 | 6 | 9 | 9 |
| target | 4 | 4 | 5 | 6 | 6 | 4 | 5 | 8 |  |
| fast | 42 | 39 | 41 | 35 | 44 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 66 | 130 | 34386 | 1940588 | 434162 | 4.58 (estimate) |
