### 📊 Metrics — issue 487

Wall time for the issue: 2077 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/511.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 4 | 1 | 2 | 409 | 11207 | 33996 | 0.28 |
| red | 7 | 2 | 0 | 0 | 401 | 270 | 53 | 104 | 25646 | 2503185 | 327368 | 3.63 |
| green | 4 | 2 | 0 | 0 | 245 | 113 | 28 | 52 | 11171 | 1143725 | 166130 | 1.78 |
| refactor | 4 | 2 | 0 | 0 | 149 | 93 | 23 | 46 | 8389 | 983126 | 159403 | 1.64 |
| pin | 3 | 3 | 0 | 0 | 127 | 47 | 12 | 24 | 4532 | 450564 | 110668 | 1.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A lib file whose caller's `source` line ends in a `\` continuation maps to that caller's suite ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 137 | 33 | 64 | 12021 | 1338329 | 238317 | 2.41 | 358 | unknown | 0/5 | nothing-left |
| A caller whose `source` line ends at the lib path, with or without a trailing quote and trailing spaces, still maps to its suite ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 11 | 22 | 6236 | 479474 | 82723 | 0.88 | unknown | unknown | unknown | unknown |
| A comment line that names a lib file is still not a dependency: the commenting script's suite is not selected ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 13 | 26 | 5541 | 595377 | 82957 | 0.89 | unknown | unknown | unknown | unknown |
| In the real repo, a change to `lib/bug-section.sh` selects both `build-develop-prompt.test.sh` and `build-verify-prompt.test.sh` ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 14 | 28 | 6516 | 655813 | 85464 | 0.95 | unknown | unknown | unknown | unknown |
| Repair: `no-nested-suites.test.sh` is green again — `affected-suites.test.sh` names no real suite file in a shape that guard reads as launching it, while criterion 4 stays pinned ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 204 | 45 | 86 | 19424 | 2011607 | 274108 | 2.98 | 378 | unknown | 1/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 10 | 9 | 10 | 9 | 10 | 10 | 11 | 0 | 0 | 10 | 12 | 0 | 0 | 11 | 1 | 1 |
| fast | 3 | 3 | 3 | 4 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 9 | 10 | 10 | 10 | 10 | 11 | 11 | 0 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 117 | 228 | 50147 | 5091807 | 797565 | 8.40 |
