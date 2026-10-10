### 📊 Metrics — issue 1306

Wall time for the issue: 5024 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1382.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 13 | 4 | 6 | 1672 | 118452 | 44147 | 0.21 |
| red | 5 | 2 | 0 | 0 | 179 | 129 | 34 | 64 | 13343 | 1655560 | 251754 | 2.18 |
| green | 4 | 2 | 0 | 0 | 1205 | 98 | 27 | 54 | 9927 | 1332063 | 183751 | 1.46 |
| refactor | 5 | 2 | 0 | 0 | 1078 | 81 | 30 | 58 | 8214 | 1384385 | 225926 | 1.59 |
| pin | 1 | 1 | 0 | 0 | 20 | 14 | 5 | 8 | 1558 | 173007 | 43645 | 0.21 |
| predicate | 1 | 0 | 0 | 0 | 17 | 13 | 4 | 8 | 1104 | 163155 | 40524 | 0.38 |
| structural | 1 | 0 | 0 | 0 | 195 | 28 | 8 | 16 | 2956 | 401335 | 48501 | 0.53 |
| transform | 1 | 1 | 0 | 0 | 172 | 10 | 4 | 8 | 1031 | 168642 | 41176 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 0 | 0 | 1728 | 165 | 55 | 104 | 16695 | 2400082 | 443323 | 2.18 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 1160 | 221 | 61 | 118 | 23110 | 2996517 | 436101 | 4.55 |

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
| A fetch of origin whose stderr is git 2.53's held-ref-lock wording (`error: fetching ref refs/remotes/origin/master failed: reference already exists`), fed in-process as the fetch's stderr, is retried through the sleep exactly as a `cannot lock ref` fetch is — at most 60 fetches and 59 sleeps — then refused with exit 2 ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 125 | 39 | 76 | 12225 | 1788718 | 323770 | 2.29 | 1475 | unknown | 0/5 | nothing-left |  |  | full |
| When a fetch refused after spending its retries failed on git 2.53's `reference already exists` wording, the refusal on stderr names the ref lock as the cause, as the `cannot lock ref` wording already does ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 42 | 82 | 15494 | 2073232 | 282280 | 2.31 | 1121 | unknown | 1/5 | nothing-structural |  |  | full |
| A fetch of origin failing with neither ref-lock wording is still refused at once — exit 2 after one fetch and no sleep — and its refusal does not name the ref lock ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 100 | 31 | 58 | 10414 | 1416197 | 229227 | 1.93 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A fetch of origin whose stderr is git 2.53's held-ref-lock wording (`error: fetching ref refs/remotes/origin/master failed: reference already exists`), fed in-process as the fetch's stderr, is retried through the sleep exactly as a `cannot lock ref` fetch is — at most 60 fetches and 59 sleeps — then refused with exit 2 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 660 | 0.90 |
| When a fetch refused after spending its retries failed on git 2.53's `reference already exists` wording, the refusal on stderr names the ref lock as the cause, as the `cannot lock ref` wording already does ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 418 | 0.69 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 229 | 217 | 267 | 177 | 4 | 2 | 1 | 169 | 176 | 159 | 157 | 2 | 161 | 158 |
| fast | 75 | 68 | 72 | 68 | 64 | 61 | 57 |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 116 | 222 | 39805 | 5396599 | 879424 | 6.73 |
