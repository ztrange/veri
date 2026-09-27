### 📊 Metrics — issue 526

Wall time for the issue: 4405 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/527.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 14 | 2 | 4 | 1255 | 56923 | 35791 | 0.32 |
| red | 10 | 4 | 1 | 0 | 1171 | 544 | 93 | 180 | 53722 | 5174759 | 541692 | 6.44 |
| green | 10 | 4 | 1 | 0 | 1676 | 490 | 99 | 194 | 48232 | 5027811 | 453252 | 5.60 |
| refactor | 8 | 4 | 0 | 0 | 583 | 291 | 70 | 138 | 29493 | 3391892 | 358712 | 4.14 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 757 | 2.54 | 0 | 0.00 |
| green | 860 | 2.55 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `no-sigpipe-pipelines.test.sh` fails, naming `<suite>:<line>`, a `while` loop under a suite that declares pipefail which can `break` while fed by a process substitution (`done < <(writer …)`), unless an exemption entry carrying a reason names that site — so `skill-event-marks.test.sh` case 13's `tail`-fed loop is reported until it is repaired ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 423 | 80 | 154 | 42278 | 4370693 | 395177 | 4.88 | 1226 | 1/2 | 1/5 | structural-owed |  |  |
| `no-sigpipe-pipelines.test.sh` fails, naming `<suite>:<line>`, a `while` loop that can `break` while fed by a pipe (`writer … | while …`), unless an exemption entry carrying a reason names that site ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 309 | 60 | 118 | 30880 | 3158575 | 308550 | 3.72 | 574 | unknown | 3/5 | structural-owed |  |  |
| Case 13 of `skill-event-marks.test.sh` reads the SKILL.md lines of the over-budget exit 3 branch without leaving any writer mid-stream, and still reports a FAIL naming the line when that branch carries an `event.sh` mark ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 365 | 68 | 134 | 35094 | 3453662 | 369267 | 4.35 | 1039 | 1/2 | 1/5 | nothing-structural |  |  |
| `make test`'s count-line check passes a suite whose exit status is 0 and whose stdout ends in its count line even when a line reaches its stderr after that count line, and still fails a suite whose stdout never reaches its count line ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 228 | 54 | 106 | 23195 | 2611532 | 280662 | 3.23 | 1042 | unknown | 1/5 | nothing-structural |  |  |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 2 | 0 | 9 | 10 | 6 | 3 | 7 | 3 | 4 | 4 | 10 | 7 | 6 | 4 | 4 | 7 | 3 | 6 | 7 | 3 | 1 | 1 | 1 | 1 | 8 | 0 | 1 | 0 | 1 | 35 | 35 | 0 | 71 | 107 | 71 | 0 | 0 | 35 |
| fast | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 0 | 3 | 3 | 1 | 35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 464 | 464 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 264 | 516 | 132702 | 13651385 | 1389447 | 16.50 |
