# Plan for #776 — numeric tunables and arguments read a leading zero as decimal, not octal

Octal-parity cases the port pinned — each step below that reverses one names it, and its Green
updates only that case's leading-zero / non-number rows to the behaviour this issue asks for;
criterion 4 excludes exactly those rows.

- [x] refactor-budget.sh reads VERI_REFACTOR_BUDGET, VERI_ISSUE_REFACTOR_BUDGET and <count> with leading zeros as decimal: budget 010 with count 9 still lets another transform run, and 08 is eight with no arithmetic error (updates the leading-zero rows of test_main_reads_its_arguments_by_position_and_compares_them_as_bash_arithmetic_does in py/test_refactor_budget.py) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] refactor-budget.sh compares a <count> past 2^63 as its decimal value, never wrapped: count 9223372036854775808 against budget 5 says the budget is spent (exit 3) (updates the past-2^63 rows of the same case) ⟦criterion 1⟧
- [ ] refactor-budget.sh given a budget variable or <count> that is not a non-negative whole number exits 2 naming that variable or <count> on stderr ⟦criterion 2⟧
- [ ] refactor-overflow.sh reads <reached> with leading zeros as decimal: 010 skips ten candidates and 08 skips eight, never exiting 1 with an arithmetic error (updates the leading-zero rows of test_main_returns_gh_s_own_failing_code_and_reads_reached_as_bash_arithmetic in py/test_refactor_overflow.py) ⟦criterion 1⟧
- [ ] refactor-overflow.sh reads a <reached> past 2^63 as its decimal value, skipping every candidate rather than exiting 1 (updates the past-2^63 row of the same case) ⟦criterion 1⟧
- [ ] refactor-overflow.sh given a <reached> that is not a non-negative whole number exits 2 naming <reached> on stderr ⟦criterion 2⟧
- [ ] wait-ci.sh reads its slice-seconds and total-seconds arguments with leading zeros as decimal: 060 is sixty seconds and 09 is nine (updates the leading-zero rows of test_main_reads_its_numeric_arguments_and_a_deadline_file_as_bash_arithmetic in py/test_wait_ci.py) ⟦criterion 1⟧
- [ ] wait-ci.sh given a slice-seconds or total-seconds argument that is not a non-negative whole number (1.5, abc) exits 2 naming that argument on stderr, rather than giving up after one poll with exit 3 (updates the non-number rows of the same case) ⟦criterion 2⟧
- [ ] wait-ci.sh given a deadline file under .tdd/ci-deadline-<sha> that is empty, unreadable or holds a non-numeric word such as now exits 2 naming the file on stderr, rather than reading it as 0 or as a variable (updates the deadline-file rows of the same case) ⟦criterion 3⟧
- [ ] workqueue.sh reads VERI_WORKQUEUE_LOCK_WAIT with leading zeros as decimal: 010 waits ten seconds' worth of lock polls, not eight (updates the leading-zero rows of test_start_done_park_and_assign_take_the_lock_directory_polling_it_for_the_wait_times_20_and_release_it_on_every_path in py/test_workqueue.py) ⟦criterion 1⟧
- [ ] workqueue.sh given a VERI_WORKQUEUE_LOCK_WAIT that is not a non-negative whole number (0.5, abc) exits 2 naming VERI_WORKQUEUE_LOCK_WAIT on stderr for every subcommand that takes the lock, assign included, never writing without the lock and never reporting an unknown subcommand (updates the 0.5 and abc rows of the same case) ⟦criterion 2⟧
- [ ] leaf-timeout.sh reads its baseline, --full seconds and VERI_REFACTOR_BUDGET with leading zeros as decimal: baseline 0200 sizes as two hundred (1200) and 08 as eight, never exiting 1 (updates the leading-zero rows of test_main_reproduces_leaf_timeout_sh_bash_arithmetic_in_stdout_and_return_code in py/test_leaf_timeout.py) ⟦criterion 1⟧
- [ ] leaf-timeout.sh sizes a baseline past 2^63 from its decimal value, never wrapped to a small or negative number (updates the past-2^63 rows of the same case, if any) ⟦criterion 1⟧
- [ ] leaf-timeout.sh given a baseline, --full seconds, VERI_REFACTOR_BUDGET or VERI_TIMEOUT that is not a non-negative whole number exits 2 naming that argument or variable on stderr ⟦criterion 2⟧
- [ ] push-branch.sh reads VERI_PUSH_RETRIES and VERI_PUSH_BACKOFF with leading zeros as decimal: VERI_PUSH_RETRIES=007 makes 7 retries after the first attempt and 08 makes 8, never exiting 1 without recording its push-failed event (updates test_main_keeps_bash_octal_arithmetic_for_leading_zero_tunables in py/test_push_branch.py) ⟦criterion 1⟧
- [ ] push-branch.sh given a VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF that is not a non-negative whole number exits 2 naming that variable on stderr ⟦criterion 2⟧
- [ ] every case the six scripts' bash and pytest suites held before this branch keeps its assertions unchanged, apart from the octal-parity rows the steps above name ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] every case each script's suites already hold passes ⟦full-suite⟧ ⟦criterion 4⟧
