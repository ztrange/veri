### 📊 Metrics — issue 1012

Wall time for the issue: 3103 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1034.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 963 | 11866 | 29714 | 0.13 |
| red | 4 | 1 | 0 | 0 | 537 | 173 | 33 | 64 | 15719 | 1619066 | 192275 | 2.02 |
| green | 2 | 1 | 0 | 0 | 370 | 38 | 13 | 24 | 3828 | 508568 | 78812 | 0.64 |
| refactor | 2 | 1 | 0 | 0 | 106 | 33 | 10 | 18 | 2866 | 354012 | 79189 | 0.60 |
| pin | 2 | 2 | 0 | 0 | 416 | 37 | 8 | 16 | 3077 | 298134 | 76515 | 0.40 |
| diff | 2 | 1 | 0 | 0 | 401 | 63 | 19 | 38 | 5654 | 841235 | 80248 | 0.73 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 1055 | 124 | 33 | 62 | 11711 | 1201753 | 260284 | 1.40 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 786 | 228 | 51 | 100 | 20396 | 2431128 | 276469 | 3.11 |

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
| A ref lock on the skill clone held by another process past today's 5 × VERI_FETCH_RETRY_SLEEP window (still locked after the fifth fetch) but released within the new bound lets run-conductor.sh's launch proceed, pinned offline with VERI_FETCH_RETRY_SLEEP=0 so no real-clock wait is taken ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 128 | 37 | 68 | 12338 | 1453375 | 244062 | 1.99 | 724 | unknown | 0/5 | nothing-left |  |  | full |
| A ref lock on the skill clone that is never released makes run-conductor.sh refuse with exit 2 once the new retry bound is reached, launching no conductor, with stderr naming the ref lock ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 14 | 28 | 7262 | 743824 | 99942 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |
| A fetch of origin that fails for any reason other than `cannot lock ref` is still refused at once by run-conductor.sh with exit 2 after a single fetch, without waiting for any retry ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 13 | 26 | 5890 | 582581 | 82787 | 0.73 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's *Launching the conductor* paragraph on the ref-lock retry states the new bound in place of "retried up to 5 times" ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 19 | 38 | 5654 | 841235 | 80248 | 0.73 | 419 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A ref lock on the skill clone held by another process past today's 5 × VERI_FETCH_RETRY_SLEEP window (still locked after the fifth fetch) but released within the new bound lets run-conductor.sh's launch proceed, pinned offline with VERI_FETCH_RETRY_SLEEP=0 so no real-clock wait is taken ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 106 | 0.60 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 50 | 51 | 51 | 0 | 52 | 65 | 67 | 107 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fast | 15 | 16 | 15 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 52 | 63 | 55 | 65 | 190 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 84 | 162 | 32107 | 3632881 | 536753 | 4.51 |
