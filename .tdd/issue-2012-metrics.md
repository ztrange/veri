### 📊 Metrics — issue 2012

Wall time for the issue: 1639 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2113.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1009 | 17051 | 13088 | 0.04 |
| red | 10 | 4 | 0 | 0 | 328 | 252 | 53 | 106 | 19419 | 1533401 | 183346 | 0.98 |
| green | 8 | 4 | 0 | 0 | 369 | 230 | 51 | 100 | 12668 | 1408515 | 113676 | 0.55 |
| refactor | 8 | 4 | 0 | 0 | 132 | 80 | 24 | 44 | 4176 | 543515 | 100517 | 0.35 |
| pin | 2 | 1 | 1 | 0 | 75 | 41 | 10 | 20 | 3674 | 278089 | 18216 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 14 | 1 | 0 | 460 | 282 | 58 | 116 | 16416 | 1521279 | 191076 | 0.79 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 330 | 236 | 64 | 122 | 14755 | 1734394 | 178741 | 0.77 |
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

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| network_guard, small_case_guard and unit/test_popen_command.py reach popen_command through one module path, so one module object is loaded: a unit-tier case (no process) asserts the helper module each guard uses is the same object as the one test_popen_command.py imports ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.08 |
| network_guard reads `args` once, so an iterator `args` such as iter(["gh"]) gets network_guard's own refusal, the same outcome as the list ["gh"], instead of an IndexError: a unit-tier case (no process) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 30 | 0.10 |
| small_case_guard reads `args` once, so an iterator `args` such as iter(["python3", "<path under veri/>"]) gets the same outcome as the equivalent list (allowed), not a refusal: a unit-tier case (no process) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 28 | 0.08 |
| small_case_guard raises its own TypeError for a list `args` holding a non-str word, ["ls", 5], as it did before #1894, instead of passing it through: a unit-tier case (no process) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 4 | 10 | 3 | 2 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 5 | 3 | 3 | 4 | 3 | 2 | 5 | 3 |
| fast | 0 | 5 | 7 | 6 | 6 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 139 | 272 | 40946 | 3780571 | 428843 | 2.03 |
