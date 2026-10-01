### 📊 Metrics — issue 625

Wall time for the issue: 5075 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/638.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 759 | 11318 | 35225 | 0.30 |
| red | 5 | 2 | 0 | 0 | 610 | 270 | 48 | 92 | 24322 | 2587532 | 264715 | 3.12 |
| green | 6 | 2 | 1 | 0 | 2315 | 260 | 55 | 110 | 24507 | 2619177 | 265277 | 3.14 |
| refactor | 4 | 2 | 0 | 0 | 357 | 77 | 22 | 44 | 6812 | 949944 | 162616 | 1.63 |
| pin | 1 | 1 | 0 | 0 | 176 | 23 | 5 | 10 | 2223 | 203610 | 39562 | 0.40 |
| structural | 1 | 0 | 0 | 0 | 88 | 10 | 3 | 6 | 986 | 105575 | 35760 | 0.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2198 | 2.23 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a command launched by `detach-leaf.sh` runs with SIGPIPE at its default disposition: a writer whose reader closes early dies silently, printing no `write error: Broken pipe`, as it does outside a leaf ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 196 | 41 | 82 | 16003 | 1887549 | 254835 | 2.74 | 362 | unknown | 0/5 | nothing-left |  |  | full |
| a non-PASS verdict's reason output carries only the verifier's reason: stderr written by anything `verify.sh` runs — `preserve_attempt` included — never reaches the reason file the conductor reads ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 339 | 72 | 142 | 33739 | 3633629 | 380215 | 4.44 | 2879 | 1/2 | 1/5 | structural-owed |  |  | full |
| a failure of `preserve-attempt.sh` during a non-PASS verdict is still reported where a human reads it (the verifier's stderr or the run's event log), never silenced ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 95 | 17 | 32 | 8122 | 839085 | 97120 | 1.11 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a command launched by `detach-leaf.sh` runs with SIGPIPE at its default disposition: a writer whose reader closes early dies silently, printing no `write error: Broken pipe`, as it does outside a leaf ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.76 |
| a non-PASS verdict's reason output carries only the verifier's reason: stderr written by anything `verify.sh` runs — `preserve_attempt` included — never reaches the reason file the conductor reads ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 300 | 0.87 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 0 | 0 | 0 | 78 | 77 | 80 | 79 | 77 | 75 | 76 | 75 | 72 |
| fast | 14 | 14 | 13 | 14 | 15 | 14 | 14 |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 84 | 76 | 74 | 73 |  |  |  |  |  |  |  |  |  |
| all | 536 | 531 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 134 | 264 | 59609 | 6477156 | 803155 | 8.91 |
