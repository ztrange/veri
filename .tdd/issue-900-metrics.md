### 📊 Metrics — issue 900

Wall time for the issue: 1996 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/902.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 835 | 11866 | 29475 | 0.13 |
| red | 3 | 1 | 0 | 0 | 247 | 111 | 23 | 46 | 9719 | 1069938 | 126612 | 1.26 |
| green | 2 | 1 | 0 | 0 | 288 | 52 | 14 | 28 | 4335 | 598367 | 77181 | 0.65 |
| refactor | 2 | 1 | 0 | 0 | 79 | 26 | 9 | 16 | 2483 | 302232 | 76259 | 0.55 |
| pin | 1 | 1 | 0 | 0 | 82 | 10 | 4 | 8 | 1107 | 148528 | 37118 | 0.19 |
| diff | 2 | 1 | 0 | 0 | 101 | 33 | 11 | 22 | 2990 | 450092 | 77500 | 0.61 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 436 | 85 | 26 | 50 | 8634 | 950462 | 216623 | 1.14 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 370 | 154 | 36 | 72 | 12835 | 1630561 | 207522 | 2.24 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| run-conductor.sh waits between ref-lock fetch retries for the interval VERI_FETCH_RETRY_SLEEP names, so a run with VERI_FETCH_RETRY_SLEEP=0 retries a locked fetch without waiting on the real clock ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 143 | 36 | 70 | 12128 | 1487440 | 236053 | 1.92 | 574 | unknown | 0/5 | nothing-left |  |  | full |
| with VERI_FETCH_RETRY_SLEEP unset, run-conductor.sh still waits 1 s between ref-lock fetch retries, pinned by a case that records the interval each wait was given ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 14 | 28 | 5516 | 631625 | 81117 | 0.73 | unknown | unknown | unknown | unknown |  |  | pin |
| cases 31 and 32 of tests/run-conductor.test.sh exercise the ref-lock retry path with no real sleep, and their assertions are unchanged ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 11 | 22 | 2990 | 450092 | 77500 | 0.61 | 123 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| run-conductor.sh waits between ref-lock fetch retries for the interval VERI_FETCH_RETRY_SLEEP names, so a run with VERI_FETCH_RETRY_SLEEP=0 retries a locked fetch without waiting on the real clock ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 79 | 0.55 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 30 | 29 | 33 | 34 | 1 | 37 | 0 | 0 | 35 | 36 | 32 |
| fast | 14 | 14 | 15 |  |  |  |  |  |  |  |  |
| target | 33 | 37 | 33 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 62 | 122 | 21469 | 2581023 | 424145 | 3.39 |
