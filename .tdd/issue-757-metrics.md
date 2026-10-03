### 📊 Metrics — issue 757

Wall time for the issue: 1366 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/791.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 9 | 2 | 4 | 1133 | 60287 | 38820 | 0.35 |
| diff | 6 | 3 | 0 | 0 | 109 | 65 | 21 | 42 | 6237 | 806345 | 230088 | 2.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 4 | 4 | 0 | 0 | 70 | 41 | 12 | 24 | 4338 | 433316 | 153300 | 1.40 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 54 | 33 | 11 | 22 | 3032 | 433316 | 115608 | 1.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `test_status.py` holds no case that reads `tests/status.test.sh` or any other `*.test.sh` — `test_status_test_sh_keeps_only_the_adr_0027_survivors_and_the_floor` and `test_status_test_sh_floor_holds_an_exit_2_case_and_a_bad_argument_stderr_case` are deleted, and `STATUS_SUITE`, `STATUS_SUITE_FLOOR` and `STATUS_SUITE_CUT` are gone with them ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 8 | 16 | 2608 | 322049 | 78524 | 0.74 | 68 | unknown | unknown | unknown |  |  | full |
| every other case in `test_status.py` keeps its name and its assertions, and `test_no_case_in_this_suite_calls_a_function_of_veri_status_other_than_main` stays ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 6 | 12 | 1931 | 219533 | 77446 | 0.70 | 52 | unknown | unknown | unknown |  |  | full |
| `tests/status.test.sh` is unchanged by the branch ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 17 | 7 | 14 | 1698 | 264763 | 74118 | 0.68 | 56 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 1 | 1 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 23 | 46 | 7370 | 866632 | 268908 | 2.47 |
