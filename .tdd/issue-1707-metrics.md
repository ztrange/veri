### 📊 Metrics — issue 1707

Wall time for the issue: 1680 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1737.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 939 | 0 | 30410 | 0.13 |
| red | 3 | 1 | 0 | 0 | 143 | 55 | 19 | 38 | 6867 | 613813 | 64010 | 0.39 |
| green | 2 | 1 | 0 | 0 | 89 | 20 | 10 | 18 | 2252 | 250562 | 29596 | 0.17 |
| refactor | 2 | 1 | 0 | 0 | 34 | 12 | 6 | 12 | 814 | 157005 | 29286 | 0.14 |
| pin | 1 | 1 | 0 | 0 | 20 | 16 | 5 | 10 | 1699 | 139805 | 15725 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 129 | 53 | 18 | 36 | 5291 | 464196 | 91050 | 0.46 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 167 | 58 | 23 | 44 | 7280 | 696989 | 77977 | 0.45 |

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
| A leaf launched through run-leaf.sh requests the 5-minute cache TTL (FORCE_PROMPT_CACHING_5M=1 in the claude binary's environment), so a stub claude that writes its cache at 5 minutes when asked reports ephemeral_5m_input_tokens non-zero and ephemeral_1h_input_tokens zero in the leaf's stream usage ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 58 | 26 | 50 | 6269 | 704577 | 97383 | 0.52 | 259 | unknown | 0/5 | nothing-left |  |  | full |
| The conductor launched through run-conductor.sh does not request the 5-minute cache TTL (no FORCE_PROMPT_CACHING_5M in the claude binary's environment), so a stub claude reports its cache writes as ephemeral_1h_input_tokens ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 14 | 28 | 5363 | 456608 | 41234 | 0.26 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A leaf launched through run-leaf.sh requests the 5-minute cache TTL (FORCE_PROMPT_CACHING_5M=1 in the claude binary's environment), so a stub claude that writes its cache at 5 minutes when asked reports ephemeral_5m_input_tokens non-zero and ephemeral_1h_input_tokens zero in the leaf's stream usage ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.14 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 4 | 8 | 35 |
| fast | 16 | 17 | 16 |  |  |
| target | 17 | 0 | 1 | 1 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 41 | 80 | 12571 | 1161185 | 169027 | 0.92 |
