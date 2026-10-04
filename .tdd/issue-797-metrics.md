### 📊 Metrics — issue 797

Wall time for the issue: 5258 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/800.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 16 | 3 | 6 | 1658 | 111486 | 39566 | 0.37 |
| red | 6 | 3 | 0 | 0 | 333 | 245 | 59 | 112 | 21066 | 2957511 | 284421 | 3.29 |
| green | 6 | 3 | 0 | 0 | 2675 | 254 | 75 | 144 | 23466 | 3800782 | 289476 | 3.55 |
| refactor | 6 | 3 | 0 | 0 | 586 | 91 | 31 | 62 | 8786 | 1384495 | 256795 | 2.51 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 10 | 10 | 0 | 0 | 2333 | 287 | 76 | 152 | 25286 | 3554380 | 427172 | 4.63 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 1287 | 319 | 92 | 172 | 29690 | 4699894 | 443086 | 5.08 |

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
| SKILL.md's "2. Scope & plan → the ledger" section states that a step bringing in code (a port step, a new module) either comes after the steps that pin every branch it brings in, or brings in only the branches its own test requires, the rest arriving with the steps that pin them ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 56 | 110 | 18954 | 2772474 | 280370 | 3.18 | 2082 | unknown | 0/5 | nothing-left |  |  | full |
| prompts/verify-plan.md directs a REJECT for a plan whose step introduces a branch (for example a fallback forced by an existing suite) that only a later step's test requires, and requires the REJECT reason to name both the introducing step and the later pinning step ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 231 | 58 | 110 | 18185 | 3015216 | 288256 | 3.27 | 1030 | unknown | 0/5 | nothing-left |  |  | full |
| prompts/verify-plan.md states that a plan whose step bringing in code comes after the steps pinning its branches, or brings in only the branches its own test requires, is not a REJECT on ordering grounds ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 159 | 51 | 98 | 16179 | 2355098 | 262066 | 2.89 | 751 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md's "2. Scope & plan → the ledger" section states that a step bringing in code (a port step, a new module) either comes after the steps that pin every branch it brings in, or brings in only the branches its own test requires, the rest arriving with the steps that pin them ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 398 | 0.95 |
| prompts/verify-plan.md directs a REJECT for a plan whose step introduces a branch (for example a fallback forced by an existing suite) that only a later step's test requires, and requires the REJECT reason to name both the introducing step and the later pinning step ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 92 | 0.77 |
| prompts/verify-plan.md states that a plan whose step bringing in code comes after the steps pinning its branches, or brings in only the branches its own test requires, is not a REJECT on ordering grounds ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 96 | 0.79 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 0 | 195 | 527 | 0 | 24 | 261 | 9 | 9 | 9 | 10 | 39 | 10 | 8 | 8 | 11 | 0 | 7 | 3 | 1 | 7 | 3 | 107 | 3 | 2 | 11 |
| fast | 38 | 40 | 52 | 57 | 121 | 45 | 63 | 48 | 48 | 40 | 47 | 48 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 7 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 168 | 324 | 54976 | 8254274 | 870258 | 9.71 |
