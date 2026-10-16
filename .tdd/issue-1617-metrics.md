### 📊 Metrics — issue 1617

Wall time for the issue: 1128 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1618.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 900 | 12309 | 35019 | 0.15 |
| red | 5 | 1 | 0 | 0 | 127 | 103 | 28 | 56 | 10908 | 1226026 | 201739 | 1.04 |
| green | 2 | 1 | 0 | 0 | 100 | 30 | 10 | 20 | 3433 | 407068 | 74245 | 0.37 |
| refactor | 2 | 1 | 0 | 0 | 61 | 18 | 6 | 12 | 1390 | 211106 | 72052 | 0.32 |
| pin | 3 | 3 | 0 | 0 | 57 | 40 | 12 | 24 | 4338 | 460751 | 109609 | 0.53 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 188 | 93 | 26 | 52 | 9626 | 980438 | 254462 | 1.21 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 168 | 106 | 31 | 62 | 11343 | 1336822 | 238202 | 1.20 |

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
| unreplaced-cases.sh counts a REPLACES: line as replacing a step's case when the reported name equals the step's name with every backslash escape removed (a `\` followed by `` ` ``, `"`, `$` or `\`), e.g. step name ``\`### 🔴 Red\` `` and report name `` `### 🔴 Red` ``, and exits 0 when that was the only case ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 86 | 25 | 50 | 8172 | 986042 | 224289 | 1.08 | 293 | unknown | 0/5 | nothing-left |  |  | full |
| unreplaced-cases.sh still counts a REPLACES: line whose name keeps the step's backslash escapes exactly as a replacement, exiting 0 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 9 | 18 | 3896 | 370170 | 77827 | 0.39 | unknown | unknown | unknown | unknown |  |  | pin |
| unreplaced-cases.sh still prints a step's case and exits 1 when the only REPLACES: line's name, with backslash escapes removed, differs from the step's name with backslash escapes removed ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 9 | 18 | 3625 | 375290 | 77300 | 0.38 | unknown | unknown | unknown | unknown |  |  | pin |
| replaces-case-survivors.sh still prints a step case named with backslash escapes when its suite's source still holds that case spelled with those same escapes ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 13 | 26 | 4376 | 573449 | 78229 | 0.41 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| unreplaced-cases.sh counts a REPLACES: line as replacing a step's case when the reported name equals the step's name with every backslash escape removed (a `\` followed by `` ` ``, `"`, `$` or `\`), e.g. step name ``\`### 🔴 Red\` `` and report name `` `### 🔴 Red` ``, and exits 0 when that was the only case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 61 | 0.32 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 1 | 0 | 1 |  |  |
| fast | 34 | 27 | 38 |  |  |  |  |  |
| target | 2 | 1 | 0 | 1 | 0 | 1 | 0 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 57 | 114 | 20969 | 2317260 | 492664 | 2.41 |
