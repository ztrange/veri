### 📊 Metrics — issue 1603

Wall time for the issue: 1100 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1604.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 2 | 4 | 1087 | 59294 | 35348 | 0.16 |
| red | 4 | 2 | 0 | 0 | 88 | 61 | 22 | 44 | 6929 | 957977 | 161434 | 0.81 |
| green | 4 | 2 | 0 | 0 | 223 | 59 | 24 | 44 | 6363 | 910980 | 147675 | 0.75 |
| refactor | 4 | 2 | 0 | 0 | 124 | 35 | 15 | 28 | 3453 | 523788 | 144010 | 0.66 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 263 | 93 | 32 | 64 | 10088 | 1272873 | 256392 | 1.25 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 184 | 72 | 31 | 56 | 7744 | 1179166 | 232075 | 1.12 |

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
| replaces_case.parse, given a step text that names the replaces-case mark but carries no replaces clause with a quoted case, returns None instead of raising AttributeError ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 65 | 29 | 52 | 7103 | 1025770 | 219016 | 1.05 | 278 | unknown | 0/5 | nothing-left |  |  | full |
| verify.sh green, run with --step text that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 32 | 64 | 9642 | 1366975 | 234103 | 1.17 | 299 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| replaces_case.parse, given a step text that names the replaces-case mark but carries no replaces clause with a quoted case, returns None instead of raising AttributeError ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 63 | 0.32 |
| verify.sh green, run with --step text that names the replaces-case mark but carries no replaces clause with a quoted case ... in a suite path, returns the verifier's verdict: exit 0 and the verifier's reason on a PASS, not exit 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 61 | 0.34 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 7 | 0 | 11 | 0 | 1 | 11 | 0 | 8 |
| fast | 37 | 30 | 40 | 29 | 26 | 26 |  |  |  |  |
| target | 0 | 0 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 63 | 120 | 17832 | 2452039 | 488467 | 2.38 |
