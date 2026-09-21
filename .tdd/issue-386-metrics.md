### 📊 Metrics — issue 386

Wall time for the issue: 7443 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/407.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 13 | 6 | 0 | 0 | 779 | 696 | 127 | 240 | 55122 | 5854193 | 579287 | 10.10 |
| green | 18 | 6 | 3 | 0 | 3293 | 984 | 214 | 392 | 76071 | 9403598 | 750761 | 14.11 |
| refactor | 12 | 6 | 0 | 0 | 1335 | 577 | 114 | 218 | 47035 | 5175518 | 514011 | 8.90 |
| pin | 1 | 1 | 0 | 0 | 42 | 35 | 7 | 14 | 2913 | 308955 | 40205 | 0.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3135 | 11.75 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| stop-requested.sh prints the mode on stdout and exits 0 when .tdd/stop holds at-ledger, at-leaf or now | 10 | 3 | 2 | 0 | 0 | 0 | 622 | 114 | 218 | 46532 | 5145432 | 434571 | 8.08 | 2310 | 2/2 | 0/5 | nothing-left |
| stop-requested.sh prints nothing and exits 3 when there is no .tdd/stop | 6 | 3 | 0 | 0 | 0 | 0 | 249 | 59 | 114 | 20202 | 2642277 | 248880 | 4.32 | 372 | unknown | 1/5 | nothing-structural |
| stop-requested.sh exits 2 with nothing on stdout and a diagnostic on stderr when .tdd/stop's first line is an unknown word or empty | 8 | 3 | 1 | 0 | 0 | 0 | 492 | 96 | 180 | 40846 | 4470592 | 326780 | 6.53 | 2225 | 1/2 | 3/5 | nothing-structural |
| stop-requested.sh --clear removes .tdd/stop and exits 0, and exits 0 when there was no file to remove | 6 | 3 | 0 | 0 | 0 | 0 | 244 | 52 | 94 | 19573 | 2135806 | 251351 | 4.07 | 804 | unknown | 0/5 | nothing-left |
| stop-requested.sh given any other argument exits 2 and leaves .tdd/stop as it was | 6 | 3 | 0 | 0 | 0 | 0 | 265 | 57 | 102 | 20162 | 2391777 | 256774 | 4.27 | 629 | unknown | 0/5 | nothing-left |
| stop-requested.sh --clear with a trailing argument exits 2 and leaves .tdd/stop as it was | 6 | 3 | 0 | 0 | 0 | 0 | 236 | 55 | 98 | 19298 | 2308305 | 260592 | 4.24 | 584 | unknown | 1/5 | nothing-structural |
| the stop-requested suite runs in the fast tier from tests/unit/ and its header states the bar it clears | 2 | 1 | 0 | 0 | 0 | 0 | 184 | 29 | 58 | 14528 | 1648075 | 105316 | 2.24 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 0 | 37 | 12 | 221 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 224 | 1 | 225 | 0 | 0 | 0 | 1 | 224 | 0 | 1 | 0 | 227 | 0 | 0 | 0 | 0 |
| fast | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 221 | 223 | 222 | 222 | 222 | 223 | 224 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 462 | 864 | 181141 | 20742264 | 1884264 | 33.75 |
