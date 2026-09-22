### 📊 Metrics — issue 418

Wall time for the issue: 7401 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/420.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 14 | 6 | 0 | 0 | 1745 | 1424 | 228 | 402 | 106268 | 12085415 | 835325 | 17.05 |
| green | 14 | 6 | 1 | 0 | 3209 | 1650 | 273 | 488 | 126016 | 14777497 | 823181 | 18.77 |
| refactor | 12 | 6 | 0 | 0 | 1424 | 1141 | 168 | 320 | 82404 | 9318586 | 675756 | 13.48 |
| pin | 2 | 2 | 0 | 0 | 154 | 78 | 18 | 30 | 5386 | 695751 | 86926 | 1.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2062 | 7.28 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Running one suite directly through the repository's suite runner exits non-zero, naming the suite, when that suite exits 0 without printing its `<n> passed, <m> failed` count line | 6 | 3 | 0 | 0 | 0 | 0 | 564 | 95 | 174 | 43079 | 5323014 | 354799 | 7.29 | 963 | unknown | 1/5 | structural-owed |
| That runner runs one named suite without setting `TESTS=`, so no nested make inherits it | 2 | 1 | 0 | 0 | 0 | 0 | 182 | 30 | 52 | 13998 | 1595059 | 116079 | 2.31 | unknown | unknown | unknown | unknown |
| The `make test` target and the direct invocation report a countless suite identically, from one guard rather than two that can drift | 8 | 3 | 1 | 0 | 0 | 0 | 1458 | 172 | 316 | 109557 | 10307045 | 536884 | 13.26 | 2969 | 1/2 | 2/5 | structural-owed |
| Every developer prompt names the one invocation to use for running a single suite | 6 | 3 | 0 | 0 | 0 | 0 | 487 | 92 | 170 | 36478 | 4726700 | 317310 | 6.45 | 753 | unknown | 1/5 | structural-owed |
| Every developer prompt that names `run-suite.sh` tells its leaf what to run when the target repository has no such runner | 6 | 3 | 0 | 0 | 0 | 0 | 517 | 105 | 184 | 38294 | 5246120 | 332493 | 6.91 | 644 | unknown | 1/5 | structural-owed |
| Every blind verifier prompt names that same invocation, so a verifier cannot render PASS over a partially-dead suite | 6 | 3 | 0 | 0 | 0 | 0 | 456 | 85 | 150 | 33471 | 4274832 | 333829 | 6.31 | 568 | unknown | 1/5 | structural-owed |
| Every blind verifier prompt that names `run-suite.sh` tells its leaf what to run when the target repository has no such runner | 6 | 3 | 0 | 0 | 0 | 0 | 359 | 80 | 142 | 27881 | 3872333 | 312042 | 5.75 | 468 | unknown | 1/5 | structural-owed |
| A suite pins the guard against the deliberately partially-dead fixture invoked directly, not only through the make target | 2 | 1 | 0 | 0 | 0 | 0 | 270 | 28 | 52 | 17316 | 1532146 | 117752 | 2.38 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 16 | 17 | 16 | 15 | 17 | 15 | 14 | 15 | 15 | 15 | 15 | 15 | 18 | 18 | 17 | 31 | 33 | 31 | 33 | 17 | 58 | 18 | 17 | 18 | 18 | 1 | 1 | 37 | 38 | 43 | 0 | 1 | 0 | 2 | 7 | 7 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 3 | 3 | 1 | 18 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 15 | 14 | 15 | 18 | 18 | 1 | 0 | 1 | 1 | 18 | 17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 242 | 243 | 240 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 687 | 1240 | 320074 | 36877249 | 2421188 | 50.66 |
