### 📊 Metrics — issue 339

Wall time for the issue: 8707 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/367.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 14 | 6 | 0 | 0 | 519 | 433 | 78 | 154 | 41283 | 3307668 | 571863 | 8.41 |
| green | 13 | 5 | 1 | 1 | 10318 | 293 | 80 | 152 | 26904 | 3114467 | 449704 | 6.73 |
| refactor | 10 | 5 | 0 | 0 | 1491 | 174 | 48 | 96 | 16309 | 1870468 | 370815 | 5.05 |
| pin | 2 | 2 | 0 | 0 | 126 | 47 | 13 | 24 | 4599 | 477268 | 75767 | 1.11 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 7783 | 2.34 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| push-branch.sh's logic runs from functions with a `main` entry, and the only top-level code executed when the file is run directly is `[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"`; sourcing it runs nothing ⟦criterion 2⟧ | 11 | 4 | 1 | 1 | 1 | 0 | 253 | 52 | 102 | 23459 | 2043915 | 381317 | 5.42 | 3233 | 1/2 | 1/5 | nothing-structural |
| push-branch.sh's existing integration suite tests/push-branch.test.sh passes unmodified against the refactored script — same stdout, stderr and exit codes for every existing case ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 16 | 30 | 7879 | 692352 | 86952 | 1.41 | unknown | unknown | unknown | unknown |
| A new skills/tdd/scripts/tests/unit/push-branch.test.sh sources push-branch.sh (never execs it) and mocks git, sleep and the event recording as same-named shell functions, and passes with PATH set to a directory containing none of those binaries ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 168 | 35 | 70 | 15963 | 1451752 | 236874 | 3.49 | 1089 | unknown | 1/5 | nothing-structural |
| The new unit suite's header comment records push-branch.sh as the chosen script and the reasoning as a process-count proxy, not measured seconds ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 120 | 31 | 58 | 11091 | 1117833 | 218151 | 3.02 | 986 | unknown | 0/5 | nothing-left |
| Both the new unit suite and the untouched integration suite pass under `make test`, and the unit suite alone passes under `make unit` ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 17 | 32 | 7538 | 752315 | 93797 | 1.50 | unknown | unknown | unknown | unknown |
| CLAUDE.md's "Testing idiom" section documents the pattern (main guard, source, mock-as-function, unchanged CLI contract) naming push-branch.sh as the worked example, in wording a guard suite pins ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 123 | 36 | 70 | 11500 | 1420525 | 226700 | 3.27 | 811 | unknown | 1/5 | nothing-structural |
| claude-md-counts.test.sh's suite-count assertions include the new unit suite file and still pass ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 1 | 0 | 124 | 32 | 64 | 11665 | 1291179 | 224358 | 3.18 | 2241 | unknown | 2/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 219 | 426 | 89095 | 8769871 | 1468149 | 21.30 |
