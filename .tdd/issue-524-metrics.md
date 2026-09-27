### 📊 Metrics — issue 524

Wall time for the issue: 3238 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/525.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 13 | 3 | 6 | 1283 | 102675 | 39961 | 0.37 |
| red | 6 | 2 | 0 | 0 | 472 | 341 | 67 | 128 | 32783 | 3791293 | 344911 | 4.17 |
| green | 8 | 2 | 2 | 0 | 1702 | 374 | 74 | 146 | 34545 | 3762294 | 321365 | 4.01 |
| refactor | 4 | 2 | 0 | 0 | 167 | 112 | 27 | 54 | 11008 | 1221780 | 173984 | 1.86 |
| pin | 2 | 2 | 0 | 0 | 127 | 47 | 12 | 22 | 4427 | 451103 | 77390 | 0.80 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1702 | 4.01 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| no-sigpipe-pipelines.test.sh also audits the Makefile's recipe lines, reporting a recipe line that ends a pipeline in a reader leaving before EOF (a grep whose options carry q, or a head) as Makefile:<line> — shown on a planted offending recipe; the recipe shell declares no pipefail, so the Makefile is audited without that condition ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 371 | 70 | 138 | 34356 | 3651257 | 376062 | 4.43 | 1261 | 1/2 | 0/5 | nothing-left |  |  |
| The make test / make unit recipe's count-line check reads the suite's last line to EOF (grep -E … > /dev/null, or feeding the reader by redirection rather than a pipe; never trap '' PIPE, never dropping pipefail), so the audit over the real Makefile names no site ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 110 | 21 | 40 | 10673 | 1196504 | 103498 | 1.28 | unknown | unknown | unknown | unknown |  |  |
| A suite whose last output line is not a count line is still failed by make test, named `<suite>: never reached its count line`, exactly as before the repair ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 82 | 19 | 36 | 7836 | 956370 | 101017 | 1.16 | unknown | unknown | unknown | unknown |  |  |
| A Makefile recipe site where leaving before EOF is deliberate is exempted by an entry in the audit's exemption table keyed Makefile:<line> carrying a reason, and an exemption entry with no reason still fails the run ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 311 | 70 | 136 | 29898 | 3422339 | 337073 | 3.98 | 1074 | 1/2 | 2/5 | nothing-structural |  |  |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 0 | 0 | 60 | 0 | 61 | 49 | 6 | 1 | 6 | 6 | 29 | 2 | 2 | 7 | 1 | 61 | 8 | 2 | 6 | 2 | 5 | 0 | 2 |
| fast | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 0 | 2 | 6 | 6 | 29 | 29 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 440 | 436 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 183 | 356 | 84046 | 9329145 | 957611 | 11.21 |
