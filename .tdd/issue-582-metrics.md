### 📊 Metrics — issue 582

Wall time for the issue: 3777 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/587.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 1 | 2 | 732 | 11731 | 26522 | 0.12 |
| red | 4 | 2 | 0 | 0 | 241 | 90 | 25 | 48 | 10581 | 980859 | 156265 | 0.93 |
| green | 6 | 2 | 1 | 0 | 2455 | 157 | 54 | 108 | 16070 | 2303530 | 198366 | 1.42 |
| refactor | 4 | 2 | 0 | 0 | 170 | 46 | 17 | 32 | 4773 | 570039 | 136884 | 0.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1489 | 0.92 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `make test` gives every suite a GIT_EXEC_PATH equal to what the resolved real git reports for `--exec-path` when run at its own path, not the path the symlink derives ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 36 | 70 | 12173 | 1390082 | 218250 | 1.27 | 1195 | unknown | 0/5 | nothing-structural |  |  | full |
| `make test` gives every suite a GIT_TEMPLATE_DIR naming the templates directory beside the resolved real git (`../share/git-core/templates`) when that directory exists, and leaves it unset when it does not (the Linux path) ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 183 | 60 | 118 | 19251 | 2464346 | 273265 | 1.78 | 1804 | 1/2 | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `make test` gives every suite a GIT_EXEC_PATH equal to what the resolved real git reports for `--exec-path` when run at its own path, not the path the symlink derives ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 57 | 0.33 |
| `make test` gives every suite a GIT_TEMPLATE_DIR naming the templates directory beside the resolved real git (`../share/git-core/templates`) when that directory exists, and leaves it unset when it does not (the Linux path) ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 113 | 0.38 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 39 | 1 | 27 | 79 | 32 | 73 | 0 | 28 | 0 | 37 | 0 | 38 | 89 | 85 | 48 | 39 | 38 |
| fast | 6 | 6 | 5 | 6 | 6 | 5 | 5 |  |  |  |  |  |  |  |  |  |  |
| target | 27 | 38 | 38 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 462 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 190 | 32156 | 3866159 | 518037 | 3.17 |
