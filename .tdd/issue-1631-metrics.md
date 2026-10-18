### 📊 Metrics — issue 1631

Wall time for the issue: 1703 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1764.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 5 | 1 | 2 | 642 | 0 | 30063 | 0.08 |
| red | 2 | 1 | 0 | 0 | 37 | 25 | 9 | 18 | 3073 | 255348 | 54118 | 0.19 |
| green | 4 | 1 | 1 | 0 | 215 | 87 | 23 | 44 | 7756 | 648098 | 73090 | 0.47 |
| refactor | 2 | 1 | 0 | 0 | 40 | 16 | 6 | 12 | 1074 | 155067 | 27931 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 4 | 1 | 0 | 163 | 52 | 18 | 36 | 5142 | 480200 | 78247 | 0.30 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 33 | 22 | 8 | 16 | 2579 | 226967 | 53781 | 0.18 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 105 | 59 | 13 | 24 | 4824 | 351346 | 53174 | 0.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 215 | 0.47 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| An `add-ledger-step.sh … instead-of` replacing an `⟦added⟧` step with one text, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, exits 0 and replaces the step, leaving the `⟦added⟧` count unchanged and filing nothing under `## Owed steps` (a small pytest case driving the module in-process) ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 128 | 38 | 74 | 11903 | 1058513 | 155139 | 0.76 | 412 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| An `add-ledger-step.sh … instead-of` replacing an `⟦added⟧` step with one text, on a ledger already holding `VERI_STEP_GROWTH` `⟦added⟧` steps, exits 0 and replaces the step, leaving the `⟦added⟧` count unchanged and filing nothing under `## Owed steps` (a small pytest case driving the module in-process) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 40 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 2 | 0 | 2 | 1 | 3 | 3 | 1 |
| fast | 16 | 16 | 0 | 16 | 16 | 17 |  |  |  |
| target | 16 | 2 | 16 | 1 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 39 | 76 | 12545 | 1058513 | 185202 | 0.84 |
