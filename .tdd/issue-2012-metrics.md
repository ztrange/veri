### 📊 Metrics — issue 2012

Wall time for the issue: 2501 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2113.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1009 | 17051 | 13088 | 0.04 |
| red | 11 | 4 | 0 | 0 | 371 | 283 | 59 | 118 | 22014 | 1718039 | 202885 | 1.07 |
| green | 10 | 5 | 0 | 0 | 583 | 301 | 74 | 146 | 18545 | 2213707 | 154455 | 0.79 |
| refactor | 10 | 5 | 0 | 0 | 164 | 93 | 29 | 54 | 4982 | 664791 | 125301 | 0.43 |
| pin | 2 | 1 | 1 | 0 | 75 | 41 | 10 | 20 | 3674 | 278089 | 18216 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 16 | 1 | 0 | 534 | 310 | 65 | 130 | 18074 | 1699438 | 216056 | 0.89 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 545 | 323 | 91 | 176 | 22375 | 2667341 | 238863 | 1.09 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 125 | 94 | 17 | 34 | 9775 | 524898 | 59026 | 0.47 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 75 | 0.11 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| network_guard, small_case_guard and unit/test_popen_command.py reach popen_command through one module path, so one module object is loaded: a unit-tier case (no process) asserts the helper module each guard uses is the same object as the one test_popen_command.py imports ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 33 | 64 | 7819 | 906741 | 87410 | 0.39 | 254 | unknown | 0/5 | nothing-left |  |  | full |
| A unit-tier case (no process) fails if either network_guard or small_case_guard stops calling the popen_command helper and keeps its own copy of the Popen-args-to-basename lines, one assertion per guard, watched red by reverting one guard to its own copy; no production change ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 135 | 27 | 54 | 13449 | 802987 | 77242 | 0.58 | unknown | 1/2 | unknown | unknown |  |  | pin |
| network_guard reads `args` once, so an iterator `args` such as iter(["gh"]) gets network_guard's own refusal, the same outcome as the list ["gh"], instead of an IndexError: a unit-tier case (no process) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 86 | 22 | 44 | 5783 | 580803 | 82087 | 0.32 | 220 | unknown | 0/5 | nothing-left |  |  | full |
| small_case_guard reads `args` once, so an iterator `args` such as iter(["python3", "<path under veri/>"]) gets the same outcome as the equivalent list (allowed), not a refusal: a unit-tier case (no process) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 105 | 26 | 50 | 5371 | 673099 | 82298 | 0.33 | 227 | unknown | 0/5 | nothing-left |  |  | full |
| small_case_guard raises its own TypeError for a list `args` holding a non-str word, ["ls", 5], as it did before #1894, instead of passing it through: a unit-tier case (no process) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 167 | 30 | 58 | 7515 | 799890 | 86718 | 0.37 | 298 | unknown | 0/5 | nothing-left |  |  | full |
| fix the CI failure: skills/tdd/scripts/tests/py/test_supervise.py — FAILED test_supervise.py::test_cli_records_the_skill_clones_own_head_in_a_launch_events_skill_commit_and_the_literal_unknown_for_a_skill_outside_a_git_clone - AssertionError: assert [(1, [a00415...]), (0, [unknown])] == [(0, [a00415...]), (0, [unknown])] (the first launch exited 1, not 0) ⟦ci-repair⟧ ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 115 | 34 | 68 | 9278 | 1111106 | 85102 | 0.42 | 540 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| network_guard, small_case_guard and unit/test_popen_command.py reach popen_command through one module path, so one module object is loaded: a unit-tier case (no process) asserts the helper module each guard uses is the same object as the one test_popen_command.py imports ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.08 |
| network_guard reads `args` once, so an iterator `args` such as iter(["gh"]) gets network_guard's own refusal, the same outcome as the list ["gh"], instead of an IndexError: a unit-tier case (no process) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 30 | 0.10 |
| small_case_guard reads `args` once, so an iterator `args` such as iter(["python3", "<path under veri/>"]) gets the same outcome as the equivalent list (allowed), not a refusal: a unit-tier case (no process) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 28 | 0.08 |
| small_case_guard raises its own TypeError for a list `args` holding a non-str word, ["ls", 5], as it did before #1894, instead of passing it through: a unit-tier case (no process) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.08 |
| fix the CI failure: skills/tdd/scripts/tests/py/test_supervise.py — FAILED test_supervise.py::test_cli_records_the_skill_clones_own_head_in_a_launch_events_skill_commit_and_the_literal_unknown_for_a_skill_outside_a_git_clone - AssertionError: assert [(1, [a00415...]), (0, [unknown])] == [(0, [a00415...]), (0, [unknown])] (the first launch exited 1, not 0) ⟦ci-repair⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 32 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 4 | 10 | 3 | 2 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 5 | 3 | 3 | 4 | 3 | 2 | 5 | 3 | 3 | 33 | 8 | 14 | 8 |
| fast | 0 | 5 | 7 | 6 | 6 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 5 | 5 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 173 | 340 | 50224 | 4891677 | 513945 | 2.45 |
