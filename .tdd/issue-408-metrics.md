### 📊 Metrics — issue 408

Wall time for the issue: 8903 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/413.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 12 | 6 | 0 | 0 | 1217 | 1097 | 178 | 314 | 89230 | 9008295 | 661837 | 13.35 |
| green | 18 | 6 | 3 | 0 | 4720 | 1427 | 271 | 486 | 116721 | 13010037 | 905041 | 18.48 |
| refactor | 12 | 6 | 0 | 0 | 2022 | 1239 | 202 | 384 | 92593 | 11187527 | 652695 | 14.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3792 | 13.10 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| build-develop-prompt.sh accepts an `exhausted` phase and renders its template carrying the step, the verifier's last rejection reason and the issue spec, refusing a missing reason file with exit 2 | 6 | 3 | 0 | 0 | 0 | 0 | 503 | 98 | 170 | 38615 | 4790242 | 320862 | 6.57 | 727 | unknown | 2/5 | structural-owed |
| exhausted-outcome.sh reads the leaf's report on stdin and answers which of the three outcomes it holds: exit 0 printing the SPLIT: criteria, exit 1 printing the needs-user answer, exit 3 printing nothing when it reports neither | 10 | 3 | 2 | 0 | 0 | 0 | 900 | 136 | 256 | 68208 | 6828541 | 484833 | 9.97 | 2256 | 2/2 | 2/5 | structural-owed |
| add-ledger-step.sh takes `instead-of` as a third placement, inserting the texts where the anchor step was and removing that step, under the same VERI_STEP_GROWTH budget and owed-steps refusal | 6 | 3 | 0 | 0 | 0 | 0 | 326 | 69 | 122 | 25821 | 3009280 | 277700 | 4.93 | 698 | unknown | 0/5 | nothing-left |
| SKILL.md's revise-exhausted branch launches the exhausted leaf and branches three ways — replace-and-continue on SPLIT:, park on needs-user, and the unchanged revise-exhausted bail on neither | 6 | 3 | 0 | 0 | 0 | 0 | 597 | 97 | 180 | 48187 | 5198923 | 332956 | 7.13 | 964 | unknown | 1/5 | structural-owed |
| the three outcomes are distinguishable marks in the run's event log, and a split reached this way is told apart from a leaf-volunteered one | 6 | 3 | 0 | 0 | 0 | 0 | 688 | 117 | 214 | 56015 | 6454290 | 359494 | 8.22 | 1685 | unknown | 2/5 | structural-owed |
| a parked step is mirrored to the issue thread with the leaf's answer and the verifier's last rejection reason, so the user reads why without opening a log | 8 | 3 | 1 | 0 | 0 | 0 | 749 | 134 | 242 | 61698 | 6924583 | 443728 | 9.44 | 2236 | 1/2 | 2/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 39 | 11 | 0 | 43 | 42 | 0 | 1 | 0 | 0 | 0 | 0 | 238 | 0 | 0 | 0 | 0 | 62 | 62 | 61 | 0 | 0 | 0 | 1 | 62 | 62 | 240 | 2 | 2 | 0 | 0 | 0 | 55 | 62 | 98 | 97 | 98 | 0 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 238 | 239 | 232 | 238 | 240 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 651 | 1184 | 298544 | 33205859 | 2219573 | 46.27 |
