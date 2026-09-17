### 📊 Metrics — issue 248

Wall time for the issue: 2218 s, from the first event of the log to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/260.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 3 | 1 | 0 | 0 | 536 | 94 | 23 | 46 | 7297 | 1001769 | 104948 | 1.31 |
| green | 2 | 1 | 0 | 0 | 874 | 55 | 17 | 34 | 3686 | 741726 | 66225 | 0.74 |
| refactor | 2 | 1 | 0 | 0 | 634 | 49 | 13 | 26 | 4215 | 602248 | 67404 | 0.66 |
| pin | 1 | 1 | 0 | 0 | 53 | 40 | 17 | 28 | 3677 | 750492 | 37335 | 0.34 |

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
| On a resumed run (a log carrying a `resume` mark), the metrics report's issue-wall sentence says the wall starts at the last `resume` and no longer claims "from the first event of the log", pinned by a test in `metrics.test.sh` on the sentence's wording, not just the seconds figure | 6 | 3 | 0 | 0 | 0 | 0 | 170 | 46 | 92 | 12581 | 2084012 | 205868 | 2.18 | 2090 | unknown | 0/5 | nothing-left |
| On a run with no `resume` mark, the metrics report's issue-wall sentence describes the start as the log's first event, pinned by a test in `metrics.test.sh` on the sentence's wording | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 24 | 42 | 6294 | 1012223 | 70044 | 0.87 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 70 | 134 | 18875 | 3096235 | 275912 | 3.04 |
