### 📊 Metrics — issue 1128

Wall time for the issue: 2345 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1172.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1133 | 12385 | 31215 | 0.14 |
| red | 5 | 1 | 0 | 0 | 181 | 160 | 38 | 72 | 15434 | 1916236 | 266335 | 2.66 |
| green | 2 | 1 | 0 | 0 | 132 | 59 | 15 | 30 | 5808 | 759852 | 96993 | 0.87 |
| refactor | 2 | 1 | 0 | 0 | 74 | 39 | 12 | 22 | 3085 | 468308 | 80454 | 0.62 |
| pin | 3 | 3 | 0 | 0 | 891 | 133 | 40 | 80 | 15594 | 2123823 | 150920 | 1.18 |
| diff | 2 | 1 | 0 | 0 | 88 | 26 | 10 | 20 | 2586 | 401699 | 74841 | 0.57 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 1068 | 208 | 63 | 124 | 22784 | 3008424 | 337436 | 2.18 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 310 | 218 | 53 | 102 | 20856 | 2673879 | 363322 | 3.86 |

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
| when `run-conductor.sh` is missing, `orchestrate.sh` exits 2 with exactly one stderr line naming `run-conductor.sh` and the reason (No such file or directory), launching nothing further ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 39 | 76 | 13475 | 1817113 | 276454 | 2.33 | 335 | unknown | 0/5 | nothing-left |  |  | full |
| when `run-conductor.sh` exists but is not executable (mode 644), `orchestrate.sh` exits 2 with exactly one stderr line naming `run-conductor.sh` and the reason (Permission denied), launching nothing further ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 91 | 25 | 48 | 10097 | 1316040 | 110549 | 1.06 | unknown | unknown | unknown | unknown |  |  | pin |
| after a failed conductor launch, `orchestrate.sh` asks `solvable-issues.sh` no further time — it was asked exactly once ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 110 | 27 | 52 | 10868 | 1428253 | 111872 | 1.10 | unknown | unknown | unknown | unknown |  |  | pin |
| a conductor that starts and exits with its issue still listed and unparked is relaunched, and `solvable-issues.sh` is asked again, as today ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 14 | 28 | 5481 | 706813 | 95827 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| `orchestrate.sh`'s header `Exit:` line documents exit 2 for a `run-conductor.sh` that cannot be started ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 20 | 2586 | 401699 | 74841 | 0.57 | 106 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| when `run-conductor.sh` is missing, `orchestrate.sh` exits 2 with exactly one stderr line naming `run-conductor.sh` and the reason (No such file or directory), launching nothing further ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 74 | 0.62 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 8 | 7 | 0 | 0 | 8 | 0 | 1 | 0 | 0 | 7 | 8 |
| fast | 21 | 22 | 21 | 20 | 21 |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 1 | 632 | 0 | 1 | 0 | 0 | 0 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 116 | 226 | 43640 | 5682303 | 700758 | 6.04 |
