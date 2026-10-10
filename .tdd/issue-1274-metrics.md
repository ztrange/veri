### 📊 Metrics — issue 1274

Wall time for the issue: 4445 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 7 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1103 | 12489 | 34984 | 0.15 |
| red | 9 | 1 | 0 | 0 | 1162 | 347 | 94 | 182 | 44214 | 5049790 | 480932 | 2.87 |
| pin | 4 | 3 | 1 | 0 | 100 | 78 | 24 | 48 | 9986 | 1135216 | 143469 | 0.79 |
| green | 11 | 3 | 2 | 0 | 807 | 215 | 75 | 148 | 26365 | 3607161 | 493734 | 2.60 |
| refactor | 6 | 3 | 0 | 0 | 1862 | 113 | 44 | 84 | 12649 | 2051036 | 265825 | 1.40 |
| exhausted | 1 | 0 | 0 | 0 | 24 | 16 | 5 | 10 | 2014 | 218427 | 41239 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 11 | 3 | 0 | 1101 | 252 | 79 | 152 | 30920 | 3486044 | 575361 | 2.96 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 2864 | 525 | 164 | 322 | 65411 | 8588075 | 884822 | 5.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 523 | 1.12 |
| pin | 56 | 0.36 | 0 | 0.00 |
| green | 294 | 1.67 | 392 | 0.40 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 24 | 0.21 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary, under VERI_PARALLEL=1, stops a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step only after its step-done result and relaunches it for the same issue, never stopping or relaunching one that never crosses the budget; hands each conductor the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL exactly as they were, set or unset; and starts the outer supervisor with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries: replaces 'with VERI_PARALLEL=1 a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step is stopped only after its step-done result and relaunched for the same issue, and one that never crosses the budget is never stopped or relaunched', 'the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL reach each conductor exactly as they were, set or unset', 'the outer supervisor runs with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 218 | 70 | 132 | 28235 | 3344231 | 396273 | 2.20 | 876 | 2/2 | 0/5 | nothing-left |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli in a real scratch git repository, with conductors faked at the Popen boundary, leaves the caller's git status --porcelain empty after a launch in a repo that has never seen veri and in one with no info/ directory, keeps the exclude file's last line intact while adding .tdd/* exactly once over two launches, and, resolving its git common dir and working directory from that repository rather than its own directory, appends to no other info/exclude and writes no .tdd/parallel.exit or conductor log outside it: replaces 'in a target repo that has never seen veri, the caller's git status --porcelain stays empty after a launch', 'a repo with no info/ directory still has an empty git status --porcelain after a launch', 'the caller's exclude keeps its last line intact and gains .tdd/* exactly once over two launches', '#1158: a parallel-conductors.sh that resolves its git common dir and working directory from its own directory, not the suite's scratch repository, appends to no info/exclude and writes no .tdd/parallel.exit or conductor log outside that repository' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 154 | 52 | 102 | 19135 | 2573768 | 366063 | 1.91 | 357 | 1/2 | 1/5 | nothing-structural |  |  | already-satisfied |
| parallel-conductors.sh supervising a conductor-<n> prints no leaf-role.sh refusal, and run through a symlink to the skill directory and from another working directory finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place, pinned by test_parallel_conductors.py cases beside C2's one shim test: replaces 'supervising a conductor-<n> prints no leaf-role.sh refusal', 'run through a symlink to the skill directory and from another working directory, parallel-conductors.sh finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 192 | 59 | 118 | 23082 | 2987240 | 371143 | 2.01 | 2087 | 1/2 | 1/5 | nothing-structural |  |  | already-satisfied |
| the symlinked-run case in test_parallel_conductors.py (test_a_launch_run_through_a_symlink_to_the_skills_directory_from_another_cwd_answers_as_it_does_in_place_and_prints_no_leaf_role_refusal) passes under make test's environment as it does run alone, so the in-place leg answers exit 0 with '#7 — done' and 'start 7' there too, without changing production code ⟦added⟧ ⟦criterion 1⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 205 | 61 | 120 | 24776 | 3156391 | 291720 | 1.73 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary, under VERI_PARALLEL=1, stops a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step only after its step-done result and relaunches it for the same issue, never stopping or relaunching one that never crosses the budget; hands each conductor the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL exactly as they were, set or unset; and starts the outer supervisor with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries: replaces 'with VERI_PARALLEL=1 a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step is stopped only after its step-done result and relaunched for the same issue, and one that never crosses the budget is never stopped or relaunched', 'the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL reach each conductor exactly as they were, set or unset', 'the outer supervisor runs with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.40 |
| parallel-conductors.sh driven through run_cli in a real scratch git repository, with conductors faked at the Popen boundary, leaves the caller's git status --porcelain empty after a launch in a repo that has never seen veri and in one with no info/ directory, keeps the exclude file's last line intact while adding .tdd/* exactly once over two launches, and, resolving its git common dir and working directory from that repository rather than its own directory, appends to no other info/exclude and writes no .tdd/parallel.exit or conductor log outside it: replaces 'in a target repo that has never seen veri, the caller's git status --porcelain stays empty after a launch', 'a repo with no info/ directory still has an empty git status --porcelain after a launch', 'the caller's exclude keeps its last line intact and gains .tdd/* exactly once over two launches', '#1158: a parallel-conductors.sh that resolves its git common dir and working directory from its own directory, not the suite's scratch repository, appends to no info/exclude and writes no .tdd/parallel.exit or conductor log outside that repository' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 64 | 0.46 |
| parallel-conductors.sh supervising a conductor-<n> prints no leaf-role.sh refusal, and run through a symlink to the skill directory and from another working directory finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place, pinned by test_parallel_conductors.py cases beside C2's one shim test: replaces 'supervising a conductor-<n> prints no leaf-role.sh refusal', 'run through a symlink to the skill directory and from another working directory, parallel-conductors.sh finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 1741 | 0.53 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 5 | 5 | 5 | 1 | 1 | 0 | 0 | 1 | 3 | 0 | 2 | 1 | 1 | 5 | 0 | 5 | 1 | 1 | 323 | 322 | 5 | 319 | 3 |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 4 | 0 | 4 | 5 |  |
| fast | 23 | 24 | 23 | 24 | 22 | 22 | 22 | 21 | 21 | 22 | 23 | 23 | 24 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 243 | 474 | 96331 | 12074119 | 1460183 | 8.01 |
