### 📊 Metrics — issue 888

Wall time for the issue: 2338 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/889.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 964 | 11866 | 29725 | 0.13 |
| red | 3 | 1 | 0 | 0 | 133 | 123 | 24 | 48 | 10353 | 1229384 | 141326 | 1.42 |
| green | 2 | 1 | 0 | 0 | 157 | 81 | 19 | 38 | 6261 | 882156 | 82533 | 0.78 |
| refactor | 2 | 1 | 0 | 0 | 88 | 29 | 9 | 18 | 2631 | 353758 | 78061 | 0.58 |
| pin | 1 | 1 | 0 | 0 | 17 | 13 | 3 | 6 | 1561 | 101925 | 38609 | 0.19 |
| rebase | 3 | 1 | 0 | 0 | 743 | 46 | 14 | 24 | 3698 | 524701 | 80666 | 0.66 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 521 | 87 | 26 | 48 | 9125 | 917729 | 221847 | 1.16 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 626 | 213 | 44 | 88 | 16343 | 2186061 | 229073 | 2.60 |
| developer | not recorded | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With VERI_GH_DRIVER unset, when gh api's POST to pulls/<n>/ccr/ready_for_review fails with a 404 (github.com has no such REST route), gh_pr_ready marks the draft ready through GraphQL's markPullRequestReadyForReview mutation sent as a `gh api graphql` call carrying that PR's node id, never runs `gh pr ready`, and returns 0 | 6 | 3 | 0 | 0 | 0 | 0 | 181 | 42 | 84 | 15197 | 1970045 | 257015 | 2.23 | 413 | unknown | 0/5 | nothing-left |  |  | full |
| With VERI_GH_DRIVER unset, when the ccr/ready_for_review POST and the `gh api graphql` markPullRequestReadyForReview fallback both fail, gh_pr_ready returns 2 and the PR is reported not readied | 4 | 2 | 0 | 0 | 0 | 0 | 111 | 27 | 50 | 9307 | 1121879 | 164180 | 1.39 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With VERI_GH_DRIVER unset, when gh api's POST to pulls/<n>/ccr/ready_for_review fails with a 404 (github.com has no such REST route), gh_pr_ready marks the draft ready through GraphQL's markPullRequestReadyForReview mutation sent as a `gh api graphql` call carrying that PR's node id, never runs `gh pr ready`, and returns 0 | 1 | 0/5 | nothing-left | PASS | 0 | 88 | 0.58 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 38 | 1 | 2 | 1 | 0 | 0 |
| fast | 14 | 15 | 15 |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 |  |  |  |  |  |
| all | 344 | 347 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 70 | 136 | 25468 | 3103790 | 450920 | 3.76 |
