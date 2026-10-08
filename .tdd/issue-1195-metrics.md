### 📊 Metrics — issue 1195

Wall time for the issue: 1361 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1206.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 731 | 10759 | 31564 | 0.14 |
| diff | 2 | 1 | 0 | 0 | 109 | 35 | 11 | 22 | 3248 | 444273 | 73292 | 0.58 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 60 | 19 | 6 | 12 | 2196 | 208250 | 67670 | 0.33 |
| developer | claude-opus-5-5 | 1 | 0 | 0 | 0 | 58 | 22 | 6 | 12 | 1783 | 246782 | 37186 | 0.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In orchestrate.test.sh, the stub run-conductor.sh of both the launch-state case ("launches run-conductor.sh <issue> as the leader of its own session…") and the #1126 SIGPIPE/SIGXFSZ case redirects its own stderr away (e.g. `exec 2>/dev/null`) right after it echoes `conductor <n> on stderr`, so its bash can no longer add a `Terminated` job-report line to the stderr those cases assert on, while each case's expected output still contains `conductor <n> on stderr` read from orchestrate's stderr; no other line of the suite and no file outside it changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 22 | 3248 | 444273 | 73292 | 0.58 | 132 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s |
| --- | ---: |
| fast | 24 |
| affected | 8 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 12 | 24 | 3979 | 455032 | 104856 | 0.72 |
