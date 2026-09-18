### 📊 Metrics — issue 280

Wall time for the issue: 1182 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/304.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 0 | 0 | 0 | 95 | 57 | 13 | 24 | 6103 | 497802 | 82396 | 1.23 |
| pin | 2 | 2 | 0 | 0 | 1016 | 128 | 39 | 76 | 6957 | 2211964 | 87577 | 0.87 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| status.sh --json reports bail_phase from the bail event's own phase, not the last launch's phase, when the two differ | 2 | 1 | 0 | 0 | 0 | 0 | 88 | 24 | 48 | 5980 | 1283835 | 84541 | 1.04 | unknown | unknown | unknown | unknown |
| status.sh renders the solvable count as ? (text `solvable ?`, JSON `"solvable": "?"`) when solvable-issues.sh exits other than 0 or 3 | 2 | 1 | 0 | 0 | 0 | 0 | 97 | 28 | 52 | 7080 | 1425931 | 85432 | 1.06 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 52 | 100 | 13060 | 2709766 | 169973 | 2.10 |
