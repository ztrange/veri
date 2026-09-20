### 📊 Metrics — issue 255

Wall time for the issue: 4750 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/371.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 14 | 6 | 0 | 0 | 1305 | 1143 | 196 | 354 | 94745 | 10023570 | 697130 | 13.39 |
| green | 11 | 5 | 0 | 0 | 5622 | 581 | 143 | 262 | 46017 | 6985638 | 474086 | 8.34 |
| refactor | 10 | 5 | 0 | 0 | 3371 | 752 | 130 | 252 | 54358 | 7134545 | 430661 | 8.79 |
| pin | 2 | 2 | 0 | 0 | 163 | 124 | 23 | 40 | 7125 | 966195 | 89710 | 1.56 |

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
| The renderer, fed a captured leaf log fixture, prints assistant text, each tool call's name and first input line, and a truncated tool result, one per line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 1 | 0 | 317 | 49 | 98 | 23175 | 2453804 | 196698 | 2.77 | 9007 | unknown | 1/5 | nothing-structural |
| The renderer exits 2 on a line that is not JSON ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 128 | 40 | 80 | 9600 | 1807117 | 204363 | 2.06 | 3112 | unknown | 0/5 | nothing-left |
| The Tests endpoint lists the selected run's leaf test runs — command, pass/fail from the tool result's exit status, output tail — extracted from fixture leaf logs ⟦criterion 2⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 776 | 138 | 250 | 60951 | 7539938 | 445532 | 9.43 | 156593 | unknown | 3/5 | structural-owed |
| The Tests endpoint never executes a suite: a test command whose execution would leave a trace leaves none when the endpoint is queried ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 201 | 34 | 66 | 12530 | 1754679 | 102100 | 2.21 | unknown | unknown | unknown | unknown |
| The Chatter endpoint returns the rendered log of the leaf the selected run is currently on ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 486 | 102 | 182 | 38604 | 5292864 | 335053 | 6.96 | 1193 | unknown | 3/5 | structural-owed |
| A fixture run whose current leaf changes switches the Chatter endpoint to the new leaf ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 189 | 33 | 56 | 16197 | 1683210 | 115735 | 2.40 | unknown | unknown | unknown | unknown |
| The served page has Tests and Chatter panes, each scheduling its next request only from the settlement of its previous one, like the existing panes | 6 | 3 | 0 | 0 | 0 | 0 | 503 | 96 | 176 | 41188 | 4578336 | 292106 | 6.24 | 1384 | unknown | 2/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 5 | 5 | 172 | 172 | 5 | 5 | 4 | 5 | 172 | 6 | 5 | 6 | 171 | 172 | 6 | 6 | 6 | 5 | 171 | 6 | 6 | 6 | 173 | 173 | 6 | 6 | 6 | 6 | 172 |
| fast | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 6 | 6 | 6 | 6 | 7 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 492 | 908 | 202245 | 25109948 | 1691587 | 32.08 |
