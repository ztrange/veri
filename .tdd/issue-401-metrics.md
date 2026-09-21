### 📊 Metrics — issue 401

Wall time for the issue: 3656 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/403.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 8 | 3 | 0 | 0 | 533 | 430 | 75 | 128 | 34184 | 3321171 | 403900 | 6.55 |
| green | 6 | 3 | 0 | 0 | 419 | 253 | 63 | 110 | 21283 | 2594433 | 259603 | 4.43 |
| refactor | 6 | 3 | 0 | 0 | 396 | 309 | 53 | 102 | 24200 | 2485132 | 277859 | 4.63 |
| pin | 2 | 2 | 0 | 0 | 98 | 64 | 15 | 30 | 5251 | 658539 | 78909 | 1.25 |

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
| a range whose only changed file is a prompt under scripts/prompts/ answers with the suites that name that prompt, not with every suite | 6 | 3 | 0 | 0 | 0 | 0 | 231 | 49 | 88 | 18105 | 2023406 | 260468 | 4.07 | 433 | unknown | 1/5 | nothing-structural |
| a range touching both a prompt and a suite answers with that suite and the prompt's suites, and does not widen to every suite | 2 | 1 | 0 | 0 | 0 | 0 | 86 | 15 | 30 | 7095 | 727131 | 93056 | 1.47 | unknown | unknown | unknown | unknown |
| a file that matches no placement rule still widens the answer to every suite | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 23 | 40 | 7778 | 1101081 | 102800 | 1.77 | unknown | unknown | unknown | unknown |
| a widened answer names on stderr the file that forced the widening | 6 | 3 | 0 | 0 | 0 | 0 | 317 | 57 | 106 | 24544 | 2583899 | 282597 | 4.73 | 543 | unknown | 2/5 | nothing-structural |
| the widening-names-the-file case pins stderr without any suite line naming a path in the generated-documentation tree, so no-docs-reads.test.sh stays green | 6 | 3 | 0 | 0 | 0 | 0 | 326 | 62 | 106 | 27396 | 2623758 | 281350 | 4.81 | 487 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 3 | 6 | 6 | 6 | 44 | 6 | 6 | 6 | 4 | 7 | 7 | 6 | 6 | 6 |
| fast | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 5 | 5 | 6 | 5 | 6 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 206 | 370 | 84918 | 9059275 | 1020271 | 16.86 |
