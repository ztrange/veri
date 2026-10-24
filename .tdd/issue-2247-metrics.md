### 📊 Metrics — issue 2247

Wall time for the issue: 1111 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2252.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.10 over 39 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89191 |
| 2 | $0.03 | 90225 |
| 3 | $0.03 | 92189 |
| 4 | $0.02 | 92478 |
| 5 | $0.02 | 92870 |
| 6 | $0.02 | 93131 |
| 7 | $0.02 | 93427 |
| 8 | $0.02 | 94110 |
| 9 | $0.03 | 94927 |
| 10 | $0.09 | 104326 |
| 11 | $0.04 | 106562 |
| 12 | $0.07 | 112617 |
| 13 | $0.13 | 126556 |
| 14 | $0.07 | 132636 |
| 15 | $0.05 | 135581 |
| 16 | $0.03 | 136547 |
| 17 | $0.03 | 136918 |
| 18 | $0.03 | 137737 |
| 19 | $0.03 | 138317 |
| 20 | $0.04 | 139932 |
| 21 | $0.03 | 140436 |
| 22 | $0.03 | 141074 |
| 23 | $0.03 | 141643 |
| 24 | $0.04 | 143035 |
| 25 | $0.04 | 144177 |
| 26 | $0.04 | 145693 |
| 27 | $0.03 | 146395 |
| 28 | $0.04 | 147153 |
| 29 | $0.04 | 148016 |
| 30 | $0.03 | 148641 |
| 31 | $0.04 | 149315 |
| 32 | $0.04 | 150136 |
| 33 | $0.03 | 150490 |
| 34 | $0.03 | 150825 |
| 35 | $0.03 | 151378 |
| 36 | $0.03 | 151699 |
| 37 | $0.04 | 152299 |
| 38 | $0.06 | 155497 |
| 39 | $0.04 | 156345 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 31 | 23 | 4 | 8 | 2668 | 78387 | 50334 | 0.16 |
| diff | 4 | 2 | 0 | 0 | 221 | 66 | 13 | 26 | 7976 | 368911 | 109171 | 0.39 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 3 | 1 | 0 | 133 | 47 | 10 | 20 | 4713 | 230015 | 82215 | 0.28 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 119 | 42 | 7 | 14 | 5931 | 217283 | 77290 | 0.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/tdd/scripts/tests/py/test_prompt_test_tiers.py builds each distinct prompt (one build-develop-prompt.sh or build-verify-prompt.sh argv) at most once per session, through one shared session-scoped cache every case reads, so no case starts a prompt build another case already started; every case keeps its assertions and still goes red under the mutant of the prompt text it pins (test-only, no production change; the cases stay process-marked, building through the real scripts) ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 6 | 12 | 2627 | 140574 | 55269 | 0.18 | 179 | n/a | n/a | n/a |  |  | full |
| skills/tdd/scripts/tests/py/test_mutation_parity_process.py: no case instance runs mutation_parity more than once — each of the five existing case functions that today runs it two or more times (test_a_row_replaced_by_a_pytest_node_id_…, test_a_row_whose_old_case_is_a_pytest_node_id_…, test_a_table_of_several_rows_…, test_a_row_whose_case_cannot_be_run_…_exits_2, test_after_the_pairs_check_exits_2_…) is edited in place into a pytest.mark.parametrize over the runs it makes today, each parametrized instance making exactly one run and asserting that run's exit code, stdout verdict and (where the case checks it today) byte-identical tree; no new test function is added, none is deleted, and no expected value the case asserts today is dropped or changed, so each instance still goes red under the mutant of the behaviour it pins (test-only edit of existing cases, no production change; the cases stay medium, process-marked, through real bash suites and pytest) ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 7 | 14 | 5349 | 228337 | 53902 | 0.21 | 186 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 13 | 14 | 15 | 14 |
| affected | 18 | 21 | 22 | 22 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 17 | 34 | 10644 | 447298 | 159505 | 0.55 |
