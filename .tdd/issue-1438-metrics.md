### 📊 Metrics — issue 1438

Wall time for the issue: 2036 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1453.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 3 | 6 | 998 | 107202 | 38535 | 0.17 |
| red | 3 | 1 | 0 | 0 | 116 | 95 | 24 | 46 | 9525 | 1160578 | 141148 | 1.36 |
| green | 4 | 1 | 1 | 0 | 463 | 153 | 40 | 80 | 12930 | 2001120 | 145752 | 1.52 |
| refactor | 2 | 1 | 0 | 0 | 356 | 33 | 6 | 14 | 1554 | 270009 | 42665 | 0.62 |
| pin | 1 | 1 | 0 | 0 | 20 | 12 | 4 | 8 | 1592 | 159289 | 40013 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 577 | 84 | 25 | 52 | 7727 | 1095723 | 171110 | 1.07 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 389 | 218 | 52 | 102 | 18872 | 2602475 | 237003 | 2.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 463 | 1.52 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With no user.name/user.email in any git config, preserve-attempt.sh still writes the snapshot ref under refs/veri/attempts/<issue>/<step>/<phase>-<attempt> and exits 0 ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 244 | 60 | 122 | 20154 | 2942325 | 276790 | 2.90 | 1000 | 1/2 | 0/5 | nothing-left |  |  | full |
| With no user.name/user.email in any git config, preserve-attempt.sh given a mark still copies .tdd/<phase>.log and .tdd/<phase>.out under .tdd/attempts/ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 14 | 26 | 5447 | 648671 | 92788 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With no user.name/user.email in any git config, preserve-attempt.sh still writes the snapshot ref under refs/veri/attempts/<issue>/<step>/<phase>-<attempt> and exits 0 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 356 | 0.62 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 4 | 4 | 3 | 298 | 3 |
| fast | 25 | 25 | 26 | 25 | 25 | 23 |  |
| target | 3 | 3 | 3 | 2 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 77 | 154 | 26599 | 3698198 | 408113 | 3.87 |
