### 📊 Metrics — issue 355

Wall time for the issue: 3920 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/381.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 7 | 3 | 0 | 0 | 566 | 503 | 91 | 166 | 40241 | 4218781 | 331301 | 6.43 |
| green | 6 | 3 | 0 | 0 | 1420 | 332 | 82 | 138 | 25799 | 3352966 | 268960 | 5.01 |
| refactor | 6 | 3 | 0 | 0 | 1263 | 360 | 69 | 116 | 29046 | 2816398 | 263633 | 4.77 |
| pin | 1 | 1 | 0 | 0 | 48 | 39 | 9 | 14 | 3384 | 297459 | 38596 | 0.62 |

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
| The red verifier prompt states that a run erroring on exactly the name the step introduces — a missing function, script, file, route or field — is a valid red | 6 | 3 | 0 | 0 | 0 | 0 | 411 | 83 | 138 | 33614 | 3404367 | 278107 | 5.32 | 1099 | unknown | 0/5 | nothing-left |
| The red verifier prompt still states that any other error before an assertion is a REJECT: a typo'd name, a wrong path, a missing fixture, a syntax error in the test | 6 | 3 | 0 | 0 | 0 | 0 | 407 | 82 | 146 | 32423 | 3713295 | 275197 | 5.42 | 1640 | unknown | 1/5 | nothing-structural |
| The red verifier prompt no longer requires the target test to reach its assertions | 2 | 1 | 0 | 0 | 0 | 0 | 99 | 21 | 38 | 8373 | 888714 | 83822 | 1.49 | unknown | unknown | unknown | unknown |
| The red developer prompt says a predicted missing-name error names the missing name in PREDICTED_FAILURE: | 6 | 3 | 0 | 0 | 0 | 0 | 317 | 65 | 112 | 24060 | 2679228 | 265364 | 4.60 | 810 | unknown | 0/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 172 | 173 | 173 | 1 | 2 | 1 | 171 | 175 | 172 | 173 | 174 | 173 | 1 | 1 | 1 | 171 | 172 | 3 |
| fast | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 2 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 251 | 434 | 98470 | 10685604 | 902490 | 16.83 |
