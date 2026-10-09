### 📊 Metrics — issue 1221

Wall time for the issue: 2347 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1255.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 5 | 1 | 2 | 793 | 10759 | 31751 | 0.14 |
| diff | 2 | 1 | 0 | 0 | 1060 | 66 | 19 | 38 | 6479 | 975666 | 96861 | 0.91 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 521 | 20 | 6 | 12 | 2309 | 217177 | 74259 | 0.36 |
| developer | claude-opus-5-5 | 1 | 0 | 0 | 0 | 548 | 51 | 14 | 28 | 4963 | 769248 | 54353 | 0.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A new ADR docs/adr/0029 records that the scripts are Python 3 (standard library, floor 3.12) behind two-line /bin/sh shims keeping every entry point's name, arguments, stdout, stderr and exit codes; what #537's Rejected list rejected (Go, a permanent bash core, a long-lived Python process, and the rest); and the shim survival rule — a .sh entry point stays because SKILL.md, the Makefile and the hooks call it by name, and holds no logic and no Python source — linking #537, #473, #474 and ADR 0027 for the test-deletion rule without restating it ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 19 | 38 | 6479 | 975666 | 96861 | 0.91 | 1093 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| fast | 25 | 27 |
| affected | 466 | 467 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 20 | 40 | 7272 | 986425 | 128612 | 1.05 |
