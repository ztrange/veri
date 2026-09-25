### 📊 Metrics — issue 462

Wall time for the issue: 2670 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/463.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 13 | 2 | 4 | 1246 | 55702 | 33947 | 0.31 |
| red | 14 | 6 | 0 | 0 | 926 | 452 | 102 | 200 | 40072 | 4608681 | 582742 | 6.39 |
| green | 12 | 6 | 0 | 0 | 667 | 335 | 93 | 182 | 30559 | 3940961 | 473162 | 5.19 |
| refactor | 12 | 6 | 0 | 0 | 440 | 288 | 75 | 150 | 25808 | 3231815 | 476028 | 4.97 |
| pin | 1 | 1 | 0 | 0 | 37 | 18 | 4 | 8 | 1672 | 148732 | 36472 | 0.35 |

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
| workqueue.sh assign with no worker, or with a worker and no issue, exits 2 and leaves .tdd/workqueue byte-identical ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 186 | 46 | 92 | 17319 | 2035036 | 282677 | 3.02 | 678 | 1/2 | 1/5 | nothing-structural |
| workqueue.sh assign naming the same issue twice in one call exits 2 and leaves .tdd/workqueue byte-identical ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 42 | 84 | 14972 | 1832737 | 239932 | 2.59 | 291 | unknown | 0/5 | structural-owed |
| workqueue.sh assign given an empty issue argument exits 2 and leaves .tdd/workqueue byte-identical ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 159 | 43 | 82 | 14351 | 1792077 | 239800 | 2.56 | 275 | unknown | 0/5 | structural-owed |
| workqueue.sh done with a worker and an issue but no merge sha exits 2 and leaves .tdd/workqueue byte-identical ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 189 | 44 | 84 | 15641 | 1875303 | 244524 | 2.64 | 344 | unknown | 1/5 | nothing-left |
| workqueue.sh done with an empty merge sha argument ("") exits 2 and leaves .tdd/workqueue byte-identical ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 134 | 39 | 78 | 11459 | 1632760 | 229046 | 2.39 | 269 | unknown | 0/5 | nothing-structural |
| workqueue.sh park with a reason containing a tab or a newline treats both characters the same way, either keeping the queue one line per item with four tab-separated fields or refusing with the file untouched ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 192 | 44 | 88 | 17351 | 1964972 | 244911 | 2.70 | 334 | unknown | 1/5 | nothing-structural |
| workqueue.sh show <worker> prints only that worker's group, and for a worker with no items prints nothing and exits 0 ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 16 | 32 | 7018 | 797304 | 87514 | 1.00 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 6 | 6 | 6 | 7 | 0 | 6 | 6 | 6 | 7 | 6 | 0 | 6 | 0 | 6 | 0 | 7 | 6 | 6 | 6 | 1 | 0 | 6 | 7 | 8 | 6 | 8 | 7 | 0 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 6 | 7 | 7 | 8 | 7 | 0 | 7 | 0 | 7 | 8 |
| all | 307 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 3 | 2 | 2 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 7 | 7 | 0 | 6 | 6 | 7 | 7 | 8 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 276 | 544 | 99357 | 11985891 | 1602351 | 17.21 |
