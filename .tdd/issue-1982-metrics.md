### 📊 Metrics — issue 1982

Wall time for the issue: 2684 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2036.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1186 | 0 | 30662 | 0.09 |
| diff | 22 | 8 | 3 | 0 | 1509 | 783 | 174 | 346 | 75217 | 6342511 | 639659 | 3.55 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 9 | 3 | 0 | 538 | 242 | 47 | 94 | 18745 | 1288463 | 232300 | 0.90 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 409 | 254 | 60 | 118 | 24497 | 2281884 | 216022 | 1.58 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 573 | 296 | 68 | 136 | 33161 | 2772164 | 221999 | 1.16 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 832 | 2.28 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| verify's verdict contract runs in-process: the cases in tests/py/test_verify.py marked "a real supervise.sh and run-leaf.sh around a stub claude that answers VERDICT: PASS" or "… VERDICT: REJECT" assert verify's exit code (0 PASS, 1 REJECT, 2 no verdict) and its stdout reason through run_cli against veri/verify.py with the leaf's launch faked in-process, and carry no process mark; one case in tests/py/test_verify_process.py runs verify.sh and proves it forwards its arguments and the module's exit code. Tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 156 | 32 | 64 | 13030 | 1122051 | 128609 | 0.79 | 312 | 1/2 | unknown | unknown |  |  | full |
| supervise's launch gate runs in-process: the cases in tests/py/test_supervise.py marked "a real stub claude that a refused develop-green launch must never start (#1741)", "a real stub claude that an allowed develop-green launch must start (#1741)", "a real stub claude that a launch refused for an empty VERI_STEP must never start (#1760)" and "a real stub verify command that a launch refused for an empty --step must never start (#1760)" assert the exit code and stderr through run_cli against veri/supervise.py, with the leaf's start replaced by an in-process spy that records whether it started, and carry no process mark. Tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 13 | 26 | 4677 | 473904 | 50927 | 0.22 | 172 | n/a | n/a | n/a |  |  | full |
| supervise's model choice runs in-process: the cases in tests/py/test_supervise.py marked "run-leaf.sh run for real …, starting a stub claude" assert the model each leaf name is launched on, and the exit status recorded, through run_cli against the veri/ modules with claude's start faked in-process, and carry no process mark; one case in tests/py/test_supervise_process.py runs supervise.sh and proves it forwards its arguments and the leaf's exit code. Tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 84 | 19 | 38 | 10481 | 801253 | 59118 | 0.33 | 180 | n/a | n/a | n/a |  |  | full |
| orchestrate runs in-process: the cases in tests/py/unit/test_orchestrate.py marked "solvable-issues.sh started for real over a VERI_GH_JSON listing" drive veri/orchestrate.py through run_cli with the solvable-issues listing faked in-process, asserting the same exit codes and output, and carry no process mark; one case in tests/py/test_orchestrate_process.py runs orchestrate.sh and proves it forwards its arguments and the module's exit code. Tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 127 | 19 | 38 | 10856 | 757576 | 54074 | 0.32 | 176 | n/a | n/a | n/a |  |  | full |
| run-conductor's launch contract runs in-process: the cases in tests/py/test_run_conductor.py marked "a stub conductor script as CLAUDE_BIN …, and git archive and tar materialising the snapshot" assert the exit code and stdout/stderr through run_cli against veri/run_conductor.py with the snapshot's materialising and the conductor's start faked in-process, and carry no process mark; one case in tests/py/test_run_conductor_process.py runs run-conductor.sh and proves it forwards its arguments and the module's exit code. Tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 6 | 1 | 2 | 0 | 0 | 0 | 206 | 46 | 90 | 18932 | 1632662 | 156769 | 1.08 | 432 | 2/2 | unknown | unknown |  |  | full |
| rebase-onto-default's contract runs in-process: its four exits (3 already contains origin/<default>, 0 rebased printing the pre-rebase and onto shas, 1 conflict aborted printing the conflicting files, 2 no answer) and their stdout/stderr are each asserted through run_cli against veri/rebase_onto_default.py with git faked in-process, and one case in tests/py/test_rebase_onto_default_process.py runs rebase-onto-default.sh and proves it forwards the module's exit code; the real-git resume-discard cases stay as they are. Tests only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 16 | 32 | 7896 | 592984 | 74527 | 0.32 | 141 | n/a | n/a | n/a |  |  | full |
| the cases that need a real child process still start one and keep `@pytest.mark.process("<boundary>")`: supervise's heartbeat and hard-timeout kills, its process-group kill, its TERM/INT/HUP handling, its nested supervision, verify's hung verifier killed by the real supervise.sh, and orchestrate's SIGTERM to a conductor's process group; the branch's diff removes none of these cases nor their marks ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 15 | 30 | 5066 | 481372 | 46194 | 0.21 | 194 | n/a | n/a | n/a |  |  | full |
| no case that moved in-process loses its failure-path assertion: every case the branch moved from a process mark to run_cli asserts the same exit code (0, 1, 2 or 3) on the module's return that its process version asserted, so a module answering a wrong exit code turns at least one moved case red ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 14 | 28 | 4279 | 480709 | 69441 | 0.26 | 192 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 6 | 5 | 6 | 5 | 6 | 6 | 6 | 6 | 5 | 5 | 6 | 5 | 6 | 6 | 6 | 6 | 6 | 5 | 6 | 5 |  |  |  |  |  |  |
| affected | 0 | 9 | 10 | 0 | 10 | 10 | 26 | 0 | 13 | 13 | 0 | 0 | 1 | 0 | 20 | 20 | 20 | 20 | 8 | 0 | 8 | 9 | 51 | 51 | 51 | 51 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 175 | 348 | 76403 | 6342511 | 670321 | 3.64 |
