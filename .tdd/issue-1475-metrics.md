### 📊 Metrics — issue 1475

Wall time for the issue: 2496 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1525.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 25 | 18 | 4 | 8 | 1697 | 134764 | 90248 | 0.39 |
| red | 2 | 1 | 0 | 0 | 239 | 57 | 17 | 34 | 7196 | 937751 | 99090 | 0.56 |
| green | 2 | 1 | 0 | 0 | 1209 | 37 | 14 | 28 | 4199 | 708489 | 94986 | 0.49 |
| refactor | 2 | 1 | 0 | 0 | 134 | 16 | 8 | 16 | 1589 | 357485 | 90976 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 4 | 1 | 0 | 947 | 63 | 20 | 40 | 6739 | 907866 | 228079 | 1.07 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 660 | 65 | 23 | 46 | 7942 | 1230623 | 147221 | 0.79 |

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
| SKILL.md's phased-step subsection runs no-product-caller.sh on the old interface before contract-b only: the window around no-product-caller.sh names contract-b as the phase it gates, no longer says "Before it launches contract-a or contract-b", and says contract-a starts on the migrate phase's PASS without the scan — pinned by amending the skill-refactor-kind.test.sh case "starts a phased step's contract only once no-product-caller.sh on the old interface exits 0" ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 39 | 78 | 12984 | 2003725 | 285052 | 1.47 | 1679 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md's phased-step subsection runs no-product-caller.sh on the old interface before contract-b only: the window around no-product-caller.sh names contract-b as the phase it gates, no longer says "Before it launches contract-a or contract-b", and says contract-a starts on the migrate phase's PASS without the scan — pinned by amending the skill-refactor-kind.test.sh case "starts a phased step's contract only once no-product-caller.sh on the old interface exits 0" ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 134 | 0.42 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 30 | 30 | 28 | 345 |
| fast | 62 | 68 | 56 |  |
| target | 31 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 86 | 14681 | 2138489 | 375300 | 1.86 |
