### 📊 Metrics — issue 236

Wall time for the issue: 3065 s, from the first event of the log to the mark that ended the run.
Steps done: 1 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/239.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 1 | 0 | 0 | 192 | 168 | 33 | 56 | 15440 | 1257160 | 166239 | 2.30 |
| green | 2 | 1 | 0 | 0 | 1972 | 146 | 31 | 56 | 14086 | 1498506 | 98914 | 1.51 |
| refactor | 2 | 1 | 0 | 0 | 370 | 50 | 12 | 24 | 4202 | 539899 | 76963 | 0.76 |
| pin | 2 | 2 | 0 | 0 | 415 | 115 | 14 | 28 | 2914 | 759864 | 40893 | 0.87 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 110 | 1.47 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 415 | 0.87 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's Draft PR step writes the run's `done` mark, carrying the opened PR's URL, before it renders the metrics report it commits — so a log holding exactly that one ended run renders a committed issue-<n>-metrics.md whose Outcome line names the landed PR | 6 | 3 | 0 | 0 | 0 | 270 | 58 | 106 | 23885 | 2640944 | 253275 | 3.11 | 2487 | unknown | unknown | unknown |
| A log with exactly one run that ended in a `done` mark renders a Wall time line that is a number, not unknown | 2 | 1 | 0 | 0 | 0 | 71 | 22 | 40 | 6167 | 983839 | 85708 | 1.02 | unknown | unknown | unknown | unknown |
| The report pasted into the PR body and into the closing `### ✅ Done` comment is the one rendered after `done` was written, and the committed file matches it | 2 | 1 | 0 | 0 | 0 | 138 | 10 | 18 | 6590 | 430646 | 44026 | 1.32 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 90 | 164 | 36642 | 4055429 | 383009 | 5.44 |
