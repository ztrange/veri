### 📊 Metrics — issue 512

Wall time for the issue: unknown s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 5 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 2 | 4 | 840 | 56558 | 36404 | 0.32 |
| red | 6 | 3 | 0 | 0 | 640 | 301 | 52 | 102 | 27891 | 2644779 | 296047 | 3.46 |
| green | 6 | 3 | 0 | 0 | 938 | 232 | 54 | 102 | 21778 | 2407481 | 266354 | 3.05 |
| refactor | 6 | 3 | 0 | 0 | 435 | 186 | 45 | 90 | 17440 | 2024665 | 244414 | 2.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The clock-suspend stub records the suspension before, or atomically with, its clock jump, so the injected awake clock never reads higher than the true awake seconds at any moment during the stub's run ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 202 | 47 | 90 | 18459 | 2092086 | 257784 | 2.85 | 692 | unknown | 1/5 | nothing-structural |
| Case 50's slept-through leaf stays suspended across two watchdog polls before it exits 0, and still reports status 0 with secs in the awake range ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 237 | 53 | 104 | 22094 | 2522181 | 271311 | 3.12 | 888 | unknown | 1/5 | nothing-structural |
| Repair: clock-suspend moves the wall clock and the awake clock in one atomic write, so no watchdog poll ever sees one moved without the other — case 50 still failed status=2 in 1 of 17 runs because, with the suspension recorded first, one poll saw the awake clock 100 s behind the wall clock, supervise.sh credited that as sleep, a log write at the same poll reset seen_at and discarded the credit, and the next poll read 100 s of silence ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 280 | 51 | 100 | 26556 | 2462658 | 277720 | 3.25 | 739 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 33 | 33 | 33 | 33 | 6 | 0 | 1 | 34 | 33 | 33 | 33 | 34 | 35 | 35 | 0 | 34 | 34 | 36 | 35 | 35 | 35 | 35 | 35 |
| fast | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 34 | 35 | 35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 153 | 298 | 67949 | 7133483 | 843219 | 9.53 |
