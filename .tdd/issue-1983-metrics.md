### 📊 Metrics — issue 1983

Wall time for the issue: 1442 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2123.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 13 | 2 | 4 | 1631 | 30715 | 37028 | 0.11 |
| diff | 8 | 4 | 0 | 0 | 554 | 349 | 60 | 116 | 28567 | 2500467 | 297047 | 1.28 |
| red | 3 | 0 | 0 | 0 | 184 | 134 | 32 | 64 | 14917 | 1312933 | 94363 | 0.52 |
| pin | 3 | 3 | 0 | 0 | 81 | 55 | 14 | 28 | 4095 | 374465 | 43112 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 263 | 152 | 36 | 72 | 12725 | 1084894 | 192035 | 0.72 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 572 | 399 | 72 | 140 | 36485 | 3133686 | 279515 | 1.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In tests/py/test_grade_prose_process.py every case that checks grade_prose's verdicts or output drives veri/grade_prose.py in-process through the run_cli fixture instead of starting grade-prose.sh or a nested python3, keeping its name and outcome (a real supervise.sh and stub claude may stay, with their process mark); exactly one case keeps launching grade-prose.sh as a real child process, keeps its @pytest.mark.process mark, and asserts the shim forwards its arguments and its exit code; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 106 | 15 | 28 | 7351 | 558274 | 94590 | 0.37 | 193 | n/a | n/a | n/a |  |  | full |
| In tests/py/test_skill_edit_step_process.py every case that checks skill_edit_step's outcomes drives veri/skill_edit_step.py in-process through the run_cli fixture instead of starting skill-edit-step.sh or a nested python3, keeping its name and outcome (real git, supervise.sh and stub claude may stay, with their process mark); exactly one case keeps launching skill-edit-step.sh as a real child process, keeps its @pytest.mark.process mark, and asserts the shim forwards its arguments and its exit code; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 13 | 24 | 4314 | 532393 | 76237 | 0.29 | 119 | n/a | n/a | n/a |  |  | full |
| A case in tests/py/test_mutation_parity_process.py launches mutation-parity.sh as a real child process, marked @pytest.mark.process, on a one-row pairs table and asserts the shim forwards the table argument (the row's verdict line on stdout) and the exit code; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 10 | 20 | 3646 | 311241 | 37378 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| In tests/py/test_mutation_parity_process.py every case that checks mutation_parity's verdicts or output runs the module's pytest runs in-process, through pytester.runpytest_inprocess substituted for mutation_parity's pytest runner, instead of a nested python3 or pytest, keeping its name and outcome; only the shim case from the previous step keeps a real python3 child of mutation-parity.sh; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 163 | 21 | 42 | 13758 | 1049079 | 72627 | 0.42 | 252 | n/a | n/a | n/a |  |  | full |
| A case in tests/py/test_mutation_parity_process.py, driving mutation_parity in-process with its pytest runs in-process, applies a row's mutation to a source file and asserts that once the case's run ends the source file holds its original bytes and no bytecode or imported module built from the mutated source survives, so a later in-process import in the same interpreter reads the original source; no production change ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 16 | 32 | 6328 | 562779 | 45914 | 0.23 | unknown | unknown | unknown | unknown |  |  | pin |
| A case in tests/py/test_mutation_parity_process.py, driving mutation_parity in-process with its pytest runs in-process, runs rows whose verdicts are proven, unproven and owed and rows that end in exit 2 (a missing suite path, an uncollected pytest node id) and asserts each row's verdict and the exit code are the ones the module gives when its pytest runs are real processes; no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 99 | 20 | 40 | 9038 | 813378 | 54183 | 0.31 | unknown | unknown | unknown | unknown |  |  | pin |
| Across the branch's diff of tests/py/test_mutation_parity_process.py, tests/py/test_grade_prose_process.py and tests/py/test_skill_edit_step_process.py no existing case is removed or renamed and no existing case's asserted outcome changes, apart from moving in-process; no suite asserts a speed, time or process count ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 11 | 22 | 3144 | 360721 | 53593 | 0.20 | 119 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 4 | 5 | 5 | 5 | 5 | 4 | 5 |  |  |  |  |  |
| affected | 12 | 14 | 17 | 17 | 3 | 3 | 3 | 4 | 4 | 4 | 4 | 18 |
| target | 4 | 2 | 3 | 2 | 3 | 3 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 108 | 212 | 49210 | 4218580 | 471550 | 2.09 |
