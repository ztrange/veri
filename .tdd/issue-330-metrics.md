### 📊 Metrics — issue 330

Wall time for the issue: 3003 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/346.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 10 | 2 | 0 | 0 | 711 | 557 | 92 | 174 | 55603 | 4569942 | 525711 | 8.93 |
| green | 4 | 2 | 0 | 0 | 833 | 157 | 32 | 64 | 16256 | 1590288 | 191613 | 3.12 |
| refactor | 4 | 2 | 0 | 0 | 680 | 162 | 35 | 66 | 17166 | 1857429 | 198395 | 3.34 |
| pin | 6 | 6 | 0 | 0 | 569 | 126 | 36 | 72 | 12187 | 1468811 | 226284 | 3.30 |

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
| The dashboard's python server lives in a module file beside dashboard.sh that dashboard.sh execs; importing it and calling runs_json, metrics_json or events_json never binds a port — a case imports it, calls a function, then confirms the default port 8765 is still free ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 40 | 76 | 18814 | 1726228 | 250590 | 3.84 | 966 | unknown | 2/5 | nothing-structural |
| /api/runs's payload is asserted by calling runs_json directly against a fixture repo, byte-identical to status.sh --json on the same fixture, with no HTTP request and no server process for that case ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 82 | 17 | 34 | 8392 | 838331 | 91998 | 1.55 | unknown | unknown | unknown | unknown |
| /api/metrics's payload is asserted by calling metrics_json directly — recomputed live for a running run, and the committed .tdd/issue-<n>-metrics.md verbatim for a finished one — with no server for that case ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 14 | 26 | 7930 | 593716 | 87923 | 1.37 | unknown | unknown | unknown | unknown |
| /api/events's payload is asserted by calling events_json directly, including the empty list for an issue no run holds a ledger for, with no server for that case ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 14 | 28 | 7075 | 634903 | 85614 | 1.35 | unknown | unknown | unknown | unknown |
| The static-HTML polling contract (the page polls all 3 endpoints every 2 s) is asserted by reading dashboard.html directly off disk, with no server started for that case ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 13 | 26 | 5864 | 583187 | 85094 | 1.29 | unknown | unknown | unknown | unknown |
| At most 2 dashboard.sh server processes are started across the whole dashboard suite, counted deterministically by a PATH-first counting shim or a bind marker file, never by wall clock ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 303 | 56 | 108 | 31985 | 3023233 | 321776 | 5.53 | 902 | unknown | 3/5 | structural-owed |
| The remaining server-dependent cases together assert: default port 8765 with no argument; an explicit port argument bound instead; loopback only, unreachable from a non-loopback attempt; clean exit 0 on SIGINT; one server process answering more than one request across its life ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 124 | 18 | 36 | 11936 | 915196 | 101346 | 1.77 | unknown | unknown | unknown | unknown |
| Every assertion dashboard.test.sh made before this issue is still made by some case afterwards, and make test is green ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 97 | 23 | 42 | 9216 | 1171676 | 117662 | 1.99 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 195 | 376 | 101212 | 9486470 | 1142003 | 18.70 |
