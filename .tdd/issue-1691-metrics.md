### 📊 Metrics — issue 1691

Wall time for the issue: 1091 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1759.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 760 | 17463 | 13065 | 0.04 |
| diff | 4 | 2 | 0 | 0 | 139 | 57 | 18 | 36 | 7062 | 499528 | 57980 | 0.27 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 74 | 33 | 9 | 18 | 3469 | 229021 | 40357 | 0.16 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 73 | 30 | 10 | 20 | 4353 | 287970 | 30688 | 0.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The bash-leg case test_1501_same_size_mutation_reverted_within_a_second_leaves_no_mutated_bytecode in skills/tdd/scripts/tests/py/test_mutation_parity_process.py checks, after the tool exits, for any bytecode (any .pyc of any cpython tag) the run wrote for the mutated module under its tmp_path, and any post-exit import it keeps runs on the interpreter the pytest leg itself uses (sys.executable), never the python3 first on PATH; so it goes red on every run when failed_cases() runs the bash suite without PYTHONDONTWRITEBYTECODE, whether or not the mutation and the revert fall within one second, and stays green against the current code (test-only change, no production change; stays a medium case marked @pytest.mark.process) ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 11 | 22 | 3891 | 315782 | 29764 | 0.14 | 111 | n/a | n/a | n/a |  |  | full |
| The pytest-leg case test_1501_pytest_suite_row_leaves_no_mutated_bytecode_and_unmutated_runs_read_current_source in skills/tdd/scripts/tests/py/test_mutation_parity_process.py checks, after the tool exits, for any bytecode (any .pyc of any cpython tag) the run wrote for the mutated module under its tmp_path, and any post-exit import it keeps runs on the interpreter the leg itself uses (the venv interpreter mutation_parity runs pytest on), never the python3 first on PATH; so it goes red on every run when pytest() runs without PYTHONDONTWRITEBYTECODE, whichever python3 is first on PATH, and stays green against the current code (test-only change, no production change; stays a medium case marked @pytest.mark.process) ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 7 | 14 | 3171 | 183746 | 28216 | 0.12 | 94 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 17 | 13 | 15 | 13 |  |
| affected | 2 | 2 | 2 | 2 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 19 | 38 | 7822 | 516991 | 71045 | 0.31 |
