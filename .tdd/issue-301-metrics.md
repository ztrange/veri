### 📊 Metrics — issue 301

Wall time for the issue: 9182 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/308.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 9 | 3 | 0 | 0 | 2201 | 593 | 73 | 136 | 55354 | 3574332 | 454426 | 5.71 |
| green | 6 | 3 | 0 | 0 | 5874 | 417 | 78 | 146 | 28677 | 4332886 | 249505 | 4.84 |
| refactor | 8 | 3 | 0 | 0 | 3839 | 347 | 47 | 92 | 16023 | 2244843 | 210694 | 3.89 |
| pin | 2 | 2 | 0 | 0 | 308 | 190 | 25 | 50 | 13955 | 1424896 | 91886 | 0.80 |

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
| `make test` runs every suite under the offline shim with a per-suite reach log, so a suite that runs `git fetch` against a remote URL, `gh` or `curl` fails `make test`, naming the suite and what it tried ⟦criterion 3⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 440 | 51 | 100 | 17002 | 2621568 | 224011 | 5.21 | 5840 | unknown | 1/5 | nothing-structural |
| A suite that fetches this checkout's own origin still fails `make test`, named — the own-origin guarantee holds from the recipe's single run, not from a re-run ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 166 | 23 | 44 | 11915 | 1177716 | 97743 | 1.27 | unknown | unknown | unknown | unknown |
| No suite is run more than once by a single `make test` for the offline check: hermetic-suites.test.sh re-runs no suite for the offline or own-origin cases ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 486 | 83 | 156 | 41161 | 4605711 | 314566 | 4.35 | 4226 | unknown | 2/5 | nothing-structural |
| The ambient-`VERI_*` and conductor-lock cases still hold: a suite whose result changes with an ambient `VERI_*` value or a live conductor lock still fails, named ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 147 | 19 | 36 | 14723 | 970638 | 101053 | 1.28 | unknown | unknown | unknown | unknown |
| hermetic-suites.test.sh runs solvable-issues.test.sh's reference (no-lock, cleared) arm once, shared by its ambient and lock cases, instead of once per case ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 308 | 47 | 88 | 29208 | 2201324 | 269138 | 3.13 | 2814 | unknown | 3/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 223 | 424 | 114009 | 11576957 | 1006511 | 15.24 |
