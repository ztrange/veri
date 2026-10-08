### 📊 Metrics — issue 1129

Wall time for the issue: 1447 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1170.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 771 | 12385 | 30791 | 0.13 |
| red | 4 | 1 | 0 | 0 | 114 | 96 | 29 | 52 | 10190 | 1214992 | 176013 | 1.70 |
| green | 2 | 1 | 0 | 0 | 103 | 38 | 12 | 22 | 4171 | 472365 | 81252 | 0.66 |
| refactor | 2 | 1 | 0 | 0 | 67 | 31 | 11 | 20 | 3042 | 414287 | 81160 | 0.62 |
| pin | 2 | 2 | 0 | 0 | 222 | 92 | 27 | 54 | 9752 | 1477104 | 97610 | 0.78 |
| predicate | 1 | 0 | 0 | 0 | 9 | 7 | 3 | 6 | 504 | 102179 | 35954 | 0.32 |
| structural | 1 | 0 | 0 | 0 | 29 | 17 | 7 | 12 | 1505 | 252284 | 38176 | 0.39 |
| transform | 1 | 1 | 0 | 0 | 19 | 8 | 4 | 8 | 883 | 150109 | 36131 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 358 | 144 | 48 | 94 | 15581 | 2251745 | 280139 | 1.73 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 214 | 151 | 46 | 82 | 15237 | 1843960 | 296948 | 3.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| an answer whose first line is empty and whose later lines name issues launches a conductor for the first non-empty, unparked line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 106 | 35 | 64 | 10960 | 1374269 | 246862 | 1.96 | 297 | unknown | 0/5 | structural-owed |  |  | full |
| an empty line between a parked issue and an unparked one is skipped, not taken as the issue, so the conductor is launched for the unparked line after it ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 12 | 22 | 4240 | 505359 | 85052 | 0.70 | unknown | unknown | unknown | unknown |  |  | pin |
| an answer whose every line is empty or parked ends the run with exit 0, launching no conductor ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 140 | 46 | 88 | 14847 | 2203692 | 214382 | 1.97 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| an answer whose first line is empty and whose later lines name issues launches a conductor for the first non-empty, unparked line ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 67 | 0.62 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 8 | 8 | 1 | 1 | 9 | 8 |  |
| fast | 21 | 22 | 21 |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 94 | 176 | 30818 | 4095705 | 577087 | 4.78 |
