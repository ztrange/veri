### 📊 Metrics — issue 2755

Wall time for the issue: 3403 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2774.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.59 over 23 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87101 tokens, largest 147751 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87101 |
| 2 | $0.07 | 94103 |
| 3 | $0.03 | 95226 |
| 4 | $0.03 | 97095 |
| 5 | $0.04 | 99392 |
| 6 | $0.02 | 99889 |
| 7 | $0.11 | 110709 |
| 8 | $0.02 | 111026 |
| 9 | $0.02 | 111282 |
| 10 | $0.03 | 112851 |
| 11 | $0.04 | 115359 |
| 12 | $0.03 | 116434 |
| 13 | $0.14 | 131573 |
| 14 | $0.09 | 139698 |
| 15 | $0.04 | 140701 |
| 16 | $0.04 | 142352 |
| 17 | $0.04 | 144044 |
| 18 | $0.03 | 144750 |
| 19 | $0.03 | 145456 |
| 20 | $0.03 | 146166 |
| 21 | $0.03 | 146738 |
| 22 | $0.03 | 147006 |
| 23 | $0.04 | 147751 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 1025 | 0 | 31945 | 0.09 |
| diff | 4 | 1 | 1 | 0 | 377 | 73 | 27 | 44 | 8023 | 630084 | 105436 | 0.57 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 2 | 1 | 0 | 228 | 39 | 12 | 22 | 4182 | 280741 | 62362 | 0.23 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 159 | 41 | 16 | 24 | 4866 | 349343 | 75019 | 0.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 377 | 0.57 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The `wait-leaf.sh develop-red` wait in `fake_claude_env`, the helper of the `gh-driver` scenario in `test_run_conductor.py`, has a ceiling of at least 25 s and below 30 s, and its exit code is asserted, so a wait that times out fails the case with a message saying the leaf did not finish, that message reaching pytest's failure output rather than `leaf` `None`; test-only, no production change, the case stays a process case through real `detach-leaf.sh`, `supervise.sh` and `run-leaf.sh` ⟦diff-checked⟧ ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 73 | 27 | 44 | 8023 | 630084 | 105436 | 0.57 | 523 | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| fast | 29 | 26 |
| affected | 25 | 22 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 28 | 46 | 9048 | 630084 | 137381 | 2.25 (estimate) |
