### 📊 Metrics — issue 384

Wall time for the issue: 4689 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/406.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 7 | 3 | 0 | 0 | 717 | 605 | 117 | 212 | 45890 | 6075540 | 375883 | 7.94 |
| green | 6 | 3 | 0 | 0 | 1478 | 449 | 96 | 168 | 34155 | 4505793 | 304312 | 6.15 |
| refactor | 6 | 3 | 0 | 0 | 1777 | 829 | 117 | 216 | 62129 | 6744212 | 346165 | 8.39 |
| pin | 1 | 1 | 0 | 0 | 75 | 51 | 14 | 24 | 3647 | 625593 | 50765 | 0.91 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| While the run's current leaf is a verifier, /api/chatter renders that verifier's transcript rather than the empty string | 6 | 3 | 0 | 0 | 0 | 0 | 626 | 107 | 194 | 49036 | 5779749 | 338101 | 7.50 | 1723 | unknown | 3/5 | structural-owed |
| A leaf transcript carrying the plain-text result appended after its stream-json records renders that transcript, rather than the empty string | 6 | 3 | 0 | 0 | 0 | 0 | 609 | 104 | 186 | 48244 | 5522469 | 335831 | 7.33 | 1751 | unknown | 3/5 | structural-owed |
| A run on no leaf, and a leaf that has written nothing yet, each still answer {"chatter": ""} | 2 | 1 | 0 | 0 | 0 | 0 | 191 | 43 | 74 | 14529 | 2287561 | 116638 | 2.67 | unknown | unknown | unknown | unknown |
| render-leaf-log.sh's header states what the script actually does with a line that is not JSON | 6 | 3 | 0 | 0 | 0 | 0 | 508 | 90 | 166 | 34012 | 4361359 | 286555 | 5.90 | 653 | unknown | 1/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 9 | 223 | 223 | 9 | 9 | 9 | 10 | 222 | 10 | 9 | 10 | 222 | 222 | 10 | 223 | 10 | 224 | 9 | 0 | 0 | 0 | 10 | 0 | 1 | 0 | 0 |
| fast | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 9 | 9 | 9 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 344 | 620 | 145821 | 17951138 | 1077125 | 23.40 |
