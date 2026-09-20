### 📊 Metrics — issue 342

Wall time for the issue: 7431 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/370.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 19 | 7 | 1 | 1 | 2768 | 1420 | 236 | 424 | 117719 | 11900069 | 973973 | 18.63 |
| green | 20 | 7 | 3 | 0 | 3095 | 1287 | 260 | 464 | 95958 | 11730012 | 927783 | 17.54 |
| refactor | 16 | 7 | 0 | 0 | 1783 | 1050 | 194 | 346 | 81886 | 9163631 | 632177 | 12.95 |
| pin | 2 | 1 | 1 | 0 | 220 | 172 | 28 | 46 | 14537 | 1329343 | 87064 | 1.90 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 1269 | 4.12 | 0 | 0.00 |
| green | 2427 | 10.26 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 220 | 1.90 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| a test-command run made through the new wrapper writes one `test-run` event carrying `tier`, `suites` and `seconds`, and exits with the command's own status | 6 | 3 | 0 | 0 | 0 | 0 | 397 | 78 | 134 | 30786 | 3369451 | 296157 | 5.42 | 651 | unknown | 2/5 | structural-owed |
| the "usual" for a tier is the median of that tier's last 10 `test-run` events' seconds, read out of `.tdd/events.jsonl` | 11 | 3 | 2 | 1 | 1 | 0 | 682 | 129 | 218 | 53539 | 5408618 | 478490 | 8.83 | 6013 | 2/2 | 1/5 | nothing-structural |
| `VERI_UNIT_BUDGET` and `VERI_TIME_WARN_RATIO` unset resolve to `10` and `1.5`, and a non-numeric value for either exits 2 with a diagnostic naming the variable | 8 | 3 | 1 | 0 | 0 | 0 | 378 | 78 | 148 | 30273 | 3489557 | 340308 | 5.91 | 1160 | 1/2 | 0/5 | nothing-left |
| a unit-tier run whose seconds exceed `VERI_UNIT_BUDGET` is over budget; at or under it, it is not | 6 | 3 | 0 | 0 | 0 | 0 | 381 | 74 | 134 | 31548 | 3347561 | 268093 | 5.14 | 637 | unknown | 3/5 | nothing-structural |
| a run of any tier whose seconds exceed `VERI_TIME_WARN_RATIO` × its usual is over budget; at or under the ratio, it is not | 6 | 3 | 0 | 0 | 0 | 0 | 380 | 73 | 134 | 31329 | 3395183 | 273274 | 5.21 | 612 | unknown | 3/5 | nothing-structural |
| the over-budget answer prints exactly one `⏱` line for a run over budget and nothing for one that is not, and SKILL.md instructs the conductor to paste that line into the phase's narration and to branch on nothing | 8 | 3 | 1 | 0 | 0 | 0 | 759 | 124 | 222 | 55516 | 5947853 | 415194 | 8.51 | 1915 | 1/2 | 1/5 | nothing-structural |
| an over-budget test run leaves a run's outcome alone: the verdict stands and nothing retries or bails because of the seconds | 4 | 1 | 1 | 0 | 0 | 0 | 440 | 61 | 104 | 37211 | 3312484 | 234380 | 4.93 | unknown | 1/2 | unknown | unknown |
| `metrics.sh <issue>` prints a new per-tier section of the `test-run` events' recorded seconds, reading only `.tdd/events.jsonl` | 8 | 3 | 0 | 0 | 0 | 0 | 512 | 101 | 186 | 39898 | 5852348 | 315101 | 7.08 | 807 | unknown | 2/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 718 | 1280 | 310100 | 34123055 | 2620997 | 51.03 |
