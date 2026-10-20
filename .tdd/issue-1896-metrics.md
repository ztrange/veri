### 📊 Metrics — issue 1896

Wall time for the issue: 1562 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1913.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 2 | 4 | 639 | 47225 | 13360 | 0.04 |
| red | 7 | 3 | 0 | 0 | 185 | 157 | 42 | 78 | 16106 | 1210565 | 134859 | 0.62 |
| green | 4 | 1 | 0 | 0 | 143 | 99 | 31 | 56 | 10105 | 859544 | 62336 | 0.45 |
| refactor | 2 | 1 | 0 | 0 | 63 | 51 | 11 | 20 | 3367 | 284013 | 30428 | 0.14 |
| pin | 2 | 2 | 0 | 0 | 41 | 31 | 7 | 14 | 2255 | 181106 | 26943 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 173 | 129 | 32 | 60 | 9275 | 799881 | 116776 | 0.46 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 162 | 142 | 37 | 70 | 15213 | 1128445 | 105389 | 0.53 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 108 | 76 | 24 | 42 | 7984 | 654127 | 45761 | 0.37 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| While the PR's head differs from the given head-sha, wait-ci.sh records no .tdd/ci-deadline-<head-sha> file and does not exit 2 for that sha: the call ends its slice with exit 3 ⟦criterion 1⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 240 | 68 | 122 | 21879 | 1823133 | 183706 | 0.97 | 549 | 1/2 | 1/5 | nothing-left |  |  | full |
| The first wait-ci.sh call that sees the PR's head equal to the given head-sha records .tdd/ci-deadline-<head-sha>, counted from that call's moment, and a later call inherits that recorded deadline ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 14 | 28 | 6004 | 448435 | 37293 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| With no head-sha given, wait-ci.sh still records .tdd/ci-deadline-<head> on the first pending call for the PR's current head ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 9 | 18 | 3950 | 263660 | 33567 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| While the PR's head differs from the given head-sha, wait-ci.sh records no .tdd/ci-deadline-<head-sha> file and does not exit 2 for that sha: the call ends its slice with exit 3 ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 63 | 0.14 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| fast | 6 | 6 | 6 | 5 | 6 |  |  |  |  |  |  |  |
| target | 1 | 1 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 93 | 172 | 32472 | 2582453 | 267926 | 1.36 |
