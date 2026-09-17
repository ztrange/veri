### 📊 Metrics — issue 240

Wall time for the issue: 2498 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/266.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 6 | 1 | 0 | 0 | 266 | 238 | 32 | 64 | 23913 | 1335912 | 237960 | 3.31 |
| pin | 4 | 4 | 0 | 0 | 251 | 235 | 50 | 98 | 19779 | 2699908 | 165451 | 1.41 |
| green | 2 | 1 | 0 | 0 | 1353 | 106 | 28 | 50 | 7470 | 1444125 | 81447 | 0.97 |
| refactor | 2 | 1 | 0 | 0 | 451 | 66 | 17 | 34 | 5543 | 913515 | 85484 | 0.85 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The ordering case reads the Draft PR step's fenced command block line by line and fails when the `metrics:` commit line precedes the `gh pr create` line | 2 | 1 | 0 | 0 | 0 | 0 | 86 | 16 | 30 | 8161 | 759733 | 79889 | 0.89 | unknown | unknown | unknown | unknown |
| The ordering case fails when the `gh pr edit` line precedes the `metrics:` commit or `push-branch.sh` | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 19 | 38 | 7738 | 952413 | 78681 | 0.94 | unknown | unknown | unknown | unknown |
| The ordering case passes on SKILL.md's current order (gh pr create → event.sh done → metrics.sh → metrics: commit → push-branch.sh → gh pr edit) | 2 | 1 | 0 | 0 | 0 | 0 | 122 | 18 | 36 | 11147 | 920093 | 85786 | 1.03 | unknown | unknown | unknown | unknown |
| The 📊-in-PR-body probe asks the `gh pr edit` command, not a record that merely also contains `gh pr create` | 2 | 1 | 0 | 0 | 0 | 0 | 98 | 18 | 36 | 7645 | 920702 | 84660 | 1.00 | unknown | unknown | unknown | unknown |
| The suite's header comment describes the post-#236 Draft PR order | 6 | 3 | 0 | 0 | 0 | 0 | 262 | 56 | 106 | 22014 | 2840519 | 241326 | 2.68 | 1976 | unknown | 0/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 127 | 246 | 56705 | 6393460 | 570342 | 6.54 |
