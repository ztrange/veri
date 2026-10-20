### 📊 Metrics — issue 1879

Wall time for the issue: 5291 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 14 of 14 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1925.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 12 | 1 | 2 | 1424 | 17463 | 15768 | 0.06 |
| diff | 36 | 14 | 4 | 0 | 4356 | 1140 | 235 | 456 | 89453 | 7430709 | 897771 | 4.74 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 19 | 15 | 4 | 0 | 972 | 344 | 75 | 146 | 24760 | 1970272 | 323844 | 1.25 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 1605 | 445 | 98 | 186 | 39168 | 3131181 | 286103 | 1.42 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 1793 | 363 | 63 | 126 | 26949 | 2346719 | 303592 | 2.12 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 2788 | 3.15 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In skills/tdd/scripts/tests/py/test_supervise.py, the inline `class Leaf` definitions before the `fake_clocked_leaf` helper (the cases from about :626 to :2292) are replaced by the shared `StubLeaf`, widened with parameters where a body differs; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 12 | 22 | 4658 | 340796 | 35907 | 0.17 | 152 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_supervise.py, no `class Leaf` remains at all: the one inside `fake_clocked_leaf` and the cases after it (about :3228 and :3767) use `StubLeaf`, `fake_clocked_leaf` and `install_awake_fakes`, the helper widened with a git pass-through and a Popen hook for the :3228 case; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 15 | 28 | 6761 | 497552 | 40767 | 0.22 | 266 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_supervise.py, the in-process missing-argument case `test_main_refuses_a_missing_or_empty_name_and_a_missing_cmd_…` is deleted and the `run_cli` one kept, and `clean_env` no longer deletes `VERI_*` names the autouse `hermetic_environment` fixture already deletes (its `setenv` half stays); every other case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 102 | 15 | 28 | 5661 | 457375 | 37409 | 0.20 | 337 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_parallel_conductors.py, no `for name in TUNABLES` delenv loop remains (`TUNABLES` itself stays), and `recording_kill` is defined only once, the shared one, every former site using it; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 22 | 3753 | 320090 | 32457 | 0.15 | 101 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_verify.py, no case deletes a `VERI_*` name with `monkeypatch.delenv`, and `VERIFY_LEAF_ARGS` is deleted in one fixture rather than per case; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 70 | 14 | 28 | 5562 | 449862 | 36381 | 0.19 | 189 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_verify.py, older cases that inline their own `monkeypatch.setattr(subprocess, …)` leaf fakes use the existing `answering_leaf` or `tamper_scratch` helpers where those fit; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 217 | 37 | 72 | 19267 | 1510184 | 122451 | 0.99 | 375 | 1/2 | unknown | unknown |  |  | full |
| In skills/tdd/scripts/tests/py/test_run_conductor.py, one helper patches the process boundary (the `subprocess.run/Popen/call/check_call/check_output` and `os.system/fork/posix_spawn/posix_spawnp/execv/execvp/execve` loops), and all six sites — `fake_git`, `fake_locked_fetch` and the four inline cases — use it; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 9 | 18 | 4459 | 259433 | 35568 | 0.16 | 122 | n/a | n/a | n/a |  |  | full |
| `ViaStdin` is defined only in skills/tdd/scripts/tests/py/conftest.py: test_ledger_steps_process.py, test_next_pending_refactor_process.py and test_next_unchecked_process.py import it instead of defining their own; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 8 | 16 | 2173 | 224452 | 32856 | 0.13 | 59 | n/a | n/a | n/a |  |  | full |
| `as_requested`/`fake_run`/`refused` are each defined once in test_transform_touches_tests.py, and `fake_run`/`fake_call`/`FakePopen` are each defined once in test_timed_test_run.py (the older `test_main_*` cases use the `calls` fixture); every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 14 | 26 | 7501 | 490226 | 47729 | 0.24 | 103 | n/a | n/a | n/a |  |  | full |
| A `process` or `tree_audit` mark whose argument is only whitespace is refused at collection by conftest.py's `pytest_collection_modifyitems`, pinned by a planted case beside the existing empty-argument ones in tests/py/unit/test_process_mark.py that goes red with the conftest.py change reverted; test-only, no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 6 | 1 | 2 | 0 | 0 | 0 | 184 | 33 | 66 | 10302 | 960322 | 155261 | 0.88 | 955 | 2/2 | unknown | unknown |  |  | full |
| conftest.py's `shim_problems` reports a shim whose first line is not `#!/bin/sh` (for example `#!/bin/bash`) as not the canonical shim, pinned by a planted case in tests/py/test_shims.py that goes red with the conftest.py change reverted; the real scripts directory still audits clean; test-only, no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 121 | 25 | 50 | 7366 | 741006 | 159530 | 0.77 | 856 | 1/2 | unknown | unknown |  |  | full |
| The real-scripts-directory shim audit (`shim_problems(SCRIPTS, EXEMPT) == []`) is its own `tree_audit` case in tests/py/test_shims.py, no longer the first assert of the exemption-table case, which keeps its name and its remaining asserts; test-only, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 9 | 16 | 2573 | 239039 | 34426 | 0.14 | 56 | n/a | n/a | n/a |  |  | full |
| "Path is `ROOT` or under it" is one helper in conftest.py, used at both sites that spell it (`hermetic_environment` and `in_repository_outside`); behaviour otherwise identical; test-only, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 24 | 2881 | 344807 | 56475 | 0.20 | 401 | n/a | n/a | n/a |  |  | full |
| `run_cli` in conftest.py and `run()` in skills/tdd/scripts/veri/entry.py share one exit-mapping function instead of `run_cli` copying `run()`'s mapping; `run_cli` still returns `(code, stdout, stderr)` without calling `sys.exit` or redirecting fd 1, and `entry.run` behaves as before; every case keeps its name and outcome ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 78 | 21 | 40 | 6536 | 595565 | 70554 | 0.30 | 779 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 6 | 6 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 5 | 6 | 7 | 6 |  |  |  |  |  |  |
| affected | 31 | 31 | 32 | 31 | 31 | 31 | 3 | 3 | 14 | 15 | 14 | 14 | 14 | 14 | 21 | 22 | 1 | 0 | 2 | 2 | 325 | 328 | 1 | 0 | 329 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 321 | 326 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 236 | 458 | 90877 | 7448172 | 913539 | 4.79 |
