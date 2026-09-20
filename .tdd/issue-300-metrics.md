### 📊 Metrics — issue 300

Wall time for the issue: 2709 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/378.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 6 | 3 | 0 | 0 | 963 | 812 | 90 | 148 | 62067 | 4508351 | 361729 | 7.42 |
| green | 5 | 2 | 0 | 1 | 1849 | 385 | 67 | 120 | 30545 | 3671126 | 234675 | 4.95 |
| refactor | 4 | 2 | 0 | 0 | 560 | 326 | 61 | 108 | 26283 | 3180614 | 213379 | 4.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A slow-but-alive leaf's heartbeat premise never depends on real elapsed time: every silence supervise.test.sh puts in front of the supervisor is injected onto its clock, so a scheduling delay near a whole-second boundary cannot be read as a stall | 9 | 4 | 0 | 1 | 1 | 0 | 760 | 116 | 202 | 59009 | 5874352 | 448402 | 8.90 | 995 | unknown | 1/5 | nothing-structural |
| A case in supervise.test.sh that reaches its silence by real waiting rather than by an injected clock jump fails the run, named, against an exemption table carrying a reason for each deliberate real-clock dependence | 6 | 3 | 0 | 0 | 0 | 0 | 763 | 102 | 174 | 59886 | 5485739 | 361381 | 7.85 | 1501 | unknown | 3/5 | structural-owed |

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 218 | 376 | 118895 | 11360091 | 809783 | 16.75 |
