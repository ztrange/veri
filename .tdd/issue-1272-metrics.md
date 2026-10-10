### 📊 Metrics — issue 1272

Wall time for the issue: 3988 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1402.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1090 | 12489 | 34585 | 0.15 |
| diff | 6 | 3 | 0 | 0 | 856 | 138 | 48 | 96 | 15353 | 2341090 | 264876 | 1.45 |
| red | 3 | 0 | 0 | 0 | 146 | 132 | 33 | 62 | 16610 | 1845658 | 173300 | 1.04 |
| pin | 3 | 3 | 0 | 0 | 60 | 50 | 17 | 34 | 6523 | 762293 | 129029 | 0.66 |
| green | 12 | 3 | 3 | 0 | 1227 | 172 | 61 | 116 | 18648 | 2532086 | 506427 | 2.47 |
| refactor | 6 | 3 | 0 | 0 | 232 | 78 | 30 | 60 | 9185 | 1341306 | 262025 | 1.27 |
| predicate | 1 | 0 | 0 | 0 | 7 | 4 | 2 | 4 | 500 | 58219 | 36071 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 13 | 3 | 0 | 746 | 243 | 78 | 152 | 27585 | 3279527 | 667251 | 3.27 |
| developer | claude-sonnet-5-5 | 16 | 0 | 0 | 0 | 1792 | 339 | 114 | 222 | 40324 | 5613614 | 739062 | 3.92 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 1227 | 2.47 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| the stub_waits harness cases are retired from parallel-conductors.test.sh with no replacement — 'stub_waits' await_context returns only once its context line has arrived, however many looks that takes', 'stub_waits' heartbeats prints its heartbeat lines without calling sleep', 'await_gone returns only once the stopped stub's pid is gone, however many looks that takes, without calling sleep', 'stub_waits' await_gone returns only once the other stub's pid is gone, however many looks that takes, without calling sleep' and 'the again case's stub holds after its step-done result without calling sleep' are gone, and no other case of the suite is changed ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 22 | 3659 | 515053 | 89896 | 0.45 | 160 | n/a | n/a | n/a |  |  | full |
| parallel-conductors.sh driven through run_cli with VERI_PARALLEL=2 and conductors faked at the Popen boundary prints each conductor's assistant events as 'context <issue> <cache_read + cache_creation>' attributed to its own issue, and a non-assistant event carrying cache usage prints no 'context' line: replaces 'VERI_PARALLEL=2 prints each conductor's assistant events as 'context <issue> <cache_read + cache_creation>' attributed to its own issue', 'a non-assistant event carrying cache usage prints no 'context' line' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 135 | 46 | 90 | 15236 | 2077850 | 348686 | 1.76 | 416 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary stops a conductor over VERI_CONDUCTOR_CTX_BUDGET only once its step-done call's result appears, never mid-step or at the call; under the default budget of 120000 does not stop one at a step-done result nor at a later tool result once over budget with no new step-done; and leaves the conductor running beside a stopped one to run to its own end: replaces 'a conductor over VERI_CONDUCTOR_CTX_BUDGET is not stopped mid-step nor at the step-done call, and is stopped once that call's result appears', 'a conductor under the default VERI_CONDUCTOR_CTX_BUDGET of 120000 is not stopped at a step-done result, nor at a later tool result once over budget with no new step-done', 'while one conductor is stopped over VERI_CONDUCTOR_CTX_BUDGET at step-done, the conductor running beside it is not stopped and runs to its own end' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 168 | 49 | 94 | 19312 | 2314601 | 368272 | 1.90 | 761 | 1/2 | 1/5 | nothing-left |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary launches a conductor stopped over VERI_CONDUCTOR_CTX_BUDGET again for the same issue before a not-yet-launched solvable issue takes its slot, and prints 'restarted <n>' naming its issue: replaces 'a conductor stopped over VERI_CONDUCTOR_CTX_BUDGET is launched again for the same issue before a not-yet-launched solvable issue takes its slot', 'a conductor relaunched after an over-budget stop prints 'restarted <n>' naming its issue' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 129 | 46 | 88 | 16418 | 2088892 | 353823 | 1.79 | 742 | 1/2 | 1/5 | nothing-left |  |  | already-satisfied |
| make hermetic's slice of parallel-conductors.test.sh in tests/hermetic/hermetic-suites.test.sh still matches the suite after the removals — its markers and its assertion count updated or the slice dropped — so the slice's own check does not report that the markers moved ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 19 | 38 | 6422 | 958052 | 89927 | 0.52 | 276 | n/a | n/a | n/a |  |  | full |
| parallel-conductors.test.sh's remaining cases still pass; if none remain the file is gone, no guard table, roster, workflow comment or CLAUDE.md count outside .tdd/ and docs/ names it, and CLAUDE.md's suite count matches the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 53 | 20 | 40 | 5772 | 926204 | 121124 | 0.63 | 489 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| parallel-conductors.sh driven through run_cli with VERI_PARALLEL=2 and conductors faked at the Popen boundary prints each conductor's assistant events as 'context <issue> <cache_read + cache_creation>' attributed to its own issue, and a non-assistant event carrying cache usage prints no 'context' line: replaces 'VERI_PARALLEL=2 prints each conductor's assistant events as 'context <issue> <cache_read + cache_creation>' attributed to its own issue', 'a non-assistant event carrying cache usage prints no 'context' line' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 74 | 0.39 |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary stops a conductor over VERI_CONDUCTOR_CTX_BUDGET only once its step-done call's result appears, never mid-step or at the call; under the default budget of 120000 does not stop one at a step-done result nor at a later tool result once over budget with no new step-done; and leaves the conductor running beside a stopped one to run to its own end: replaces 'a conductor over VERI_CONDUCTOR_CTX_BUDGET is not stopped mid-step nor at the step-done call, and is stopped once that call's result appears', 'a conductor under the default VERI_CONDUCTOR_CTX_BUDGET of 120000 is not stopped at a step-done result, nor at a later tool result once over budget with no new step-done', 'while one conductor is stopped over VERI_CONDUCTOR_CTX_BUDGET at step-done, the conductor running beside it is not stopped and runs to its own end' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 80 | 0.44 |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary launches a conductor stopped over VERI_CONDUCTOR_CTX_BUDGET again for the same issue before a not-yet-launched solvable issue takes its slot, and prints 'restarted <n>' naming its issue: replaces 'a conductor stopped over VERI_CONDUCTOR_CTX_BUDGET is launched again for the same issue before a not-yet-launched solvable issue takes its slot', 'a conductor relaunched after an over-budget stop prints 'restarted <n>' naming its issue' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 78 | 0.44 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 22 | 23 | 22 | 22 | 23 | 22 | 22 | 24 | 24 | 22 | 23 | 24 | 23 | 23 | 23 | 23 | 23 |  |  |
| affected | 24 | 1 | 0 | 24 | 24 | 24 | 1 | 0 | 22 | 1 | 1 | 0 | 365 | 22 | 22 | 0 | 40 | 45 | 22 |
| target | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 192 | 374 | 67909 | 8893141 | 1406313 | 7.19 |
