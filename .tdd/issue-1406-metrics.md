### 📊 Metrics — issue 1406

Wall time for the issue: 6617 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1523.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 965 | 12193 | 41919 | 0.18 |
| red | 11 | 5 | 0 | 0 | 301 | 230 | 70 | 136 | 26406 | 3482130 | 541049 | 2.78 |
| green | 18 | 5 | 4 | 0 | 2964 | 373 | 108 | 216 | 35728 | 5508606 | 693382 | 4.62 |
| refactor | 9 | 4 | 0 | 0 | 384 | 101 | 40 | 74 | 9716 | 1648851 | 402737 | 1.87 |
| pin | 1 | 1 | 0 | 0 | 15 | 10 | 3 | 6 | 995 | 115784 | 43607 | 0.20 |
| rebase | 2 | 1 | 0 | 0 | 1174 | 42 | 14 | 28 | 4337 | 686458 | 92291 | 0.48 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 21 | 17 | 4 | 0 | 2576 | 326 | 102 | 200 | 34103 | 4770738 | 799740 | 4.02 |
| developer | claude-sonnet-5-5 | 14 | 0 | 0 | 0 | 1132 | 255 | 86 | 166 | 29030 | 4230375 | 680193 | 3.43 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 1142 | 183 | 48 | 96 | 15014 | 2452909 | 335052 | 2.68 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 5390 | 7.62 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The replaces-case green template states that deleting exactly the named cases is required for the step to pass, not merely permitted, and still forbids deleting or modifying any other case ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 91 | 31 | 60 | 9461 | 1414471 | 275843 | 1.34 | 524 | unknown | 0/5 | nothing-left |  |  | full |
| A develop-green prompt built for a `⟦replaces-case⟧` step carries the deletion requirement, pinned by a case in the prompt-builder tests ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 18 | 3251 | 425015 | 94775 | 0.45 | unknown | unknown | unknown | unknown |  |  | pin |
| A conductor-run check, given a `⟦replaces-case⟧` step's text, exits 0 when every case the step names is gone from its suite, and exits 1 naming each named case still present ⟦criterion 3⟧ | 17 | 5 | 3 | 0 | 0 | 0 | 313 | 100 | 194 | 34770 | 4904987 | 693350 | 4.32 | 1986 | 3/2 | 1/5 | nothing-left |  |  | full |
| A develop-green prompt rebuilt for a `⟦replaces-case⟧` step whose named cases survived the first green names those surviving cases as still owed for deletion ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 91 | 31 | 62 | 10065 | 1505873 | 283749 | 1.39 | 357 | unknown | 0/5 | nothing-left |  |  | full |
| SKILL.md says that before a `⟦replaces-case⟧` step's green goes to verify-green the conductor runs that check, and on survivors relaunches the green leaf naming them, records the relaunch as an event, and launches no verifier, pinned by a prose case that goes red without that paragraph ⟦criterion 3⟧ | 10 | 4 | 1 | 0 | 0 | 0 | 230 | 64 | 126 | 19635 | 3191483 | 425349 | 2.45 | 1097 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The replaces-case green template states that deleting exactly the named cases is required for the step to pass, not merely permitted, and still forbids deleting or modifying any other case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 97 | 0.42 |
| A conductor-run check, given a `⟦replaces-case⟧` step's text, exits 0 when every case the step names is gone from its suite, and exits 1 naming each named case still present ⟦criterion 3⟧ | 2 | 1/5 | nothing-left | PASS | 0 | 109 | 0.64 |
| A develop-green prompt rebuilt for a `⟦replaces-case⟧` step whose named cases survived the first green names those surviving cases as still owed for deletion ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 89 | 0.41 |
| SKILL.md says that before a `⟦replaces-case⟧` step's green goes to verify-green the conductor runs that check, and on survivors relaunches the green leaf naming them, records the relaunch as an event, and launches no verifier, pinned by a prose case that goes red without that paragraph ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 89 | 0.40 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 3 | 55 | 2 | 2 | 5 | 1 | 3 | 566 | 47 | 43 | 0 | 0 | 0 | 0 | 1 | 2 | 5 | 3 | 0 | 1 | 1 | 0 | 244 | 116 | 0 |
| fast | 56 | 56 | 61 | 55 | 57 | 60 | 58 | 56 | 57 | 55 | 57 | 56 | 57 | 56 | 58 | 56 | 56 | 58 | 62 | 63 | 63 |  |  |  |  |  |
| target | 2 | 1 | 1 | 0 | 2 | 1 | 0 | 56 | 2 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 560 | 560 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 236 | 462 | 78147 | 11454022 | 1814985 | 10.13 |
