### 📊 Metrics — issue 416

Wall time for the issue: 4549 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/421.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 14 | 5 | 0 | 0 | 1037 | 792 | 130 | 222 | 61291 | 5857374 | 722309 | 11.69 |
| green | 10 | 5 | 0 | 0 | 897 | 577 | 114 | 198 | 45375 | 5004805 | 470392 | 8.34 |
| refactor | 10 | 5 | 0 | 0 | 1096 | 906 | 119 | 228 | 66127 | 6642040 | 535632 | 10.33 |
| pin | 4 | 4 | 0 | 0 | 288 | 170 | 42 | 76 | 13511 | 1810391 | 174957 | 2.99 |

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
| A range of a `.tdd/` ledger file plus one source change answers only that source change's suites, placing the run state as affecting none | 6 | 3 | 0 | 0 | 0 | 0 | 249 | 54 | 100 | 21166 | 2397799 | 266990 | 4.40 | 501 | unknown | 1/5 | nothing-structural |
| A range whose files are all `.tdd/` run state exits 3 — nothing to do — rather than printing an empty answer | 6 | 3 | 0 | 0 | 0 | 0 | 241 | 48 | 80 | 18391 | 1831039 | 263892 | 4.01 | 465 | unknown | 1/5 | nothing-structural |
| An unplaced path that is not `.tdd/` run state still widens the answer to every suite | 2 | 1 | 0 | 0 | 0 | 0 | 163 | 23 | 42 | 10947 | 1118067 | 104378 | 1.88 | 249 | unknown | unknown | unknown |
| The widening stderr line still names every unplaced file that caused it | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 19 | 36 | 6554 | 934751 | 99264 | 1.62 | 153 | unknown | unknown | unknown |
| A green-commit-shaped range — ledger, refactor-owed file and a real source change together — answers narrowly, pinning the regression | 2 | 1 | 0 | 0 | 0 | 0 | 110 | 23 | 42 | 8012 | 1118373 | 105433 | 1.81 | 204 | unknown | unknown | unknown |
| A range that adds or deletes a file under `tests/` or `tests/unit/` includes `claude-md-counts.test.sh` in the affected set | 6 | 3 | 0 | 0 | 0 | 0 | 474 | 66 | 120 | 38840 | 3488481 | 314361 | 5.86 | 725 | unknown | 3/5 | structural-owed |
| Editing an existing suite's contents does not include `claude-md-counts.test.sh` | 2 | 1 | 0 | 0 | 0 | 0 | 102 | 18 | 32 | 8094 | 900443 | 109426 | 1.75 | 183 | unknown | unknown | unknown |
| A range that adds or deletes a script under `scripts/` also includes `claude-md-counts.test.sh`, since CLAUDE.md hand-types the script count beside the suite count | 6 | 3 | 0 | 0 | 0 | 0 | 417 | 70 | 120 | 31863 | 3211559 | 306607 | 5.47 | 658 | unknown | 2/5 | structural-owed |
| The full suite is green: `no-nested-suites.test.sh` does not read `affected-suites.test.sh`'s fixture and expectation mentions of `claude-md-counts.test.sh` as launching it | 6 | 3 | 0 | 0 | 0 | 0 | 605 | 84 | 152 | 42437 | 4314098 | 332939 | 6.55 | 773 | unknown | 2/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 6 | 6 | 7 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 8 | 8 | 8 | 8 | 5 | 5 | 5 | 4 | 5 | 8 | 9 | 9 | 9 | 9 | 9 | 10 | 9 | 9 | 9 | 0 | 0 | 0 | 5 | 5 | 5 | 5 | 5 | 0 | 1 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 7 | 6 | 6 | 7 | 6 | 7 | 7 | 8 | 8 | 8 | 8 | 8 | 9 | 2 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 405 | 724 | 186304 | 19314610 | 1903290 | 33.35 |
