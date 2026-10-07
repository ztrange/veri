### 📊 Metrics — issue 1109

Wall time for the issue: 3139 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1115.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 35 | 26 | 4 | 8 | 2493 | 124639 | 93089 | 0.82 |
| red | 4 | 2 | 0 | 0 | 150 | 119 | 26 | 52 | 9379 | 1263273 | 186273 | 1.93 |
| green | 4 | 2 | 0 | 0 | 385 | 146 | 35 | 70 | 12523 | 1728890 | 181113 | 2.05 |
| refactor | 4 | 2 | 0 | 0 | 214 | 79 | 20 | 40 | 7019 | 899190 | 177678 | 1.74 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 8 | 7 | 1 | 0 | 461 | 192 | 43 | 86 | 16821 | 1944404 | 357552 | 3.59 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 323 | 178 | 42 | 84 | 14593 | 2071588 | 280601 | 2.95 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| add-ledger-step.sh, given a ledger ending in an `## Owed steps` section whose last bullet `- old` has no trailing newline and a batch past VERI_STEP_GROWTH, exits 1, leaves every pre-existing line byte-for-byte intact and appends each owed bullet on a line of its own after `- old` — a case watched failing on today's code, where it produces `- old- t` ⟦criterion 1⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 186 | 45 | 90 | 15512 | 2201021 | 277250 | 2.97 | 491 | unknown | 0/5 | nothing-left |  |  | full |
| add-ledger-step.sh, given a ledger whose very last line is an unterminated `## Owed steps` heading and a batch past VERI_STEP_GROWTH, exits 1, adds no second `## Owed steps` heading, and puts each owed bullet on a line of its own under the existing heading, every pre-existing line intact ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 36 | 72 | 13409 | 1690332 | 267814 | 2.75 | 447 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| add-ledger-step.sh, given a ledger ending in an `## Owed steps` section whose last bullet `- old` has no trailing newline and a batch past VERI_STEP_GROWTH, exits 1, leaves every pre-existing line byte-for-byte intact and appends each owed bullet on a line of its own after `- old` — a case watched failing on today's code, where it produces `- old- t` ⟦criterion 1⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 103 | 0.89 |
| add-ledger-step.sh, given a ledger whose very last line is an unterminated `## Owed steps` heading and a batch past VERI_STEP_GROWTH, exits 1, adds no second `## Owed steps` heading, and puts each owed bullet on a line of its own under the existing heading, every pre-existing line intact ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 111 | 0.85 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 2 |
| fast | 50 | 49 | 51 | 52 | 49 | 56 |  |  |  |  |  |
| target | 0 | 1 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 85 | 170 | 31414 | 4015992 | 638153 | 6.54 |
