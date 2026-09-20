### 📊 Metrics — issue 344

Wall time for the issue: 2844 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/372.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 526 | 472 | 59 | 108 | 39647 | 3179694 | 222377 | 4.81 |
| green | 4 | 2 | 0 | 0 | 794 | 201 | 50 | 84 | 16715 | 1997726 | 172100 | 3.14 |
| refactor | 4 | 2 | 0 | 0 | 1087 | 498 | 80 | 154 | 35855 | 4789528 | 229295 | 5.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 526 | 4.81 |
| green | 0 | 0.00 | 794 | 3.14 |
| refactor | 0 | 0.00 | 1087 | 5.58 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| dashboard.html schedules each pane's next request only from the previous request's settlement — both the resolve and the reject path — and carries no setInterval anywhere on the page ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 585 | 97 | 172 | 49344 | 4918249 | 310024 | 6.79 | unknown | unknown | 4/5 | structural-owed |
| the server answers /api/events while a /api/runs request is still blocked inside status.sh, asserted by ordering rather than by elapsed time ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 586 | 92 | 174 | 42873 | 5048699 | 313748 | 6.73 | unknown | unknown | 3/5 | structural-owed |

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 189 | 346 | 92217 | 9966948 | 623772 | 13.53 |
