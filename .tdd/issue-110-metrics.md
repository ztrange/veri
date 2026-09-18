### 📊 Metrics — issue 110

Wall time for the issue: 16709 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/294.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 15 | 7 | 0 | 0 | 3141 | 1302 | 175 | 328 | 99597 | 8742700 | 731372 | 10.92 |
| green | 15 | 6 | 0 | 0 | 10911 | 692 | 161 | 308 | 48779 | 7864004 | 622736 | 7.71 |
| refactor | 12 | 6 | 0 | 0 | 4889 | 1281 | 171 | 340 | 95669 | 9618906 | 594451 | 10.01 |
| pin | 1 | 1 | 0 | 0 | 147 | 78 | 15 | 30 | 4244 | 957421 | 55701 | 0.46 |

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
| dashboard.sh starts a stdlib-only Python server on default port 8765 serving the one HTML page at / and exits 0 when sent SIGINT ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 522 | 77 | 152 | 37885 | 3897515 | 262732 | 4.17 | 2339 | unknown | 0/5 | nothing-structural |
| dashboard.sh binds the port given as its argument, and binds 127.0.0.1 only — never another interface ⟦criterion 1⟧ | 11 | 4 | 0 | 0 | 0 | 1 | 519 | 92 | 166 | 38737 | 3979529 | 434346 | 5.06 | 3960 | unknown | 3/5 | structural-owed |
| The Runs endpoint returns what status.sh --json returns ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 539 | 82 | 158 | 39922 | 4346059 | 300574 | 4.51 | 2147 | unknown | 4/5 | structural-owed |
| The Metrics endpoint returns the per-issue table, recomputed from the event log for a running run and read from the committed report for a finished one ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 649 | 97 | 182 | 49436 | 5470791 | 336600 | 5.50 | 3001 | unknown | 5/5 | budget |
| The Events endpoint returns the selected run's events.jsonl tail, newest last ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 590 | 83 | 166 | 41934 | 4722055 | 304019 | 5.00 | 4926 | unknown | 4/5 | structural-owed |
| The served page's Runs, Metrics and Events panes each poll their own JSON endpoint every 2 seconds ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 393 | 65 | 130 | 29930 | 3271754 | 257716 | 3.46 | 3803 | unknown | 1/5 | nothing-structural |
| make test runs a dashboard suite that starts the server on a spare port against fabricated run fixtures and asserts each endpoint's JSON ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 141 | 26 | 52 | 10445 | 1495328 | 108273 | 1.41 | 263 | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 522 | 1006 | 248289 | 27183031 | 2004260 | 29.11 |
