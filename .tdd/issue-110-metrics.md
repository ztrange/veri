### 📊 Metrics — issue 110

Wall time for the issue: unknown s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 1 of 7 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 385 | 273 | 32 | 60 | 19955 | 1457079 | 167004 | 2.34 |
| green | 5 | 1 | 0 | 0 | 2536 | 270 | 60 | 112 | 19652 | 2863434 | 198539 | 2.50 |
| refactor | 2 | 1 | 0 | 0 | 648 | 176 | 26 | 52 | 12541 | 1294896 | 83223 | 1.29 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 162 | 0.97 |
| green | 0 | 0.00 | 1191 | 0.99 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| dashboard.sh starts a stdlib-only Python server on default port 8765 serving the one HTML page at / and exits 0 when sent SIGINT ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 522 | 77 | 152 | 37885 | 3897515 | 262732 | 4.17 | 2339 | unknown | 0/5 | nothing-structural |
| dashboard.sh binds the port given as its argument, and binds 127.0.0.1 only — never another interface ⟦criterion 1⟧ | 5 | 1 | 0 | 0 | 0 | 1 | 197 | 41 | 72 | 14263 | 1717894 | 186034 | 1.96 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 118 | 224 | 52148 | 5615409 | 448766 | 6.13 |
