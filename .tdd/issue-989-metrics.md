### 📊 Metrics — issue 989

Wall time for the issue: 1828 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1017.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 8 | 2 | 4 | 649 | 63264 | 42037 | 0.36 |
| red | 4 | 1 | 0 | 0 | 178 | 145 | 36 | 70 | 12339 | 1832744 | 193415 | 2.16 |
| green | 2 | 1 | 0 | 0 | 244 | 97 | 20 | 40 | 7152 | 1014860 | 91758 | 1.08 |
| refactor | 2 | 1 | 0 | 0 | 87 | 36 | 9 | 18 | 3056 | 394677 | 89288 | 0.85 |
| pin | 2 | 2 | 0 | 0 | 43 | 32 | 7 | 14 | 3083 | 279393 | 85031 | 0.80 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 6 | 6 | 0 | 0 | 248 | 128 | 26 | 52 | 10355 | 1129080 | 259993 | 2.51 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 317 | 190 | 48 | 94 | 15924 | 2455858 | 241536 | 2.74 |

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
| `refactor-owed.sh render` over a file whose only step holds test-only leftovers prints no `### <that step>` line, while the leftovers still appear under `### Test-only` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 196 | 45 | 90 | 14844 | 2244120 | 276122 | 2.96 | 521 | unknown | 0/5 | nothing-left |  |  | full |
| `refactor-owed.sh render` over a file where one step's leftovers are all test-only and another's are structural prints the structural step's heading and bullet, and not the test-only step's heading ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 12 | 24 | 5129 | 577465 | 90472 | 0.94 | unknown | unknown | unknown | unknown |  |  | pin |
| `refactor-owed.sh render` over a file whose only step's every structural bullet has an `applied` line prints no `### <that step>` line, while the transforms still appear under `### Applied` ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 15 | 28 | 5657 | 700089 | 92898 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `refactor-owed.sh render` over a file whose only step holds test-only leftovers prints no `### <that step>` line, while the leftovers still appear under `### Test-only` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 87 | 0.85 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 1 | 2 | 2 | 1 | 1 |
| fast | 39 | 46 | 40 | 40 |  |  |  |  |
| target | 1 | 1 | 0 | 0 | 1 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 74 | 146 | 26279 | 3584938 | 501529 | 5.26 |
