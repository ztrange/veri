### 📊 Metrics — issue 1624

Wall time for the issue: 2355 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 14 | 3 | 6 | 1371 | 103089 | 34551 | 0.16 |
| red | 6 | 3 | 0 | 0 | 146 | 108 | 38 | 76 | 12298 | 1614584 | 229512 | 1.20 |
| green | 8 | 2 | 0 | 0 | 1700 | 252 | 67 | 130 | 20110 | 2853318 | 300713 | 2.26 |
| refactor | 4 | 2 | 0 | 0 | 144 | 47 | 18 | 36 | 4732 | 681723 | 139006 | 0.67 |
| exhausted | 1 | 0 | 0 | 0 | 20 | 15 | 2 | 4 | 1177 | 55530 | 34438 | 0.31 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 406 | 130 | 46 | 90 | 14113 | 1775635 | 283153 | 1.45 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 753 | 100 | 38 | 74 | 11260 | 1586525 | 228288 | 1.18 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 870 | 206 | 44 | 88 | 14315 | 1946084 | 226779 | 1.97 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 50 | 0.40 |
| green | 0 | 0.00 | 62 | 0.85 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 20 | 0.31 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `ledger-steps.sh has-mark` given no mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 225 | 57 | 114 | 17103 | 2524520 | 267303 | 1.74 | 1061 | 1/2 | 0/5 | nothing-left |  |  | full |
| `ledger-steps.sh has-mark ''` given an empty mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 100 | 40 | 76 | 11282 | 1575045 | 219889 | 1.15 | 1020 | unknown | 0/5 | nothing-left |  |  | full |
| the usage line `ledger-steps.sh` prints on a bad argument lists every verb the script accepts: current, last-done, current-or-last-done, next-phase, criterion <k> and has-mark <name> ⟦criterion 1⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 97 | 28 | 56 | 9932 | 1105590 | 216477 | 1.55 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `ledger-steps.sh has-mark` given no mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 59 | 0.32 |
| `ledger-steps.sh has-mark ''` given an empty mark name exits 2, prints on stderr a usage line that lists `has-mark <name>`, and prints no Python traceback ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 85 | 0.35 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 600 | 0 | 1 | 2 | 0 | 0 | 15 | 1 | 0 | 606 | 0 | 0 | 0 | 1 | 1 | 1 | 2 | 0 | 1 |
| fast | 16 | 16 | 16 | 0 | 16 | 16 | 16 | 16 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 128 | 252 | 39688 | 5308244 | 738220 | 4.60 |
