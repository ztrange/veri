### 📊 Metrics — issue 956

Wall time for the issue: 3884 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/985.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 15 | 3 | 6 | 1545 | 116478 | 42889 | 0.40 |
| red | 6 | 2 | 0 | 0 | 710 | 221 | 52 | 100 | 19659 | 2656834 | 295667 | 3.29 |
| green | 4 | 2 | 0 | 0 | 1000 | 116 | 37 | 72 | 11725 | 1816103 | 184526 | 2.07 |
| refactor | 4 | 2 | 0 | 0 | 299 | 62 | 19 | 36 | 5644 | 798656 | 176816 | 1.69 |
| pin | 2 | 2 | 0 | 0 | 303 | 48 | 10 | 20 | 3721 | 443367 | 85991 | 0.85 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 9 | 9 | 0 | 0 | 1255 | 196 | 53 | 102 | 18773 | 2341886 | 394211 | 4.00 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 1078 | 266 | 68 | 132 | 23521 | 3489552 | 391678 | 4.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `supervise.sh verdict-<phase> <cmd>` writes no `leaf-role:` line to stderr, while its exit code and its completion file `.tdd/verdict-<phase>.exit` are unchanged and it still appends no `launch` or `exit` event to `.tdd/events.jsonl` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 156 | 44 | 86 | 15036 | 2194687 | 284643 | 3.02 | 898 | unknown | 0/5 | nothing-left |  |  | full |
| `supervise.sh verdict-<phase> <cmd>` whose log holds no closing result record writes no `harvest-usage.sh:` line to stderr ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 140 | 44 | 82 | 13540 | 2003224 | 272181 | 2.85 | 946 | unknown | 0/5 | nothing-left |  |  | full |
| `supervise.sh` given a name that is neither a known role nor `verdict-*` (e.g. `bogus-x`) still writes the `leaf-role: … unknown leading word` diagnostic to stderr ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 14 | 28 | 6041 | 695896 | 93061 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |
| a `develop-*` or `verify-*` supervision whose log holds no closing result record still writes the `harvest-usage.sh: no closing result record` line to stderr ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 16 | 32 | 6132 | 821153 | 93115 | 1.03 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `supervise.sh verdict-<phase> <cmd>` writes no `leaf-role:` line to stderr, while its exit code and its completion file `.tdd/verdict-<phase>.exit` are unchanged and it still appends no `launch` or `exit` event to `.tdd/events.jsonl` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 152 | 0.85 |
| `supervise.sh verdict-<phase> <cmd>` whose log holds no closing result record writes no `harvest-usage.sh:` line to stderr ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 147 | 0.84 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 58 | 57 | 59 | 57 | 58 | 55 | 57 | 53 | 54 | 57 | 55 | 64 |
| fast | 48 | 48 | 50 | 44 | 43 | 46 |  |  |  |  |  |  |
| target | 63 | 54 | 56 | 71 | 60 | 55 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 121 | 234 | 42294 | 5831438 | 785889 | 8.30 |
