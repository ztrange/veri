### 📊 Metrics — issue 1054

Wall time for the issue: 1334 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1062.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 2 | 4 | 1023 | 53512 | 36228 | 0.17 |
| red | 5 | 2 | 0 | 0 | 135 | 116 | 29 | 56 | 11654 | 1268535 | 217737 | 1.90 |
| green | 4 | 2 | 0 | 0 | 181 | 90 | 26 | 52 | 8839 | 1137389 | 162221 | 1.33 |
| refactor | 4 | 2 | 0 | 0 | 85 | 41 | 14 | 28 | 3857 | 507617 | 153870 | 1.09 |
| pin | 1 | 1 | 0 | 0 | 13 | 9 | 3 | 6 | 1005 | 101172 | 37526 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 208 | 106 | 35 | 70 | 11579 | 1366065 | 302926 | 1.60 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 218 | 159 | 39 | 76 | 14799 | 1702160 | 304656 | 3.07 |

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
| When pulls/<n>/ccr/ready_for_review is refused with a 404 and the GraphQL-over-gh-api route then readies the PR, gh_pr_ready exits 0 and its stderr carries no HTTP 404 line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 107 | 33 | 64 | 10495 | 1359795 | 244612 | 1.93 | 266 | unknown | 0/5 | nothing-left |  |  | full |
| When the ccr/ready_for_review route and the GraphQL-over-gh-api route both fail, gh_pr_ready exits 2 and its stderr carries each route's own failure message ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 104 | 28 | 56 | 10490 | 1146024 | 239493 | 1.85 | 255 | unknown | 0/5 | nothing-left |  |  | full |
| When pulls/<n>/ccr/ready_for_review succeeds, gh_pr_ready readies the PR by that route alone, never calling the GraphQL-over-gh-api route, and exits 0 ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 11 | 22 | 4370 | 508894 | 87249 | 0.73 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When pulls/<n>/ccr/ready_for_review is refused with a 404 and the GraphQL-over-gh-api route then readies the PR, gh_pr_ready exits 0 and its stderr carries no HTTP 404 line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.55 |
| When the ccr/ready_for_review route and the GraphQL-over-gh-api route both fail, gh_pr_ready exits 2 and its stderr carries each route's own failure message ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 42 | 0.54 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 |
| fast | 16 | 17 | 17 | 17 | 18 | 16 |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 74 | 146 | 26378 | 3068225 | 607582 | 4.67 |
