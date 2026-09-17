### 📊 Metrics — issue 267

Wall time for the issue: 15731 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/286.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 2 | 0 | 0 | 1527 | 415 | 58 | 114 | 32605 | 3060436 | 227838 | 3.38 |
| green | 6 | 2 | 1 | 0 | 4140 | 296 | 59 | 116 | 19415 | 3015771 | 203817 | 3.05 |
| refactor | 6 | 2 | 1 | 0 | 2587 | 298 | 59 | 108 | 23236 | 2859671 | 243886 | 2.60 |
| pin | 1 | 1 | 0 | 0 | 83 | 71 | 14 | 26 | 5578 | 794479 | 47998 | 0.41 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2539 | 2.10 | 0 | 0.00 |
| refactor | 1629 | 1.92 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| skill-metrics.test.sh no longer compares commit_line against pr_line at record level (the `commit_line -gt pr_line` check is gone), and the "lands BEFORE the PR is opened" comment that justified it is removed or corrected ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 349 | 71 | 142 | 23777 | 3672034 | 276167 | 3.73 | 4788 | 1/2 | 0/5 | nothing-left |
| skill-metrics.test.sh no longer asks the record-level presence probe first_record_line "$pr_records" 'gh pr create' '📊 metrics', and any comment describing it is corrected ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 1 | 0 | 458 | 91 | 168 | 35768 | 4462846 | 335386 | 3.86 | 6311 | 1/2 | 0/5 | nothing-left |
| the #266 line-level Draft PR checks in skill-metrics.test.sh still fail when SKILL.md's Draft PR command order is broken (gh pr create after the metrics: commit, or gh pr edit before it / without the 📊 block) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 273 | 28 | 54 | 21289 | 1595477 | 111986 | 1.85 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 190 | 364 | 80834 | 9730357 | 723539 | 9.43 |
