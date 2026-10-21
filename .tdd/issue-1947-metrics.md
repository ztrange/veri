### 📊 Metrics — issue 1947

Wall time for the issue: 6349 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.02 over 76 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84934 |
| 2 | $0.02 | 85528 |
| 3 | $0.02 | 86118 |
| 4 | $0.03 | 88054 |
| 5 | $0.02 | 88362 |
| 6 | $0.02 | 88731 |
| 7 | $0.02 | 89062 |
| 8 | $0.02 | 89389 |
| 9 | $0.02 | 90042 |
| 10 | $0.02 | 90368 |
| 11 | $0.04 | 93259 |
| 12 | $0.02 | 93888 |
| 13 | $0.03 | 95107 |
| 14 | $0.03 | 96110 |
| 15 | $0.04 | 98151 |
| 16 | $0.03 | 99274 |
| 17 | $0.03 | 100080 |
| 18 | $0.02 | 100379 |
| 19 | $0.02 | 100945 |
| 20 | $0.02 | 101507 |
| 21 | $0.02 | 101749 |
| 22 | $0.03 | 102513 |
| 23 | $0.07 | 108509 |
| 24 | $0.03 | 109179 |
| 25 | $0.03 | 109882 |
| 26 | $0.03 | 110416 |
| 27 | $0.03 | 111058 |
| 28 | $0.02 | 111305 |
| 29 | $0.02 | 111552 |
| 30 | $0.02 | 111859 |
| 31 | $0.03 | 112203 |
| 32 | $0.04 | 114642 |
| 33 | $0.04 | 116255 |
| 34 | $0.03 | 117702 |
| 35 | $0.03 | 118419 |
| 36 | $0.03 | 119273 |
| 37 | $0.04 | 120696 |
| 38 | $0.04 | 122134 |
| 39 | $0.03 | 122860 |
| 40 | $0.03 | 123505 |
| 41 | $0.03 | 124160 |
| 42 | $0.03 | 125112 |
| 43 | $0.04 | 127263 |
| 44 | $0.05 | 129787 |
| 45 | $0.04 | 131640 |
| 46 | $0.03 | 132368 |
| 47 | $0.03 | 133049 |
| 48 | $0.04 | 134527 |
| 49 | $0.03 | 135352 |
| 50 | $0.03 | 136321 |
| 51 | $0.04 | 137974 |
| 52 | $0.03 | 138819 |
| 53 | $0.03 | 139503 |
| 54 | $0.03 | 140221 |
| 55 | $0.03 | 140662 |
| 56 | $0.05 | 143567 |
| 57 | $0.04 | 144704 |
| 58 | $0.03 | 145358 |
| 59 | $0.06 | 148914 |
| 60 | $0.04 | 149698 |
| 61 | $0.03 | 149996 |
| 62 | $0.04 | 150728 |
| 63 | $0.04 | 151825 |
| 64 | $0.04 | 152446 |
| 65 | $0.04 | 153307 |
| 66 | $0.03 | 153623 |
| 67 | $0.03 | 153914 |
| 68 | $0.03 | 154162 |
| 69 | $0.03 | 154512 |
| 70 | $0.03 | 154831 |
| 71 | $0.03 | 155155 |
| 72 | $0.03 | 155593 |
| 73 | $0.03 | 156009 |
| 74 | $0.04 | 156711 |
| 75 | $0.04 | 157295 |
| 76 | $0.06 | 161014 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 14 | 1 | 2 | 1255 | 0 | 29804 | 0.09 |
| diff | 4 | 2 | 0 | 0 | 174 | 51 | 16 | 32 | 3923 | 395028 | 66830 | 0.25 |
| red | 5 | 2 | 0 | 0 | 3608 | 90 | 25 | 50 | 8150 | 704309 | 117778 | 0.45 |
| green | 3 | 1 | 0 | 0 | 156 | 62 | 13 | 26 | 4519 | 359584 | 45955 | 0.20 |
| refactor | 2 | 1 | 0 | 0 | 53 | 18 | 6 | 12 | 1087 | 149371 | 26384 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 18 | 9 | 3 | 6 | 906 | 74520 | 13919 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 275 | 98 | 25 | 50 | 7589 | 587422 | 139160 | 0.48 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 3750 | 146 | 39 | 78 | 12251 | 1095390 | 161510 | 0.64 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 3508 | 0.19 |
| green | 0 | 0.00 | 26 | 0.06 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The older case test_a_repair_marked_step_is_never_frozen_so_an_edit_to_its_test_file_is_not_rejected_and_no_record_is_written_1586 in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py no longer parametrizes over "⟦fixture-repair⟧" (it keeps "⟦suite-repair⟧" and "⟦ci-repair⟧"), since a fixture-repair step will now be frozen; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 8 | 16 | 1969 | 188996 | 42307 | 0.14 | 128 | n/a | n/a | n/a |  |  | full |
| For a step carrying ⟦fixture-repair⟧ (text shaped "<criterion>: repairs the fixture '<name>' in <fixture file>, reproduced by a case in <test file> ⟦fixture-repair⟧"), tests-frozen.sh record --step writes a record and check --step exits 1, printing the file's path, when a test file other than the step's named fixture file and Red's own recorded case file has been edited since the record; pinned by a case that starts tests-frozen in a real git repository and so carries @pytest.mark.process ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 1 | 0 | 44 | 10 | 20 | 3197 | 226805 | 78157 | 0.25 | unknown | unknown | unknown | unknown |  |  | full |
| For a step whose trailing marks carry the fixture-repair mark (its text shaped "<criterion>: repairs the fixture '<name>' in <fixture file>, reproduced by a case in <test file>" followed by that mark), tests-frozen.sh record --step writes a record and check --step exits 1, printing the file's path, when a test file other than the step's named fixture file and Red's own recorded case file has been edited since the record; pinned by a case that starts tests-frozen in a real git repository and so carries @pytest.mark.process ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 107 | 26 | 52 | 8027 | 724918 | 91865 | 0.38 | 338 | unknown | 0/5 | nothing-left |  |  | full |
| For a step whose trailing marks carry the fixture-repair mark, tests-frozen.sh check --step exits 0 with nothing on stdout when the only test file edited since the record is the step's named fixture file (the "<fixture file>" after "repairs the fixture '<name>' in"), even though that file is a test file; pinned by a case that starts tests-frozen in a real git repository and so carries @pytest.mark.process ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 11 | 22 | 3438 | 336061 | 34014 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| The tests-frozen.sh shim's header comment states that a step marked ⟦fixture-repair⟧ is frozen like any other step except for the fixture file its step text names, which Green may edit; no behaviour change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 1954 | 206032 | 24523 | 0.10 | 162 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| For a step whose trailing marks carry the fixture-repair mark (its text shaped "<criterion>: repairs the fixture '<name>' in <fixture file>, reproduced by a case in <test file>" followed by that mark), tests-frozen.sh record --step writes a record and check --step exits 1, printing the file's path, when a test file other than the step's named fixture file and Red's own recorded case file has been edited since the record; pinned by a case that starts tests-frozen in a real git repository and so carries @pytest.mark.process ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 53 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 21 | 22 | 20 | 22 | 23 |  |  |  |  |  |  |
| affected | 2 | 7 | 8 | 8 | 8 | 0 | 8 | 11 | 8 | 8 | 2 |
| target | 8 | 2 | 2 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 64 | 128 | 19840 | 1682812 | 300670 | 1.12 |
