### 📊 Metrics — issue 2550

Wall time for the issue: 7065 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2558.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.68 over 62 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88964 tokens, largest 159157 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88964 |
| 2 | $0.03 | 90308 |
| 3 | $0.03 | 91905 |
| 4 | $0.02 | 92558 |
| 5 | $0.02 | 92923 |
| 6 | $0.02 | 93176 |
| 7 | $0.02 | 93456 |
| 8 | $0.02 | 94078 |
| 9 | $0.03 | 95232 |
| 10 | $0.05 | 98851 |
| 11 | $0.06 | 103535 |
| 12 | $0.05 | 106742 |
| 13 | $0.03 | 107958 |
| 14 | $0.02 | 108318 |
| 15 | $0.03 | 108852 |
| 16 | $0.03 | 109312 |
| 17 | $0.03 | 109923 |
| 18 | $0.03 | 110432 |
| 19 | $0.03 | 111528 |
| 20 | $0.03 | 112372 |
| 21 | $0.03 | 113246 |
| 22 | $0.03 | 114153 |
| 23 | $0.03 | 114971 |
| 24 | $0.03 | 115536 |
| 25 | $0.03 | 116134 |
| 26 | $0.02 | 116316 |
| 27 | $0.02 | 116498 |
| 28 | $0.03 | 116999 |
| 29 | $0.03 | 117752 |
| 30 | $0.03 | 118328 |
| 31 | $0.03 | 119139 |
| 32 | $0.03 | 119840 |
| 33 | $0.03 | 120134 |
| 34 | $0.03 | 121278 |
| 35 | $0.03 | 122017 |
| 36 | $0.12 | 133861 |
| 37 | $0.03 | 134517 |
| 38 | $0.03 | 135394 |
| 39 | $0.03 | 135985 |
| 40 | $0.03 | 136717 |
| 41 | $0.03 | 137622 |
| 42 | $0.03 | 138337 |
| 43 | $0.03 | 139224 |
| 44 | $0.04 | 140819 |
| 45 | $0.04 | 141871 |
| 46 | $0.04 | 142788 |
| 47 | $0.09 | 150761 |
| 48 | $0.04 | 152102 |
| 49 | $0.03 | 152287 |
| 50 | $0.03 | 152472 |
| 51 | $0.04 | 153771 |
| 52 | $0.04 | 154483 |
| 53 | $0.03 | 154845 |
| 54 | $0.04 | 155873 |
| 55 | $0.03 | 156208 |
| 56 | $0.04 | 157234 |
| 57 | $0.03 | 157501 |
| 58 | $0.03 | 157769 |
| 59 | $0.04 | 158256 |
| 60 | $0.03 | 158545 |
| 61 | $0.03 | 158876 |
| 62 | $0.03 | 159157 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 12 | 1 | 2 | 1579 | 0 | 31909 | 0.10 |
| red | 4 | 2 | 0 | 0 | 155 | 128 | 22 | 42 | 10094 | 677269 | 114811 | 0.46 |
| green | 6 | 2 | 1 | 0 | 4984 | 258 | 67 | 116 | 22960 | 1814067 | 653676 | 2.67 |
| refactor | 2 | 0 | 0 | 0 | 17 | 12 | 4 | 8 | 682 | 79728 | 48662 | 0.14 |
| diff | 2 | 1 | 0 | 0 | 173 | 65 | 13 | 26 | 5922 | 469482 | 45361 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 1746 | 137 | 34 | 64 | 12477 | 785805 | 256557 | 0.84 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 1758 | 198 | 41 | 80 | 16203 | 1301003 | 336766 | 1.13 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 1840 | 140 | 32 | 50 | 12557 | 953738 | 301096 | 1.60 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3401 | 2.03 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A veri shim run as a process by a case through the shared conftest fixture the named cases use (the autouse hermetic_environment, or the one test_verify.py/test_run_leaf.py/test_verdict_chain.py/test_detach_command_process.py launch through) runs on a Python at the 3.12 floor even when a fake python3 reporting 3.9.6 is first on PATH and no other python3 is on it: the shim exits as it does with a good interpreter, never with "veri needs Python 3.12 or newer". Pinned by a medium case (a real shim process, marked process) in a new test_shim_interpreter_floor_process.py that puts such a fake python3 first on PATH and runs a representative shim through that fixture; no production change ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 133 | 33 | 62 | 12147 | 915047 | 300796 | 0.97 | 1802 | unknown | 0/5 | nothing-left |  |  | full |
| The named cases that hand their shim a scratch or missing VERI_VENV on purpose (test_bash_version_guard_process.py, unit/test_case_tmpdir.py, and the case the issue calls test_planted) give the shim a python3 at the 3.12 floor through their own environment rather than through the outer PATH, so with a python3 reporting 3.9.6 first on the outer PATH and no other python3 on it they still pass, each keeping what it asserts; test-only change, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 13 | 26 | 5922 | 469482 | 45361 | 0.22 | 245 | n/a | n/a | n/a |  |  | full |
| A guard in conftest.py fails a process case that launches a veri shim with an environment leaving the shim's interpreter to PATH's python3 (VERI_VENV unset, or naming a directory with no executable bin/python3 at the 3.12 floor, while no python3 at the floor is first on that environment's PATH), naming the shim; pinned by a case in a new test_shim_interpreter_guard_process.py that launches such a shim with such an environment and sees the guard fail, while a case giving the shim the venv passes; no production change ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 2⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 265 | 60 | 104 | 21589 | 1656017 | 516353 | 2.30 | 3647 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A veri shim run as a process by a case through the shared conftest fixture the named cases use (the autouse hermetic_environment, or the one test_verify.py/test_run_leaf.py/test_verdict_chain.py/test_detach_command_process.py launch through) runs on a Python at the 3.12 floor even when a fake python3 reporting 3.9.6 is first on PATH and no other python3 is on it: the shim exits as it does with a good interpreter, never with "veri needs Python 3.12 or newer". Pinned by a medium case (a real shim process, marked process) in a new test_shim_interpreter_floor_process.py that puts such a fake python3 first on PATH and runs a representative shim through that fixture; no production change ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |
| A guard in conftest.py fails a process case that launches a veri shim with an environment leaving the shim's interpreter to PATH's python3 (VERI_VENV unset, or naming a directory with no executable bin/python3 at the 3.12 floor, while no python3 at the floor is first on that environment's PATH), naming the shim; pinned by a case in a new test_shim_interpreter_guard_process.py that launches such a shim with such an environment and sees the guard fail, while a case giving the shim the venv passes; no production change ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 427 | 0 | 521 | 2 | 2 | 21 | 8 | 8 | 3 | 3 | 475 | 228 | 203 | 434 | 458 |
| fast | 30 | 24 | 24 | 25 | 25 | 25 | 24 | 26 | 25 |  |  |  |  |  |  |  |  |
| target | 2 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 107 | 194 | 41237 | 3040546 | 894419 | 6.26 (estimate) |
