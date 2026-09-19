### 📊 Metrics — issue 339

Wall time for the issue: 7929 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: unknown of 7 planned.
Outcome: the run bailed — killed-stuck, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 1 | 0 | 0 | 64 | 55 | 8 | 16 | 5188 | 302381 | 76004 | 1.04 |
| green | 1 | 0 | 0 | 1 | 6307 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 64 | 1.04 |
| green | 0 | 0.00 | 6307 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| push-branch.sh's logic runs from functions with a `main` entry, and the only top-level code executed when the file is run directly is `[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"`; sourcing it runs nothing ⟦criterion 2⟧ | 3 | 1 | 0 | 1 | 1 | 0 | 55 | 8 | 16 | 5188 | 302381 | 76004 | 1.04 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 8 | 16 | 5188 | 302381 | 76004 | 1.04 |
