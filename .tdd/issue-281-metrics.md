### 📊 Metrics — issue 281

Wall time for the issue: 11475 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/307.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 2471 | 384 | 58 | 108 | 36876 | 3199609 | 214794 | 3.01 |
| green | 4 | 2 | 0 | 0 | 6575 | 206 | 44 | 84 | 12894 | 2166653 | 141561 | 2.76 |
| refactor | 4 | 2 | 0 | 0 | 1706 | 197 | 43 | 86 | 13591 | 2187150 | 167312 | 2.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| a shared sourced helper defines main_working_tree once, and status.sh and solvable-issues.sh both resolve the main working tree through it (first `worktree <path>` line of git's registry, even when called from a linked worktree) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 458 | 78 | 150 | 36068 | 4242163 | 251134 | 4.10 | 6816 | unknown | 1/5 | nothing-structural |
| run_activity and scope_totals read the event log through one shared per-line parse and one shared dollar/token sum, with status.sh's text and --json figures unchanged over a fixture log that has blank lines and usage events ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 329 | 67 | 128 | 27293 | 3311249 | 272533 | 3.67 | 4640 | unknown | 2/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 145 | 278 | 63361 | 7553412 | 523667 | 7.77 |
