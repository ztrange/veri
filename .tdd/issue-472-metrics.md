### 📊 Metrics — issue 472

Wall time for the issue: 7601 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/476.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 18 | 2 | 4 | 1750 | 56033 | 39220 | 0.36 |
| red | 11 | 4 | 0 | 0 | 1382 | 556 | 104 | 198 | 54058 | 5240203 | 561569 | 6.62 |
| green | 12 | 4 | 2 | 0 | 2984 | 526 | 119 | 234 | 51073 | 5880622 | 472594 | 5.98 |
| refactor | 8 | 4 | 0 | 0 | 606 | 272 | 70 | 134 | 26456 | 3225405 | 351622 | 3.99 |
| pin | 3 | 3 | 0 | 0 | 1356 | 117 | 28 | 54 | 11557 | 1259127 | 140535 | 1.61 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1886 | 4.11 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A leaf that is silent only across a simulated suspend longer than VERI_HEARTBEAT (injected clock: suspended time advances, awake time does not) is not killed for silence and finishes with its own exit code ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 379 | 78 | 154 | 36234 | 3726215 | 377594 | 4.49 | 1746 | 2/2 | 1/5 | nothing-structural |
| With VERI_AWAKE_CLOCK unset, supervise.sh still measures awake time on a real clock that does not advance while the machine is suspended, on macOS and on Linux, so a run nobody configured does not count a suspend as leaf silence ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 319 | 73 | 138 | 32023 | 3740714 | 301912 | 3.80 | 1582 | unknown | 2/5 | structural-owed |
| A leaf whose run spans a simulated suspend that would put wall time past VERI_TIMEOUT, while its awake time stays under it, is not killed for the timeout and finishes with its own exit code ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 246 | 58 | 114 | 23579 | 2825155 | 278662 | 3.27 | 668 | unknown | 2/5 | structural-owed |
| A leaf silent while the machine is awake (injected clock, no suspend) is still killed as stuck once its awake silence passes VERI_HEARTBEAT, at the same threshold as today ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 136 | 22 | 42 | 13033 | 1113614 | 107913 | 1.35 | unknown | unknown | unknown | unknown |
| A noisy leaf running while the machine is awake (injected clock, no suspend) is still killed once its awake run time passes VERI_TIMEOUT, at the same threshold as today ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 99 | 20 | 40 | 9697 | 1026840 | 103660 | 1.23 | unknown | unknown | unknown | unknown |
| The injected clock a suite drives can simulate a suspend with no real sleep and no real suspend, and the two suspend cases (heartbeat and timeout) run on it, each having been watched failing against the pre-fix supervisor ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 92 | 20 | 36 | 9421 | 954054 | 104634 | 1.22 | unknown | unknown | unknown | unknown |
| supervise.sh's header names the clock source the watchdog measures with and states why it pauses while the machine is suspended, for macOS and for Linux ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 50 | 96 | 19157 | 2218765 | 251945 | 2.84 | 569 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 21 | 22 | 21 | 57 | 23 | 22 | 22 | 21 | 21 | 20 | 24 | 25 | 24 | 27 | 23 | 24 | 25 | 25 | 25 | 24 | 25 | 24 | 25 | 27 | 27 | 27 | 27 | 27 | 29 | 28 | 27 |
| fast | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 22 | 21 | 22 | 25 | 25 | 25 | 405 | 32 | 27 | 27 | 635 | 27 | 26 | 27 | 0 | 27 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 344 | 341 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 323 | 624 | 144894 | 15661390 | 1565540 | 18.56 |
