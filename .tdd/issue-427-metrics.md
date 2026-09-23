### 📊 Metrics — issue 427

Wall time for the issue: 2753 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/434.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 8 | 4 | 0 | 0 | 638 | 551 | 92 | 160 | 43065 | 4337232 | 417062 | 7.42 |
| green | 8 | 4 | 0 | 0 | 649 | 429 | 104 | 188 | 35130 | 4726550 | 373477 | 6.98 |
| refactor | 8 | 4 | 0 | 0 | 748 | 643 | 96 | 172 | 49383 | 4705635 | 406291 | 7.65 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The attempt ref name carries the step index read from the committed ledger rather than the step prose | 6 | 3 | 0 | 0 | 0 | 0 | 427 | 80 | 148 | 33480 | 3908193 | 300806 | 5.80 | 620 | unknown | 1/5 | structural-owed |
| A step whose title contains spaces, apostrophes or slashes has its attempt preserved under a ref name git accepts | 6 | 3 | 0 | 0 | 0 | 0 | 448 | 72 | 126 | 34034 | 3231935 | 283496 | 5.30 | 645 | unknown | 1/5 | structural-owed |
| The leaf log and output copied beside the ref are named from that same index, so a title carrying a slash writes no nested path | 6 | 3 | 0 | 0 | 0 | 0 | 301 | 65 | 114 | 24488 | 2920297 | 291454 | 4.99 | 531 | unknown | 2/5 | structural-owed |
| A preserve that fails for any other reason reports the failure on stderr instead of passing silently | 6 | 3 | 0 | 0 | 0 | 0 | 447 | 75 | 132 | 35576 | 3708992 | 321074 | 5.96 | 625 | unknown | 3/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 4 | 3 | 4 | 3 | 5 | 4 | 3 | 67 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| fast | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 292 | 520 | 127578 | 13769417 | 1196830 | 22.05 |
