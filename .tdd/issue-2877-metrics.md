### 📊 Metrics — issue 2877

Wall time for the issue: 2632 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2914.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.40 over 81 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87231 tokens, largest 170356 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87231 |
| 2 | $0.07 | 93927 |
| 3 | $0.03 | 95882 |
| 4 | $0.03 | 97506 |
| 5 | $0.02 | 98100 |
| 6 | $0.03 | 98856 |
| 7 | $0.02 | 99193 |
| 8 | $0.02 | 99557 |
| 9 | $0.02 | 100181 |
| 10 | $0.02 | 100527 |
| 11 | $0.03 | 102343 |
| 12 | $0.04 | 104373 |
| 13 | $0.05 | 108515 |
| 14 | $0.03 | 109660 |
| 15 | $0.04 | 111615 |
| 16 | $0.03 | 112007 |
| 17 | $0.03 | 112665 |
| 18 | $0.03 | 113258 |
| 19 | $0.03 | 113744 |
| 20 | $0.03 | 114461 |
| 21 | $0.03 | 115868 |
| 22 | $0.03 | 116911 |
| 23 | $0.03 | 118102 |
| 24 | $0.03 | 118880 |
| 25 | $0.03 | 120152 |
| 26 | $0.03 | 121456 |
| 27 | $0.03 | 122168 |
| 28 | $0.03 | 123101 |
| 29 | $0.03 | 123794 |
| 30 | $0.03 | 124566 |
| 31 | $0.03 | 125010 |
| 32 | $0.04 | 126764 |
| 33 | $0.05 | 129284 |
| 34 | $0.03 | 130020 |
| 35 | $0.03 | 130285 |
| 36 | $0.03 | 130948 |
| 37 | $0.04 | 132553 |
| 38 | $0.03 | 132929 |
| 39 | $0.04 | 134025 |
| 40 | $0.03 | 134509 |
| 41 | $0.04 | 135582 |
| 42 | $0.03 | 136137 |
| 43 | $0.03 | 137091 |
| 44 | $0.04 | 138098 |
| 45 | $0.04 | 139466 |
| 46 | $0.04 | 140596 |
| 47 | $0.03 | 141334 |
| 48 | $0.03 | 141693 |
| 49 | $0.04 | 143253 |
| 50 | $0.03 | 143547 |
| 51 | $0.03 | 144120 |
| 52 | $0.03 | 144729 |
| 53 | $0.03 | 145023 |
| 54 | $0.04 | 146370 |
| 55 | $0.04 | 147117 |
| 56 | $0.03 | 147613 |
| 57 | $0.09 | 155766 |
| 58 | $0.05 | 157586 |
| 59 | $0.03 | 157927 |
| 60 | $0.04 | 158436 |
| 61 | $0.04 | 159229 |
| 62 | $0.04 | 159672 |
| 63 | $0.03 | 159872 |
| 64 | $0.04 | 160396 |
| 65 | $0.03 | 160621 |
| 66 | $0.04 | 161052 |
| 67 | $0.03 | 161257 |
| 68 | $0.04 | 162328 |
| 69 | $0.04 | 162873 |
| 70 | $0.04 | 163913 |
| 71 | $0.04 | 164877 |
| 72 | $0.04 | 165261 |
| 73 | $0.04 | 165997 |
| 74 | $0.04 | 166367 |
| 75 | $0.04 | 166748 |
| 76 | $0.04 | 167489 |
| 77 | $0.04 | 168027 |
| 78 | $0.04 | 169013 |
| 79 | $0.04 | 169591 |
| 80 | $0.04 | 169735 |
| 81 | $0.04 | 170356 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 13 | 1 | 2 | 1274 | 0 | 31984 | 0.09 |
| red | 10 | 3 | 0 | 0 | 445 | 312 | 60 | 116 | 24994 | 1809349 | 263148 | 1.26 |
| green | 6 | 3 | 0 | 0 | 291 | 98 | 26 | 48 | 7212 | 673264 | 92232 | 0.37 |
| refactor | 3 | 0 | 0 | 0 | 27 | 19 | 8 | 14 | 1151 | 160018 | 62533 | 0.18 |
| pin | 4 | 4 | 0 | 0 | 87 | 62 | 20 | 36 | 5627 | 501009 | 61924 | 0.26 |
| diff | 4 | 2 | 0 | 0 | 136 | 63 | 18 | 36 | 4701 | 498057 | 57780 | 0.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 13 | 0 | 0 | 403 | 186 | 48 | 92 | 15042 | 1198576 | 229227 | 0.84 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 516 | 315 | 70 | 130 | 23149 | 1978610 | 283063 | 1.14 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 82 | 66 | 15 | 30 | 6768 | 464511 | 57311 | 0.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| mutation-probe.sh records the command it ran as `shlex.join` of its argv (not `" ".join`), so a probe run as `bash -c '<script>'` reads back from the record with its script as one quoted word (small case in skills/tdd/scripts/tests/py/unit/test_mutation_probe.py) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 68 | 18 | 36 | 4935 | 483194 | 96379 | 0.34 | 281 | unknown | 0/5 | nothing-left |  |  | full |
| a pin record written by mutation-probe.sh for a test whose title contains an apostrophe and spaces is replayed by pin-recheck.sh with that title reaching the test runner as one argument (process case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 92 | 20 | 36 | 7790 | 645696 | 43642 | 0.25 | unknown | unknown | unknown | unknown |  |  | pin |
| when mutation-probe.sh runs its command through its sibling timed-test-run.sh (argv[4] is that wrapper), the recorded command is the test command alone, `shlex.join(argv[7:])`, carrying neither the wrapper nor its per-run temp-dir path (small case in skills/tdd/scripts/tests/py/unit/test_mutation_probe.py) ⟦criterion 5⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 75 | 21 | 36 | 6316 | 498637 | 80576 | 0.31 | 224 | unknown | 0/5 | nothing-left |  |  | full |
| a probe run through the real sibling timed-test-run.sh writes a record whose command starts with the test runner and that pin-recheck.sh replays green from another directory, while the existing #2814 cases replaying records with a dead timed-test-run.sh prefix stay green (process case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 12 | 24 | 5093 | 387910 | 42381 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| `.tdd/issue-2827-mutations.md` and `.tdd/issue-2843-mutations.md` have their unquoted `bash -c` command corrected so the script is one single-quoted word, each field's length prefix updated to match ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 10 | 20 | 2167 | 274596 | 27828 | 0.12 | 110 | n/a | n/a | n/a |  |  | full |
| `.tdd/issue-2878-mutations.md`, which landed after the issue was filed, has its two unquoted `bash -c` commands corrected the same way, length prefixes included, so the repository-wide audit can hold ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 8 | 16 | 2534 | 223461 | 29952 | 0.12 | 99 | n/a | n/a | n/a |  |  | full |
| a `tree_audit` case searches this repository's own `.tdd/*-mutations.md` records and fails on any command containing `bash -c` not immediately followed by a quote, proven by breaking it on purpose (new file skills/tdd/scripts/tests/py/test_mutation_records_quoted.py) ⟦criterion 4⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 93 | 26 | 48 | 9429 | 711535 | 86329 | 0.55 | unknown | 1/2 | unknown | unknown |  |  | pin |
| fix the CI failure: skills/tdd/scripts/tests/py/test_fast_tier_guard.py — FAILED test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it and test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table: AssertionError: test_mutation_records_quoted.py: guard-clean, outside the tier ⟦ci-repair⟧ ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 99 | 17 | 34 | 5421 | 416668 | 130530 | 0.42 | 560 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| mutation-probe.sh records the command it ran as `shlex.join` of its argv (not `" ".join`), so a probe run as `bash -c '<script>'` reads back from the record with its script as one quoted word (small case in skills/tdd/scripts/tests/py/unit/test_mutation_probe.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.05 |
| when mutation-probe.sh runs its command through its sibling timed-test-run.sh (argv[4] is that wrapper), the recorded command is the test command alone, `shlex.join(argv[7:])`, carrying neither the wrapper nor its per-run temp-dir path (small case in skills/tdd/scripts/tests/py/unit/test_mutation_probe.py) ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| fix the CI failure: skills/tdd/scripts/tests/py/test_fast_tier_guard.py — FAILED test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it and test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table: AssertionError: test_mutation_records_quoted.py: guard-clean, outside the tier ⟦ci-repair⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 2 | 4 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 5 | 5 | 5 | 4 |
| fast | 21 | 20 | 19 | 18 | 19 | 19 | 19 | 20 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 3 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 133 | 252 | 44959 | 3641697 | 569601 | 5.81 (estimate) |
