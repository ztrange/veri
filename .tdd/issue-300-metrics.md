### 📊 Metrics — issue 300

Wall time for the issue: unknown s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: unknown of 2 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 1 | 0 | 0 | 254 | 219 | 23 | 34 | 16686 | 936033 | 106738 | 1.95 |
| green | 1 | 0 | 0 | 1 | 900 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 254 | 1.95 |
| green | 0 | 0.00 | 900 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A slow-but-alive leaf's heartbeat premise never depends on real elapsed time: every silence supervise.test.sh puts in front of the supervisor is injected onto its clock, so a scheduling delay near a whole-second boundary cannot be read as a stall | 3 | 1 | 0 | 1 | 1 | 0 | 219 | 23 | 34 | 16686 | 936033 | 106738 | 1.95 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 23 | 34 | 16686 | 936033 | 106738 | 1.95 |
