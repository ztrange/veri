### 📊 Metrics — issue 1624

Wall time for the issue: 1860 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1701.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 14 | 3 | 6 | 1371 | 103089 | 34551 | 0.16 |
| red | 8 | 4 | 0 | 0 | 189 | 138 | 48 | 94 | 15978 | 1979081 | 307402 | 1.59 |
| green | 10 | 3 | 0 | 0 | 2381 | 286 | 80 | 156 | 23312 | 3382893 | 371191 | 2.62 |
| refactor | 6 | 3 | 0 | 0 | 237 | 79 | 31 | 62 | 8464 | 1235317 | 212867 | 1.06 |
| exhausted | 1 | 0 | 0 | 0 | 20 | 15 | 2 | 4 | 1177 | 55530 | 34438 | 0.31 |
| predicate | 1 | 0 | 0 | 0 | 13 | 9 | 3 | 6 | 841 | 100741 | 32181 | 0.15 |
| structural | 1 | 0 | 0 | 0 | 39 | 17 | 8 | 16 | 2065 | 330285 | 34177 | 0.19 |
| transform | 1 | 1 | 0 | 0 | 32 | 11 | 5 | 10 | 1085 | 189166 | 32930 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 533 | 186 | 67 | 130 | 19911 | 2552327 | 423342 | 2.15 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 1527 | 177 | 69 | 136 | 20067 | 2877691 | 409616 | 2.13 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 870 | 206 | 44 | 88 | 14315 | 1946084 | 226779 | 1.97 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 50 | 0.40 |
| green | 0 | 0.00 | 62 | 0.85 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 20 | 0.31 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `ledger-steps.sh has-mark` given no mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 225 | 57 | 114 | 17103 | 2524520 | 267303 | 1.74 | 1061 | 1/2 | 0/5 | nothing-left |  |  | full |
| `ledger-steps.sh has-mark ''` given an empty mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 100 | 40 | 76 | 11282 | 1575045 | 219889 | 1.15 | 1020 | unknown | 0/5 | nothing-left |  |  | full |
| the usage line `ledger-steps.sh` prints on a bad argument lists every verb the script accepts: current, last-done, current-or-last-done, next-phase, criterion <k> and has-mark <name> ⟦criterion 1⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 97 | 28 | 56 | 9932 | 1105590 | 216477 | 1.55 | unknown | 2/2 | unknown | unknown |  |  | full |
| the usage line `ledger-steps.sh` prints on a bad argument lists every verb the script accepts: current, last-done, current-or-last-done, next-phase, criterion <k> and has-mark <name>. The criterion reverses two existing exact pins of the old line, so this step's red also moves them to the new line `usage: ledger-steps.sh [current|last-done|current-or-last-done|next-phase|criterion <k>|has-mark <name>]`: the `cmp -s` at `skills/tdd/scripts/tests/ledger-steps.test.sh:53` and `USAGE` at `skills/tdd/scripts/tests/py/unit/test_ledger_steps.py:8` (green may not edit tests; coordinator ruling, #1621 shape) ⟦criterion 1⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 133 | 52 | 102 | 14605 | 2067858 | 321517 | 1.64 | 975 | unknown | 1/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `ledger-steps.sh has-mark` given no mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 59 | 0.32 |
| `ledger-steps.sh has-mark ''` given an empty mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 85 | 0.35 |
| the usage line `ledger-steps.sh` prints on a bad argument lists every verb the script accepts: current, last-done, current-or-last-done, next-phase, criterion <k> and has-mark <name>. The criterion reverses two existing exact pins of the old line, so this step's red also moves them to the new line `usage: ledger-steps.sh [current|last-done|current-or-last-done|next-phase|criterion <k>|has-mark <name>]`: the `cmp -s` at `skills/tdd/scripts/tests/ledger-steps.test.sh:53` and `USAGE` at `skills/tdd/scripts/tests/py/unit/test_ledger_steps.py:8` (green may not edit tests; coordinator ruling, #1621 shape) ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 93 | 0.39 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 600 | 0 | 1 | 2 | 0 | 0 | 15 | 1 | 0 | 606 | 0 | 0 | 0 | 1 | 1 | 1 | 2 | 0 | 1 | 2 | 0 | 601 | 2 | 2 | 1 | 0 | 1 | 15 | 1 | 16 |
| fast | 16 | 16 | 16 | 0 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 180 | 354 | 54293 | 7376102 | 1059737 | 6.24 |
