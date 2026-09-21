### 📊 Metrics — issue 270

Wall time for the issue: 7037 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/402.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 6 | 3 | 0 | 0 | 688 | 648 | 78 | 144 | 50521 | 3836400 | 313133 | 6.31 |
| green | 12 | 3 | 3 | 0 | 4053 | 1453 | 204 | 384 | 119700 | 11792417 | 715531 | 16.05 |
| refactor | 6 | 3 | 0 | 0 | 1586 | 757 | 124 | 238 | 54087 | 8475640 | 368063 | 9.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 4933 | 17.48 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Every script under skills/tdd/scripts/ that takes a required positional argument exits 2 with a usage line on stderr when it is missing | 10 | 3 | 2 | 0 | 0 | 0 | 1397 | 174 | 326 | 109672 | 10535752 | 630951 | 14.32 | 3468 | 2/2 | 3/5 | structural-owed |
| The cross-suite guard fails, naming the offending script, when a script under skills/tdd/scripts/ exits with anything but 2 on a missing required argument | 6 | 3 | 0 | 0 | 0 | 0 | 474 | 76 | 148 | 38498 | 3748122 | 287772 | 5.71 | 631 | unknown | 1/5 | nothing-structural |
| The cross-suite guard fails, naming the offending script, when one still guards a required positional argument with a bare ${N:?…} expansion | 8 | 3 | 1 | 0 | 0 | 0 | 987 | 156 | 292 | 76138 | 9820583 | 478004 | 11.60 | 2667 | 1/2 | 2/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 98 | 211 | 211 | 130 | 215 | 8 | 3 | 8 | 23 | 0 | 1 | 1 | 1 | 1 | 0 | 3 | 1 | 0 | 1 | 0 | 1 | 41 | 0 | 1 | 2 |
| fast | 2 | 2 | 1 | 1 | 2 | 1 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 211 | 217 | 218 | 229 | 228 | 233 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 406 | 766 | 224308 | 24104457 | 1396727 | 31.63 |
