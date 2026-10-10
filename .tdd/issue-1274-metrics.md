### 📊 Metrics — issue 1274

Wall time for the issue: 4591 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1416.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1103 | 12489 | 34984 | 0.15 |
| red | 11 | 1 | 0 | 0 | 1227 | 397 | 112 | 218 | 51089 | 5978725 | 578502 | 3.42 |
| pin | 6 | 5 | 1 | 0 | 136 | 106 | 33 | 66 | 13687 | 1513883 | 228235 | 1.20 |
| green | 15 | 4 | 3 | 0 | 1212 | 274 | 98 | 194 | 33452 | 4667694 | 667798 | 3.47 |
| refactor | 8 | 4 | 0 | 0 | 2241 | 144 | 56 | 108 | 16064 | 2604664 | 355145 | 1.84 |
| exhausted | 1 | 0 | 0 | 0 | 24 | 16 | 5 | 10 | 2014 | 218427 | 41239 | 0.21 |
| diff | 6 | 2 | 1 | 0 | 901 | 143 | 49 | 94 | 17011 | 2289452 | 266666 | 1.47 |
| rebase | 2 | 1 | 0 | 0 | 1548 | 33 | 13 | 26 | 3854 | 592549 | 85176 | 0.44 |
| predicate | 1 | 0 | 0 | 0 | 10 | 8 | 3 | 6 | 759 | 109595 | 38519 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 23 | 18 | 5 | 0 | 2163 | 400 | 127 | 248 | 49191 | 5611339 | 959277 | 4.89 |
| developer | claude-sonnet-5-5 | 28 | 0 | 0 | 0 | 5146 | 729 | 243 | 476 | 89842 | 12376139 | 1336987 | 7.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 56 | 0.36 | 0 | 0.00 |
| green | 699 | 2.54 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| diff | 365 | 0.90 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary, under VERI_PARALLEL=1, stops a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step only after its step-done result and relaunches it for the same issue, never stopping or relaunching one that never crosses the budget; hands each conductor the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL exactly as they were, set or unset; and starts the outer supervisor with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries: replaces 'with VERI_PARALLEL=1 a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step is stopped only after its step-done result and relaunched for the same issue, and one that never crosses the budget is never stopped or relaunched', 'the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL reach each conductor exactly as they were, set or unset', 'the outer supervisor runs with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 218 | 70 | 132 | 28235 | 3344231 | 396273 | 2.20 | 876 | 2/2 | 0/5 | nothing-left |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli in a real scratch git repository, with conductors faked at the Popen boundary, leaves the caller's git status --porcelain empty after a launch in a repo that has never seen veri and in one with no info/ directory, keeps the exclude file's last line intact while adding .tdd/* exactly once over two launches, and, resolving its git common dir and working directory from that repository rather than its own directory, appends to no other info/exclude and writes no .tdd/parallel.exit or conductor log outside it: replaces 'in a target repo that has never seen veri, the caller's git status --porcelain stays empty after a launch', 'a repo with no info/ directory still has an empty git status --porcelain after a launch', 'the caller's exclude keeps its last line intact and gains .tdd/* exactly once over two launches', '#1158: a parallel-conductors.sh that resolves its git common dir and working directory from its own directory, not the suite's scratch repository, appends to no info/exclude and writes no .tdd/parallel.exit or conductor log outside that repository' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 154 | 52 | 102 | 19135 | 2573768 | 366063 | 1.91 | 357 | 1/2 | 1/5 | nothing-structural |  |  | already-satisfied |
| parallel-conductors.sh supervising a conductor-<n> prints no leaf-role.sh refusal, and run through a symlink to the skill directory and from another working directory finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place, pinned by test_parallel_conductors.py cases beside C2's one shim test: replaces 'supervising a conductor-<n> prints no leaf-role.sh refusal', 'run through a symlink to the skill directory and from another working directory, parallel-conductors.sh finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 192 | 59 | 118 | 23082 | 2987240 | 371143 | 2.01 | 2087 | 1/2 | 1/5 | nothing-structural |  |  | already-satisfied |
| the symlinked-run case in test_parallel_conductors.py (test_a_launch_run_through_a_symlink_to_the_skills_directory_from_another_cwd_answers_as_it_does_in_place_and_prints_no_leaf_role_refusal) passes under make test's environment as it does run alone, so the in-place leg answers exit 0 with '#7 — done' and 'start 7' there too, without changing production code ⟦added⟧ ⟦criterion 1⟧ | 8 | 2 | 0 | 0 | 0 | 0 | 248 | 76 | 150 | 30341 | 3894082 | 383162 | 2.23 | unknown | 2/2 | unknown | unknown |  |  | pin |
| SCOPE-LOOP.md documents VERI_PARALLEL — at 1 rung 2 is unchanged, above 1 it runs parallel-conductors.sh detach-then-wait and relays the report — and CONTEXT.md records rung 3 — its entry names parallel-conductors.sh, defines In flight as local to one invocation and cites a new ADR — pinned by small cases in test_parallel_conductors.py reading those files as text: replaces 'SCOPE-LOOP.md documents VERI_PARALLEL: at 1 rung 2 is unchanged, above 1 it runs parallel-conductors.sh detach-then-wait and relays the report', 'CONTEXT.md records rung 3: its entry names parallel-conductors.sh, In flight is defined as local to one invocation, and a new ADR is cited' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 125 | 47 | 94 | 15513 | 2184072 | 354278 | 1.79 | 987 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| make hermetic's slice of parallel-conductors.test.sh in tests/hermetic/hermetic-suites.test.sh is dropped or updated in step with the removals, so no slice reads a suite or markers that no longer exist and the hermetic suite's own check does not report that the markers moved ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 81 | 27 | 52 | 9966 | 1194798 | 170025 | 0.90 | 415 | 1/2 | unknown | unknown |  |  | full |
| parallel-conductors.test.sh's remaining cases still pass; if none remain the file is gone, no guard table, roster, workflow comment or CLAUDE.md count outside .tdd/ and docs/ names it (no-awk-v-patterns.test.sh's EXEMPT row, no-nested-suites.test.sh's #1050 case repointed at a suite that exists or a planted fixture), and CLAUDE.md's suite count matches the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 103 | 38 | 74 | 11658 | 1796798 | 220336 | 1.18 | 563 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary, under VERI_PARALLEL=1, stops a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step only after its step-done result and relaunches it for the same issue, never stopping or relaunching one that never crosses the budget; hands each conductor the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL exactly as they were, set or unset; and starts the outer supervisor with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries: replaces 'with VERI_PARALLEL=1 a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step is stopped only after its step-done result and relaunched for the same issue, and one that never crosses the budget is never stopped or relaunched', 'the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL reach each conductor exactly as they were, set or unset', 'the outer supervisor runs with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.40 |
| parallel-conductors.sh driven through run_cli in a real scratch git repository, with conductors faked at the Popen boundary, leaves the caller's git status --porcelain empty after a launch in a repo that has never seen veri and in one with no info/ directory, keeps the exclude file's last line intact while adding .tdd/* exactly once over two launches, and, resolving its git common dir and working directory from that repository rather than its own directory, appends to no other info/exclude and writes no .tdd/parallel.exit or conductor log outside it: replaces 'in a target repo that has never seen veri, the caller's git status --porcelain stays empty after a launch', 'a repo with no info/ directory still has an empty git status --porcelain after a launch', 'the caller's exclude keeps its last line intact and gains .tdd/* exactly once over two launches', '#1158: a parallel-conductors.sh that resolves its git common dir and working directory from its own directory, not the suite's scratch repository, appends to no info/exclude and writes no .tdd/parallel.exit or conductor log outside that repository' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 64 | 0.46 |
| parallel-conductors.sh supervising a conductor-<n> prints no leaf-role.sh refusal, and run through a symlink to the skill directory and from another working directory finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place, pinned by test_parallel_conductors.py cases beside C2's one shim test: replaces 'supervising a conductor-<n> prints no leaf-role.sh refusal', 'run through a symlink to the skill directory and from another working directory, parallel-conductors.sh finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 1741 | 0.53 |
| SCOPE-LOOP.md documents VERI_PARALLEL — at 1 rung 2 is unchanged, above 1 it runs parallel-conductors.sh detach-then-wait and relays the report — and CONTEXT.md records rung 3 — its entry names parallel-conductors.sh, defines In flight as local to one invocation and cites a new ADR — pinned by small cases in test_parallel_conductors.py reading those files as text: replaces 'SCOPE-LOOP.md documents VERI_PARALLEL: at 1 rung 2 is unchanged, above 1 it runs parallel-conductors.sh detach-then-wait and relays the report', 'CONTEXT.md records rung 3: its entry names parallel-conductors.sh, In flight is defined as local to one invocation, and a new ADR is cited' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 379 | 0.45 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 5 | 5 | 5 | 1 | 1 | 0 | 0 | 1 | 3 | 0 | 2 | 1 | 1 | 5 | 0 | 5 | 1 | 1 | 323 | 322 | 5 | 319 | 3 | 3 | 1 | 1 | 1 | 2 | 256 | 2 | 1 | 35 | 36 | 304 | 0 |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 4 | 0 | 4 | 5 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |  |  |  |  |  |
| fast | 23 | 24 | 23 | 24 | 22 | 22 | 22 | 21 | 21 | 22 | 23 | 23 | 24 | 23 | 23 | 24 | 26 | 24 | 24 | 26 | 24 | 24 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 298 | 289 | 300 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 370 | 724 | 139033 | 17987478 | 2296264 | 12.38 |
