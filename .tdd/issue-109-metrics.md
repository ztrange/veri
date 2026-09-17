### 📊 Metrics — issue 109

Wall time for the issue: 21824 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/277.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 20 | 10 | 0 | 0 | 3768 | 766 | 173 | 324 | 65706 | 7856990 | 789150 | 8.87 |
| green | 20 | 10 | 0 | 0 | 11450 | 570 | 149 | 286 | 45241 | 6708566 | 710907 | 8.04 |
| refactor | 22 | 10 | 0 | 0 | 6034 | 1079 | 236 | 462 | 77228 | 12307883 | 877879 | 10.41 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| status.sh run from a repo with no `.tdd/wt/*` runs under its main working tree prints "no runs" and exits 3 | 6 | 3 | 0 | 0 | 0 | 0 | 276 | 76 | 140 | 23625 | 3757964 | 232616 | 2.82 | 2574 | unknown | 0/5 | structural-owed |
| status.sh lists every run under `.tdd/wt/*` with its issue number and title from the ledger heading, its branch, and step n of m from the ledger | 7 | 3 | 0 | 0 | 0 | 1 | 261 | 60 | 114 | 19194 | 2734261 | 258228 | 2.70 | 1736 | unknown | 2/5 | nothing-structural |
| status.sh shows each run's current phase, actor, current leaf name and elapsed seconds, and the attempts so far in the current step, read from its event log | 6 | 3 | 0 | 0 | 0 | 0 | 283 | 52 | 98 | 17438 | 2407864 | 185687 | 2.66 | 2301 | unknown | 1/5 | nothing-structural |
| status.sh shows each run's cost so far in dollars and tokens, summed from its event log | 6 | 3 | 0 | 0 | 0 | 0 | 203 | 55 | 104 | 16882 | 2562530 | 239349 | 2.72 | 1532 | unknown | 3/5 | structural-owed |
| status.sh shows each run's state: running, done with its PR url, bailed with phase and classification, or stale when no event is newer than `VERI_TIMEOUT` and its conductor.pid does not answer `kill -0` | 6 | 3 | 0 | 0 | 0 | 0 | 209 | 40 | 72 | 14272 | 1699495 | 195887 | 2.60 | 1936 | unknown | 2/5 | nothing-structural |
| status.sh --scope <name> (or VERI_LABEL when no --scope) adds scope totals: issues attempted, done, bailed, total wall time and dollars | 7 | 3 | 0 | 0 | 0 | 1 | 353 | 75 | 146 | 30184 | 3964179 | 313284 | 3.42 | 2258 | unknown | 2/5 | structural-owed |
| status.sh with no --scope but VERI_LABEL set adds the same scope totals line for the scope VERI_LABEL names | 6 | 3 | 0 | 0 | 0 | 0 | 129 | 41 | 82 | 10791 | 1841136 | 212486 | 2.19 | 2018 | unknown | 1/5 | nothing-structural |
| status.sh scope totals include the count still solvable, from solvable-issues.sh for that scope, tested with VERI_GH_JSON fixtures and no network | 6 | 3 | 0 | 0 | 0 | 0 | 192 | 49 | 96 | 15611 | 2384581 | 250881 | 2.66 | 2350 | unknown | 2/5 | nothing-structural |
| status.sh --json emits the same per-run and scope data as one JSON document | 6 | 3 | 0 | 0 | 0 | 0 | 264 | 55 | 110 | 20682 | 2764500 | 249405 | 2.83 | 2720 | unknown | 2/5 | structural-owed |
| status.sh --watch [seconds] redraws in place, recomputing everything from disk on every render | 6 | 3 | 0 | 0 | 0 | 0 | 245 | 55 | 110 | 19496 | 2756929 | 240113 | 2.72 | 2369 | unknown | 1/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 558 | 1072 | 188175 | 26873439 | 2377936 | 27.32 |
