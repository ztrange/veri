### 📊 Metrics — issue 533

Wall time for the issue: 0 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 529 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/560.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 0 | 11 | 2 | 4 | 1320 | 21744 | 53682 | 0.23 |
| red | 1 | 0 | 0 | 0 | 0 | 29 | 9 | 16 | 3900 | 342171 | 40159 | 0.27 |
| pin | 1 | 1 | 0 | 0 | 0 | 13 | 5 | 10 | 1509 | 165168 | 43959 | 0.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| commentary-figures.test.sh fails, naming the script, the chunk's range and the script's line count, when a chunk in docs/wt/commentary.py claims a line past the end of its script (compared as text, no page build) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 14 | 26 | 5409 | 507339 | 84118 | 0.49 | 0 | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 0 | 1 |
| target | 0 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 16 | 30 | 6729 | 529083 | 137800 | 0.72 |
