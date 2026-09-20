### 📊 Metrics — issue 373

Wall time for the issue: 5367 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/379.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 10 | 4 | 0 | 0 | 959 | 835 | 154 | 268 | 63634 | 7571761 | 545318 | 10.83 |
| green | 8 | 4 | 0 | 0 | 2095 | 525 | 130 | 216 | 40149 | 5678288 | 397322 | 7.82 |
| refactor | 8 | 4 | 0 | 0 | 1493 | 521 | 99 | 194 | 36787 | 5000149 | 393517 | 7.36 |
| pin | 2 | 2 | 0 | 0 | 89 | 74 | 21 | 32 | 6358 | 714147 | 84413 | 1.36 |

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
| a developer green prompt names `timed-test-run.sh` at a path the leaf can run, and tells it to run the fast command and the affected suites through that wrapper under the tiers `fast` and `affected` | 6 | 3 | 0 | 0 | 0 | 0 | 367 | 82 | 144 | 29223 | 3717202 | 293801 | 5.53 | unknown | unknown | 1/5 | nothing-structural |
| the other developer prompts — red, refactor, revise, reconcile — name the same wrapper and the tier each of their test-command runs uses | 6 | 3 | 0 | 0 | 0 | 0 | 476 | 90 | 158 | 33132 | 4305639 | 313332 | 6.12 | unknown | unknown | 2/5 | structural-owed |
| a verifier prompt — red, green, refactor, pin — names the same wrapper at a runnable path and the tier each of its test-command runs uses | 6 | 3 | 0 | 0 | 0 | 0 | 442 | 94 | 162 | 34214 | 4409078 | 324382 | 6.30 | unknown | unknown | 0/5 | nothing-left |
| a log carrying `test-run` marks renders at least one row under `#### Test-command seconds, by tier` in its metrics | 2 | 1 | 0 | 0 | 0 | 0 | 247 | 40 | 68 | 15021 | 2095321 | 119415 | 2.62 | unknown | unknown | unknown | unknown |
| `tier-usual.sh` answers with a figure taken from a log carrying `test-run` marks rather than from an empty list | 2 | 1 | 0 | 0 | 0 | 0 | 138 | 26 | 48 | 11928 | 1204387 | 93664 | 1.84 | unknown | unknown | unknown | unknown |
| a verify-green leaf's target-test run in check 1 also goes through the wrapper, naming tier `target` | 6 | 3 | 0 | 0 | 0 | 0 | 285 | 72 | 130 | 23410 | 3232718 | 275976 | 4.96 | unknown | unknown | 1/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 169 | 170 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 404 | 710 | 146928 | 18964345 | 1420570 | 27.36 |
