### 📊 Metrics — issue 331

Wall time for the issue: 5222 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/347.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 11 | 3 | 0 | 0 | 971 | 697 | 102 | 192 | 66200 | 5040249 | 553699 | 9.71 |
| green | 6 | 3 | 0 | 0 | 1704 | 216 | 48 | 90 | 20733 | 2233080 | 288016 | 4.52 |
| refactor | 6 | 3 | 0 | 0 | 584 | 116 | 29 | 56 | 10427 | 1134482 | 239857 | 3.23 |
| pin | 5 | 4 | 1 | 0 | 1013 | 156 | 38 | 74 | 14124 | 1586911 | 204492 | 3.19 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 577 | 1.32 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| harvest-usage.test.sh cases 1 and 2 launch the fixture leaf through a real run-leaf.sh against a stub claude, with its combined output in .tdd/<leaf>.log, not through supervise.sh and never a hand-written log, and that log's usage record is still not its last line ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 245 | 45 | 82 | 24981 | 2108150 | 288385 | 4.56 | 1622 | unknown | 0/5 | nothing-structural |
| harvest-usage.test.sh case 2 still asserts no usage line and a stderr diagnostic naming the harvester and the leaf, and its setup probe still refuses to run when the event log a real writer left behind is empty ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 101 | 16 | 30 | 9357 | 727776 | 95255 | 1.55 | unknown | unknown | unknown | unknown |
| harvest-usage.test.sh case 1's eight-number comparison runs in one python3 process and still goes red naming the one field whose expected value is wrong ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 239 | 41 | 78 | 22919 | 1957274 | 288265 | 4.43 | 800 | unknown | 2/5 | structural-owed |
| harvest-usage.test.sh's total python3 starts, counted by a PATH-first counting shim, are at most 8 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 18 | 34 | 7240 | 821310 | 93040 | 1.52 | unknown | unknown | unknown | unknown |
| metrics.test.sh's total python3 starts, counted by a PATH-first counting shim, are at most 21 — one per case — with every case's assertions unchanged ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 231 | 46 | 88 | 20715 | 2070077 | 253274 | 4.09 | 1093 | unknown | 0/5 | nothing-structural |
| harvest-usage.test.sh case 3 is unchanged: a hand-written one-line log fixture, no launch, exit 2, no usage line, a diagnostic naming the harvester or leaf-role ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 16 | 30 | 8909 | 708298 | 98721 | 1.56 | unknown | unknown | unknown | unknown |
| every metrics.test.sh and harvest-usage.test.sh assertion that passed before still passes, and make test is green ⟦criterion 7⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 193 | 35 | 70 | 17363 | 1601837 | 169124 | 2.93 | unknown | 1/2 | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 217 | 412 | 111484 | 9994722 | 1286064 | 20.65 |
