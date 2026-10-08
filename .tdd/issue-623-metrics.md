### 📊 Metrics — issue 623

Wall time for the issue: 1561 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1186.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 3 | 6 | 1074 | 107048 | 41762 | 0.20 |
| red | 3 | 1 | 0 | 0 | 102 | 89 | 21 | 42 | 8673 | 998809 | 135457 | 1.28 |
| pin | 1 | 1 | 0 | 0 | 16 | 12 | 4 | 8 | 1339 | 155946 | 39703 | 0.20 |
| green | 2 | 1 | 0 | 0 | 105 | 43 | 12 | 24 | 4242 | 534219 | 83553 | 0.68 |
| refactor | 2 | 1 | 0 | 0 | 60 | 28 | 7 | 14 | 2510 | 262107 | 80272 | 0.57 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 143 | 70 | 23 | 46 | 7411 | 934583 | 201402 | 1.07 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 153 | 112 | 24 | 48 | 10427 | 1123546 | 179345 | 1.87 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With VERI_GH_DRIVER unset (the cloud default), gh_pr_ready 42 against a gh whose `gh pr ready` fails with GraphQL's HTTP 403 readies PR 42 over the REST route, never runs `gh pr ready`, returns 0 and prints nothing on stderr | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 13 | 26 | 5619 | 615066 | 89585 | 0.78 | unknown | unknown | unknown | unknown |  |  | pin |
| With VERI_GH_DRIVER=auto, gh_pr_ready 42 against a gh whose `gh pr ready` fails with GraphQL's HTTP 403 and whose REST ready route then succeeds returns 0 with no line of that 403 on stderr | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 31 | 62 | 11145 | 1336015 | 249400 | 1.96 | 292 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With VERI_GH_DRIVER=auto, gh_pr_ready 42 against a gh whose `gh pr ready` fails with GraphQL's HTTP 403 and whose REST ready route then succeeds returns 0 with no line of that 403 on stderr | 1 | 0/5 | nothing-left | PASS | 0 | 60 | 0.57 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 1 | 1 | 1 | 3 | 0 | 0 |
| target | 1 | 0 | 1 |  |  |  |  |  |  |
| fast | 23 | 24 | 24 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 47 | 94 | 17838 | 2058129 | 380747 | 2.93 |
