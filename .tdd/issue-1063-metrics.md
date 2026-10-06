### 📊 Metrics — issue 1063

Wall time for the issue: 1112 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1066.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 727 | 10362 | 31139 | 0.13 |
| red | 3 | 1 | 0 | 0 | 91 | 80 | 19 | 36 | 7305 | 810559 | 128533 | 1.17 |
| green | 2 | 1 | 0 | 0 | 95 | 54 | 15 | 28 | 5137 | 617126 | 80186 | 0.70 |
| refactor | 2 | 1 | 0 | 0 | 53 | 31 | 10 | 20 | 2928 | 399921 | 76946 | 0.59 |
| pin | 1 | 1 | 0 | 0 | 16 | 12 | 4 | 8 | 1260 | 149487 | 37270 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 110 | 62 | 21 | 40 | 6589 | 759235 | 182930 | 0.95 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 153 | 121 | 28 | 54 | 10768 | 1228220 | 171144 | 1.83 |

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
| When the ccr/ready_for_review route is refused and the GraphQL-over-gh-api route readies the PR, gh_pr_ready exits 0 and its stdout carries nothing the refused ccr call printed ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 36 | 70 | 11834 | 1506694 | 242381 | 1.97 | 274 | unknown | 0/5 | nothing-left |  |  | full |
| When every route fails, the refused ccr route's response body (what it printed on stdout) reaches the caller on stderr and gh_pr_ready returns 2 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 12 | 22 | 4796 | 470399 | 80554 | 0.67 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the ccr/ready_for_review route is refused and the GraphQL-over-gh-api route readies the PR, gh_pr_ready exits 0 and its stdout carries nothing the refused ccr call printed ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 53 | 0.59 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 0 | 0 | 0 | 1 |
| fast | 15 | 15 | 16 |  |  |  |  |
| target | 1 | 0 | 1 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 49 | 94 | 17357 | 1987455 | 354074 | 2.78 |
