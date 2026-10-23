### 📊 Metrics — issue 2101

Wall time for the issue: 2351 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2188.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.86 over 43 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87216 |
| 2 | $0.02 | 87630 |
| 3 | $0.02 | 88366 |
| 4 | $0.03 | 90348 |
| 5 | $0.02 | 90826 |
| 6 | $0.02 | 91318 |
| 7 | $0.02 | 91673 |
| 8 | $0.02 | 91962 |
| 9 | $0.02 | 92611 |
| 10 | $0.03 | 94327 |
| 11 | $0.06 | 98861 |
| 12 | $0.03 | 100549 |
| 13 | $0.04 | 103075 |
| 14 | $0.03 | 103999 |
| 15 | $0.03 | 104857 |
| 16 | $0.06 | 109649 |
| 17 | $0.04 | 112085 |
| 18 | $0.03 | 112828 |
| 19 | $0.03 | 113206 |
| 20 | $0.03 | 113882 |
| 21 | $0.03 | 115139 |
| 22 | $0.03 | 115899 |
| 23 | $0.03 | 116683 |
| 24 | $0.03 | 117849 |
| 25 | $0.03 | 118603 |
| 26 | $0.03 | 119483 |
| 27 | $0.03 | 120636 |
| 28 | $0.03 | 121398 |
| 29 | $0.03 | 122178 |
| 30 | $0.03 | 123317 |
| 31 | $0.03 | 124097 |
| 32 | $0.03 | 125011 |
| 33 | $0.03 | 125303 |
| 34 | $0.03 | 125552 |
| 35 | $0.03 | 125880 |
| 36 | $0.03 | 126409 |
| 37 | $0.03 | 126705 |
| 38 | $0.03 | 127076 |
| 39 | $0.03 | 128117 |
| 40 | $0.03 | 129015 |
| 41 | $0.03 | 129457 |
| 42 | $0.03 | 129938 |
| 43 | $0.03 | 130442 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 933 | 0 | 30886 | 0.09 |
| red | 5 | 0 | 0 | 0 | 190 | 78 | 20 | 36 | 10430 | 513624 | 117662 | 0.45 |
| pin | 5 | 5 | 0 | 0 | 178 | 55 | 16 | 32 | 5015 | 405705 | 68509 | 0.26 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 190 | 63 | 17 | 34 | 5948 | 405705 | 99395 | 0.35 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 190 | 78 | 20 | 36 | 10430 | 513624 | 117662 | 0.45 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On `main`, with a `.tdd/issue-<n>.md` ledger whose unchecked `⟦skill-edit⟧` step names a stale unit, `prose-owed.sh` exits non-zero and prints the unit — pinned through the entry point's exit code in a medium `@pytest.mark.process("git")` case in skills/tdd/scripts/tests/py/test_prose_owed_waiver_process.py, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 7 | 14 | 3100 | 175414 | 49822 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| On a `tdd/<n>-…` branch with no `.tdd/issue-<n>.md` ledger of its own, a stale unit named by an unchecked `⟦skill-edit⟧` step in another issue's `.tdd/issue-<m>.md` makes `prose-owed.sh` exit non-zero and print the unit — pinned through the entry point's exit code in a medium `@pytest.mark.process("git")` case in skills/tdd/scripts/tests/py/test_prose_owed_waiver_process.py, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 6 | 12 | 2725 | 157765 | 32698 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| On a `tdd/<n>-…` branch whose own `.tdd/issue-<n>.md` names no stale unit while another issue's `.tdd/issue-<m>.md` holds an unchecked `⟦skill-edit⟧` step naming it, `prose-owed.sh` exits non-zero and prints the unit — pinned through the entry point's exit code in a medium `@pytest.mark.process("git")` case in skills/tdd/scripts/tests/py/test_prose_owed_waiver_process.py, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 9 | 16 | 3600 | 227199 | 34256 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| On the run's own `tdd/<n>-…` branch, a stale unit whose `⟦skill-edit⟧` step in `.tdd/issue-<n>.md` is already checked (`- [x]`) makes `prose-owed.sh` exit non-zero and print the unit — pinned through the entry point's exit code in a medium `@pytest.mark.process("git")` case in skills/tdd/scripts/tests/py/test_prose_owed_waiver_process.py, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 6 | 12 | 2728 | 159439 | 33756 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| On the run's own `tdd/<n>-…` branch, with two stale units of which only one is named by an unchecked `⟦skill-edit⟧` step, `prose-owed.sh` exits non-zero and prints the second, unnamed unit (and not the waived one) — pinned through the entry point's exit code in a medium `@pytest.mark.process("git")` case in skills/tdd/scripts/tests/py/test_prose_owed_waiver_process.py, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 14 | 3292 | 199512 | 35639 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 11 | 10 | 13 | 7 |  |  |  |  |  |
| target | 11 | 10 | 10 | 11 | 12 | 12 | 6 | 11 | 3 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 37 | 70 | 16378 | 919329 | 217057 | 0.80 |
