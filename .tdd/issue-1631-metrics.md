### 📊 Metrics — issue 1631

Wall time for the issue: 1854 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1764.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 5 | 1 | 2 | 642 | 0 | 30063 | 0.08 |
| red | 6 | 2 | 0 | 0 | 154 | 113 | 35 | 70 | 13307 | 1090358 | 176670 | 0.68 |
| green | 6 | 2 | 1 | 0 | 299 | 118 | 33 | 62 | 10759 | 906462 | 105714 | 0.61 |
| refactor | 4 | 2 | 0 | 0 | 100 | 43 | 15 | 30 | 3535 | 416898 | 59246 | 0.23 |
| pin | 2 | 2 | 0 | 0 | 34 | 25 | 9 | 18 | 2927 | 249397 | 30836 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 292 | 116 | 39 | 78 | 11740 | 1041323 | 172666 | 0.65 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 199 | 129 | 41 | 80 | 14606 | 1270446 | 176689 | 0.71 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 105 | 59 | 13 | 24 | 4824 | 351346 | 53174 | 0.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 215 | 0.47 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| An `add-ledger-step.sh … instead-of` replacing an `⟦added⟧` step with one text, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, exits 0 and replaces the step, leaving the `⟦added⟧` count unchanged and filing nothing under `## Owed steps` (a small pytest case driving the module in-process) ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 128 | 38 | 74 | 11903 | 1058513 | 155139 | 0.76 | 412 | 1/2 | 0/5 | nothing-left |  |  | full |
| An `add-ledger-step.sh` call whose one new non-repair text carries a newline, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, is refused: exit 1, the ledger's steps unchanged and the text filed under `## Owed steps`, counted as one added step as main counted it (a small pytest case driving the module in-process) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 101 | 32 | 62 | 10442 | 907522 | 139892 | 0.55 | 299 | unknown | 1/5 | nothing-left |  |  | full |
| An `add-ledger-step.sh` call whose one new non-repair text carries a `⟦criterion k⟧` tag, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, is refused: exit 1, the ledger's steps unchanged and the text filed under `## Owed steps`, counted as one added step as main counted it (a small pytest case driving the module in-process) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 22 | 4153 | 349684 | 38264 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| An `add-ledger-step.sh … instead-of` over an `⟦added⟧` anchor passing more new texts than the budget allows after crediting that one replaced anchor is refused: exit 1, the anchor kept and the texts filed under `## Owed steps` (a small pytest case driving the module in-process) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 11 | 22 | 4030 | 347396 | 39171 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| An `add-ledger-step.sh … instead-of` replacing an `⟦added⟧` step with one text, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, exits 0 and replaces the step, leaving the `⟦added⟧` count unchanged and filing nothing under `## Owed steps` (a small pytest case driving the module in-process) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 40 | 0.10 |
| An `add-ledger-step.sh` call whose one new non-repair text carries a newline, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, is refused: exit 1, the ledger's steps unchanged and the text filed under `## Owed steps`, counted as one added step as main counted it (a small pytest case driving the module in-process) ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 60 | 0.13 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 2 | 0 | 2 | 1 | 3 | 3 | 1 | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 2 | 2 |
| fast | 16 | 16 | 0 | 16 | 16 | 17 | 20 | 20 |  |  |  |  |  |  |  |  |  |  |
| target | 16 | 2 | 16 | 1 | 20 | 0 | 0 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 93 | 182 | 31170 | 2663115 | 402529 | 1.73 |
