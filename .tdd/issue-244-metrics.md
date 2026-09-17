### 📊 Metrics — issue 244

Wall time for the issue: 3500 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/268.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 2 | 0 | 0 | 224 | 153 | 34 | 68 | 14529 | 1531848 | 189457 | 2.39 |
| green | 4 | 2 | 0 | 0 | 1946 | 167 | 41 | 80 | 10080 | 1957432 | 145019 | 1.61 |
| refactor | 4 | 2 | 0 | 0 | 1030 | 147 | 30 | 60 | 11496 | 1464822 | 154608 | 1.61 |
| pin | 1 | 1 | 0 | 0 | 102 | 80 | 21 | 40 | 6981 | 1198279 | 49425 | 0.51 |

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
| solvable-issues.sh asks gh for every open issue, not gh's default page of 30: an opted-in, unblocked issue older than the newest 30 is printed | 6 | 3 | 0 | 0 | 0 | 0 | 233 | 54 | 108 | 15794 | 2626581 | 229175 | 2.58 | 1669 | unknown | 0/5 | nothing-left |
| An issue blocked by an open issue that is older than the newest 30 is not printed | 2 | 1 | 0 | 0 | 0 | 0 | 111 | 27 | 52 | 10176 | 1449462 | 90224 | 1.13 | unknown | unknown | unknown | unknown |
| solvable-issues.sh asks gh for every open pull request, not gh's default page of 30: an open PR past the first 30 saying Closes #<n> still claims its issue | 6 | 3 | 0 | 0 | 0 | 0 | 203 | 45 | 88 | 17116 | 2076338 | 219110 | 2.41 | 1623 | unknown | 2/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 126 | 248 | 43086 | 6152381 | 538509 | 6.12 |
