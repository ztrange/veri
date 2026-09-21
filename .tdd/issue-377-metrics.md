### 📊 Metrics — issue 377

Wall time for the issue: 3159 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/399.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 7 | 3 | 0 | 0 | 509 | 455 | 82 | 146 | 36283 | 3927781 | 367255 | 6.54 |
| green | 8 | 3 | 1 | 0 | 1278 | 538 | 116 | 204 | 42736 | 5593406 | 420919 | 8.08 |
| refactor | 6 | 3 | 0 | 0 | 644 | 582 | 84 | 162 | 49433 | 4621040 | 336526 | 6.91 |
| pin | 1 | 1 | 0 | 0 | 43 | 36 | 6 | 10 | 2058 | 225599 | 44838 | 0.61 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 673 | 3.53 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| leaf-timeout.sh derives the run's hard timeout from the full-tier measurement rather than the fast-tier one: given a recorded pair whose fast tier is quick and whose full tier is slow, the value returned is the one the slow measurement implies | 8 | 3 | 1 | 0 | 0 | 0 | 566 | 99 | 180 | 46366 | 4838628 | 413712 | 7.72 | 1232 | 1/2 | 2/5 | structural-owed |
| SKILL.md's preflight measures the full tier and hands that measurement to leaf-timeout.sh, exporting the result as VERI_TIMEOUT for every leaf, and the plan comment states which tier the number came from | 6 | 3 | 0 | 0 | 0 | 0 | 521 | 97 | 176 | 41964 | 4996138 | 334799 | 6.90 | 727 | unknown | 2/5 | nothing-structural |
| An explicit VERI_TIMEOUT still wins over the sizing and is still printed back verbatim, whatever pair of tier measurements is handed in | 2 | 1 | 0 | 0 | 0 | 0 | 110 | 18 | 34 | 8025 | 874562 | 96989 | 1.61 | 159 | unknown | unknown | unknown |
| leaf-timeout.sh still exits 2 with a diagnostic on stderr and nothing on stdout for a measurement it cannot read — the full-tier one included — and SKILL.md's preflight still refuses to start on that exit | 6 | 3 | 0 | 0 | 0 | 0 | 414 | 74 | 132 | 34155 | 3658498 | 324038 | 5.92 | 786 | unknown | 2/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 1 | 206 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 54 | 0 | 0 | 1 | 1 | 1 | 1 | 2 | 206 | 1 | 1 | 1 |
| fast | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 205 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 288 | 522 | 130510 | 14367826 | 1169538 | 22.14 |
