### 📊 Metrics — issue 411

Wall time for the issue: 2215 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/435.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 2 | 0 | 0 | 646 | 611 | 85 | 152 | 44009 | 4448921 | 300432 | 6.33 |
| green | 4 | 2 | 0 | 0 | 541 | 383 | 73 | 138 | 29377 | 3962488 | 224247 | 4.96 |
| refactor | 4 | 2 | 0 | 0 | 396 | 354 | 48 | 96 | 23484 | 2484434 | 189629 | 3.73 |
| pin | 1 | 1 | 0 | 0 | 64 | 56 | 15 | 26 | 4658 | 668594 | 47250 | 0.92 |

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
| the removal-verb probe reports a problem naming the clear-refactor-pending.sh entry when that entry names no removal verb in prose though the filename supplies one | 6 | 3 | 0 | 0 | 0 | 0 | 505 | 90 | 162 | 38175 | 4517848 | 320571 | 6.42 | 722 | unknown | 1/5 | nothing-structural |
| against SKILL.md as committed the removal-verb probe reports no problem, so a true entry stays green | 2 | 1 | 0 | 0 | 0 | 0 | 206 | 34 | 64 | 13138 | 1810557 | 107551 | 2.31 | unknown | unknown | unknown | unknown |
| every other probe of the script reference list case still reports its problem when the entry it reads carries none of what it asks for | 6 | 3 | 0 | 0 | 0 | 0 | 693 | 97 | 186 | 50215 | 5236032 | 333436 | 7.21 | 921 | unknown | 2/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 12 | 0 | 0 | 1 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 221 | 412 | 101528 | 11564437 | 761558 | 15.94 |
