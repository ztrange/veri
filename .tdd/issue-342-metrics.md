### 📊 Metrics — issue 342

Wall time for the issue: 5361 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 1 of 8 planned.
Outcome: the run bailed — killed-stuck, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 1 | 1 | 1 | 1242 | 313 | 55 | 96 | 25697 | 2476996 | 213335 | 4.01 |
| green | 2 | 1 | 0 | 0 | 185 | 137 | 32 | 54 | 10728 | 1379359 | 98158 | 1.94 |
| refactor | 2 | 1 | 0 | 0 | 152 | 136 | 21 | 42 | 9480 | 1024180 | 87558 | 1.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 1076 | 2.16 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| a test-command run made through the new wrapper writes one `test-run` event carrying `tier`, `suites` and `seconds`, and exits with the command's own status | 6 | 3 | 0 | 0 | 0 | 0 | 397 | 78 | 134 | 30786 | 3369451 | 296157 | 5.42 | 651 | unknown | 2/5 | structural-owed |
| the "usual" for a tier is the median of that tier's last 10 `test-run` events' seconds, read out of `.tdd/events.jsonl` | 3 | 0 | 1 | 1 | 1 | 0 | 189 | 30 | 58 | 15119 | 1511084 | 102894 | 2.16 | unknown | 1/2 | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 108 | 192 | 45905 | 4880535 | 399051 | 7.58 |
