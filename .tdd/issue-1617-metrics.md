### 📊 Metrics — issue 1617

Wall time for the issue: 756 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1618.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 900 | 12309 | 35019 | 0.15 |
| red | 8 | 2 | 0 | 0 | 198 | 159 | 43 | 84 | 17466 | 1811371 | 321649 | 1.64 |
| green | 4 | 2 | 0 | 0 | 207 | 62 | 20 | 40 | 6602 | 815345 | 147410 | 0.74 |
| refactor | 4 | 2 | 0 | 0 | 127 | 40 | 12 | 24 | 2668 | 422719 | 144538 | 0.65 |
| pin | 4 | 4 | 0 | 0 | 95 | 67 | 18 | 36 | 7253 | 718507 | 152133 | 0.75 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 11 | 0 | 0 | 352 | 162 | 44 | 88 | 16499 | 1695795 | 406108 | 1.96 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 286 | 174 | 50 | 98 | 18390 | 2084456 | 394641 | 1.97 |

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
| unreplaced-cases.sh counts each backslash escape on its own: a step name containing `\"`, one containing `\$` and one containing `\\` each count as replaced, exiting 0, when the REPLACES: name spells that escape removed (`"`, `$`, `\`) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 11 | 22 | 5607 | 475412 | 84672 | 0.44 | unknown | unknown | unknown | unknown |  |  | pin |
| unreplaced-cases.sh unescapes only the step's name, never the REPLACES: name: for step name `a\\$b` the REPLACES: name `a\$b` counts as replaced, exiting 0, while a REPLACES: name keeping the step's escapes exactly still counts ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 26 | 50 | 8313 | 987579 | 223413 | 1.08 | 290 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| unreplaced-cases.sh counts a REPLACES: line as replacing a step's case when the reported name equals the step's name with every backslash escape removed (a `\` followed by `` ` ``, `"`, `$` or `\`), e.g. step name ``\`### 🔴 Red\` `` and report name `` `### 🔴 Red` ``, and exits 0 when that was the only case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 61 | 0.32 |
| unreplaced-cases.sh unescapes only the step's name, never the REPLACES: name: for step name `a\\$b` the REPLACES: name `a\$b` counts as replaced, exiting 0, while a REPLACES: name keeping the step's escapes exactly still counts ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 66 | 0.32 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 2 |  |  |  |  |  |  |  |  |
| fast | 34 | 27 | 38 | 30 | 33 | 37 |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 94 | 186 | 34889 | 3780251 | 800749 | 3.93 |
