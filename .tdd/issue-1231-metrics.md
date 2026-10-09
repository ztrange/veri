### 📊 Metrics — issue 1231

Wall time for the issue: 1615 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1232.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 6 | 1 | 2 | 804 | 12385 | 29888 | 0.13 |
| diff | 2 | 1 | 0 | 0 | 325 | 130 | 18 | 36 | 12488 | 865619 | 91988 | 0.97 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 106 | 30 | 9 | 18 | 3351 | 360222 | 69952 | 0.39 |
| developer | claude-opus-5-5 | 1 | 0 | 0 | 0 | 231 | 106 | 10 | 20 | 9941 | 517782 | 51924 | 0.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| orchestrate.test.sh's "#1126 a conductor orchestrate.sh stops over VERI_CONDUCTOR_CTX_BUDGET is stopped by SIGTERM to its process group" case records the writer's own exit status, 143, whatever order the writer's death, the conductor's TERM trap and its wait on the writer happen in — no second wait on an already-reaped writer (CI run 37879617536 recorded `writer -1`), and no window where the writer can see a closed stdout before its SIGTERM lands; the case and orchestrate.test.sh stay green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 130 | 18 | 36 | 12488 | 865619 | 91988 | 0.97 | 355 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| fast | 28 | 29 |
| affected | 7 | 7 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 19 | 38 | 13292 | 878004 | 121876 | 1.10 |
