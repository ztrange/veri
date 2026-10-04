### 📊 Metrics — issue 776

Wall time for the issue: 8561 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 19 of 20 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/856.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 41 | 36 | 6 | 12 | 3529 | 288066 | 48612 | 0.52 |
| red | 37 | 16 | 0 | 1 | 1957 | 1411 | 310 | 604 | 123918 | 16023291 | 1812823 | 20.19 |
| green | 36 | 16 | 2 | 0 | 3863 | 1169 | 318 | 630 | 109830 | 15550713 | 1587426 | 18.01 |
| refactor | 31 | 15 | 0 | 0 | 1785 | 649 | 176 | 352 | 60676 | 8039174 | 1345965 | 13.59 |
| pin | 3 | 3 | 0 | 0 | 82 | 54 | 13 | 26 | 5587 | 543149 | 126102 | 1.23 |
| diff | 2 | 1 | 0 | 0 | 144 | 64 | 13 | 26 | 6386 | 670469 | 112385 | 1.16 |
| predicate | 7 | 0 | 0 | 0 | 131 | 97 | 25 | 50 | 7673 | 999834 | 279258 | 2.59 |
| structural | 5 | 0 | 0 | 0 | 1326 | 129 | 35 | 70 | 12183 | 1689265 | 222904 | 2.37 |
| transform | 4 | 3 | 1 | 0 | 254 | 59 | 17 | 34 | 6085 | 695652 | 160751 | 1.55 |
| rebase | 3 | 1 | 0 | 0 | 2549 | 168 | 27 | 56 | 8653 | 1506255 | 75638 | 1.98 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 61 | 56 | 3 | 1 | 6044 | 1639 | 414 | 822 | 153465 | 19430905 | 2601714 | 27.77 |
| developer | claude-opus-5-5 | 68 | 0 | 0 | 0 | 6088 | 2197 | 526 | 1038 | 191055 | 26574963 | 3170150 | 35.41 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 754 | 3.55 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 254 | 1.55 | 0 | 0.00 |
| rebase | 0 | 0.00 | 2549 | 1.98 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| refactor-budget.sh reads VERI_REFACTOR_BUDGET, VERI_ISSUE_REFACTOR_BUDGET and <count> with leading zeros as decimal: budget 010 with count 9 still lets another transform run, and 08 is eight with no arithmetic error (updates the leading-zero rows of test_main_reads_its_arguments_by_position_and_compares_them_as_bash_arithmetic_does in py/test_refactor_budget.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 182 | 41 | 82 | 17004 | 1947678 | 266730 | 2.86 | 450 | unknown | 0/5 | structural-owed |  |  | full |
| refactor-budget.sh compares a <count> past 2^63 as its decimal value, never wrapped: count 9223372036854775808 against budget 5 says the budget is spent (exit 3) (updates the past-2^63 rows of the same case) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 161 | 42 | 84 | 13886 | 2030503 | 271426 | 2.86 | 393 | unknown | 0/5 | structural-owed |  |  | full |
| refactor-budget.sh given a budget variable or <count> that is not a non-negative whole number exits 2 naming that variable or <count> on stderr ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 97 | 19 | 38 | 7859 | 1124371 | 106559 | 1.23 | unknown | unknown | unknown | unknown |  |  | pin |
| refactor-overflow.sh reads <reached> with leading zeros as decimal: 010 skips ten candidates and 08 skips eight, never exiting 1 with an arithmetic error (updates the leading-zero rows of test_main_returns_gh_s_own_failing_code_and_reads_reached_as_bash_arithmetic in py/test_refactor_overflow.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 161 | 43 | 80 | 13755 | 1910632 | 267302 | 2.80 | 395 | unknown | 0/5 | structural-owed |  |  | full |
| refactor-overflow.sh reads a <reached> past 2^63 as its decimal value, skipping every candidate rather than exiting 1 (updates the past-2^63 row of the same case) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 151 | 44 | 86 | 14214 | 2053418 | 267242 | 2.83 | 382 | unknown | 0/5 | nothing-left |  |  | full |
| refactor-overflow.sh given a <reached> that is not a non-negative whole number exits 2 naming <reached> on stderr ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 17 | 34 | 6710 | 950845 | 103463 | 1.15 | unknown | unknown | unknown | unknown |  |  | pin |
| wait-ci.sh reads its slice-seconds and total-seconds arguments with leading zeros as decimal: 060 is sixty seconds and 09 is nine (updates the leading-zero rows of test_main_reads_its_numeric_arguments_and_a_deadline_file_as_bash_arithmetic in py/test_wait_ci.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 170 | 43 | 86 | 15951 | 2110848 | 276984 | 2.96 | 527 | unknown | 0/5 | nothing-structural |  |  | full |
| wait-ci.sh given a slice-seconds or total-seconds argument that is not a non-negative whole number (1.5, abc) exits 2 naming that argument on stderr, rather than giving up after one poll with exit 3 (updates the non-number rows of the same case) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 259 | 61 | 120 | 23980 | 3191203 | 302315 | 3.54 | 1171 | unknown | 1/5 | structural-owed |  |  | full |
| wait-ci.sh given a negative slice-seconds or total-seconds (-5) exits 2 naming that argument on stderr, rather than polling and exiting 3 (updates the -5 rows of test_main_reads_its_numeric_arguments_with_leading_zeros_as_decimal_and_a_deadline_file_as_bash_arithmetic_issue_776 in py/test_wait_ci.py) ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 153 | 40 | 80 | 12838 | 1884618 | 262645 | 2.74 | 566 | unknown | 0/5 | structural-owed |  |  | full |
| wait-ci.sh given a deadline file under .tdd/ci-deadline-<sha> that is empty, unreadable or holds a non-numeric word such as now exits 2 naming the file on stderr, rather than reading it as 0 or as a variable (updates the deadline-file rows of the same case) ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 276 | 63 | 126 | 27743 | 3181242 | 336951 | 3.89 | 874 | 1/2 | 1/5 | structural-owed |  |  | full |
| workqueue.sh reads VERI_WORKQUEUE_LOCK_WAIT with leading zeros as decimal: 010 waits ten seconds' worth of lock polls, not eight (updates the leading-zero rows of test_start_done_park_and_assign_take_the_lock_directory_polling_it_for_the_wait_times_20_and_release_it_on_every_path in py/test_workqueue.py) ⟦criterion 1⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 335 | 89 | 176 | 30670 | 4413690 | 515870 | 5.62 | 885 | unknown | 0/5 | structural-owed |  |  | full |
| workqueue.sh given a VERI_WORKQUEUE_LOCK_WAIT that is not a non-negative whole number (0.5, abc) exits 2 naming VERI_WORKQUEUE_LOCK_WAIT on stderr for every subcommand that takes the lock, assign included, never writing without the lock and never reporting an unknown subcommand (updates the 0.5 and abc rows of the same case) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 196 | 49 | 96 | 16686 | 2390817 | 280522 | 3.06 | 483 | unknown | 0/5 | structural-owed |  |  | full |
| leaf-timeout.sh reads its baseline, --full seconds and VERI_REFACTOR_BUDGET with leading zeros as decimal: baseline 0200 sizes as two hundred (1200) and 08 as eight, never exiting 1 (updates the leading-zero rows of test_main_reproduces_leaf_timeout_sh_bash_arithmetic_in_stdout_and_return_code in py/test_leaf_timeout.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 43 | 86 | 15978 | 2045941 | 267342 | 2.87 | 385 | unknown | 0/5 | structural-owed |  |  | full |
| leaf-timeout.sh sizes a baseline past 2^63 from its decimal value, never wrapped to a small or negative number (updates the past-2^63 rows of the same case, if any) ⟦criterion 1⟧ | 8 | 3 | 0 | 1 | 0 | 0 | 211 | 57 | 110 | 19807 | 2869672 | 344360 | 3.73 | 409 | unknown | 0/5 | structural-owed |  |  | full |
| leaf-timeout.sh given a baseline, --full seconds, VERI_REFACTOR_BUDGET or VERI_TIMEOUT that is not a non-negative whole number exits 2 naming that argument or variable on stderr ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 224 | 52 | 102 | 19138 | 2548429 | 275860 | 3.10 | 460 | unknown | 1/5 | structural-owed |  |  | full |
| leaf-timeout.sh prints a VERI_TIMEOUT given with leading zeros as its decimal value: VERI_TIMEOUT=010 prints 10, never 010 ⟦added⟧ ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 166 | 52 | 104 | 16044 | 2433880 | 346743 | 3.58 | 460 | 1/2 | 0/5 | structural-owed |  |  | full |
| push-branch.sh reads VERI_PUSH_RETRIES and VERI_PUSH_BACKOFF with leading zeros as decimal: VERI_PUSH_RETRIES=007 makes 7 retries after the first attempt and 08 makes 8, never exiting 1 without recording its push-failed event (updates test_main_keeps_bash_octal_arithmetic_for_leading_zero_tunables in py/test_push_branch.py) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 241 | 52 | 102 | 21247 | 2599208 | 287133 | 3.24 | 501 | unknown | 1/5 | structural-owed |  |  | full |
| push-branch.sh given a VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF that is not a non-negative whole number exits 2 naming that variable on stderr ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 10 | 20 | 6501 | 469332 | 92869 | 0.97 | unknown | unknown | unknown | unknown |  |  | pin |
| every case the six scripts' bash and pytest suites held before this branch keeps its assertions unchanged, apart from the octal-parity rows the steps above name ⟦diff-checked⟧ ⟦criterion 4⟧ | 18 | 4 | 1 | 0 | 0 | 0 | 349 | 90 | 180 | 32327 | 4055220 | 775298 | 7.66 | 167 | unknown | unknown | unknown |  |  | full |
| every case each script's suites already hold passes ⟦full-suite⟧ ⟦criterion 4⟧ | 3 | 1 | 0 | 0 | 0 | 1 | 168 | 27 | 56 | 8653 | 1506255 | 75638 | 1.98 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| refactor-budget.sh reads VERI_REFACTOR_BUDGET, VERI_ISSUE_REFACTOR_BUDGET and <count> with leading zeros as decimal: budget 010 with count 9 still lets another transform run, and 08 is eight with no arithmetic error (updates the leading-zero rows of test_main_reads_its_arguments_by_position_and_compares_them_as_bash_arithmetic_does in py/test_refactor_budget.py) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 88 | 0.83 |
| refactor-budget.sh compares a <count> past 2^63 as its decimal value, never wrapped: count 9223372036854775808 against budget 5 says the budget is spent (exit 3) (updates the past-2^63 rows of the same case) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 92 | 0.86 |
| refactor-overflow.sh reads <reached> with leading zeros as decimal: 010 skips ten candidates and 08 skips eight, never exiting 1 with an arithmetic error (updates the leading-zero rows of test_main_returns_gh_s_own_failing_code_and_reads_reached_as_bash_arithmetic in py/test_refactor_overflow.py) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 96 | 0.84 |
| refactor-overflow.sh reads a <reached> past 2^63 as its decimal value, skipping every candidate rather than exiting 1 (updates the past-2^63 row of the same case) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.81 |
| wait-ci.sh reads its slice-seconds and total-seconds arguments with leading zeros as decimal: 060 is sixty seconds and 09 is nine (updates the leading-zero rows of test_main_reads_its_numeric_arguments_and_a_deadline_file_as_bash_arithmetic in py/test_wait_ci.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 131 | 0.84 |
| wait-ci.sh given a slice-seconds or total-seconds argument that is not a non-negative whole number (1.5, abc) exits 2 naming that argument on stderr, rather than giving up after one poll with exit 3 (updates the non-number rows of the same case) ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 223 | 1.03 |
| wait-ci.sh given a negative slice-seconds or total-seconds (-5) exits 2 naming that argument on stderr, rather than polling and exiting 3 (updates the -5 rows of test_main_reads_its_numeric_arguments_with_leading_zeros_as_decimal_and_a_deadline_file_as_bash_arithmetic_issue_776 in py/test_wait_ci.py) ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 140 | 0.83 |
| wait-ci.sh given a deadline file under .tdd/ci-deadline-<sha> that is empty, unreadable or holds a non-numeric word such as now exits 2 naming the file on stderr, rather than reading it as 0 or as a variable (updates the deadline-file rows of the same case) ⟦criterion 3⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 182 | 0.93 |
| workqueue.sh reads VERI_WORKQUEUE_LOCK_WAIT with leading zeros as decimal: 010 waits ten seconds' worth of lock polls, not eight (updates the leading-zero rows of test_start_done_park_and_assign_take_the_lock_directory_polling_it_for_the_wait_times_20_and_release_it_on_every_path in py/test_workqueue.py) ⟦criterion 1⟧ | 2 | 0/5 | structural-owed | PASS | 0 | 125 | 1.26 |
| workqueue.sh given a VERI_WORKQUEUE_LOCK_WAIT that is not a non-negative whole number (0.5, abc) exits 2 naming VERI_WORKQUEUE_LOCK_WAIT on stderr for every subcommand that takes the lock, assign included, never writing without the lock and never reporting an unknown subcommand (updates the 0.5 and abc rows of the same case) ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 101 | 0.85 |
| leaf-timeout.sh reads its baseline, --full seconds and VERI_REFACTOR_BUDGET with leading zeros as decimal: baseline 0200 sizes as two hundred (1200) and 08 as eight, never exiting 1 (updates the leading-zero rows of test_main_reproduces_leaf_timeout_sh_bash_arithmetic_in_stdout_and_return_code in py/test_leaf_timeout.py) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 101 | 0.91 |
| leaf-timeout.sh sizes a baseline past 2^63 from its decimal value, never wrapped to a small or negative number (updates the past-2^63 rows of the same case, if any) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 86 | 0.82 |
| leaf-timeout.sh given a baseline, --full seconds, VERI_REFACTOR_BUDGET or VERI_TIMEOUT that is not a non-negative whole number exits 2 naming that argument or variable on stderr ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 125 | 0.99 |
| leaf-timeout.sh prints a VERI_TIMEOUT given with leading zeros as its decimal value: VERI_TIMEOUT=010 prints 10, never 010 ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 84 | 0.81 |
| push-branch.sh reads VERI_PUSH_RETRIES and VERI_PUSH_BACKOFF with leading zeros as decimal: VERI_PUSH_RETRIES=007 makes 7 retries after the first attempt and 08 makes 8, never exiting 1 without recording its push-failed event (updates test_main_keeps_bash_octal_arithmetic_for_leading_zero_tunables in py/test_push_branch.py) ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 128 | 0.97 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 3/3 | budget-spent |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 3 | 4 | 3 | 0 | 1 | 3 | 3 | 3 | 2 | 1 | 1 | 48 | 50 | 47 | 46 | 46 | 48 | 45 | 88 | 53 | 0 | 1 | 49 | 1 | 53 | 49 | 49 | 49 | 1 | 1 | 43 | 42 | 42 | 43 | 0 | 0 | 41 | 45 | 1 | 1 | 0 | 19 | 1 | 17 | 1 | 17 | 0 | 18 | 18 | 17 | 1 | 1 | 19 | 18 | 18 | 1 | 1 | 2 | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 1 | 1 | 1 | 8 | 8 | 1 | 7 | 1 | 7 | 0 | 67 | 1 | 1 | 35 | 0 | 47 | 44 | 50 | 49 | 50 | 45 | 0 |
| fast | 40 | 42 | 42 | 41 | 38 | 42 | 38 | 42 | 46 | 40 | 45 | 41 | 40 | 42 | 39 | 37 | 36 | 41 | 43 | 42 | 40 | 40 | 38 | 36 | 34 | 34 | 36 | 40 | 41 | 41 | 40 | 39 | 40 | 39 | 40 | 38 | 43 | 40 | 40 | 42 | 40 | 39 | 38 | 36 | 41 | 39 | 37 | 39 | 40 | 38 | 38 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 2 | 2 | 1 | 1 | 3 | 3 | 0 | 46 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 786 | 825 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 940 | 1860 | 344520 | 46005868 | 5771864 | 63.18 |
