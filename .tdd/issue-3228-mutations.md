before 40
d8c8d1eae1f096c0f1ca7a4ac644422c74562c5d
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 333
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp45ouhdpo/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_dispatch.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_appends_one_launched_line_with_the_local_iso_time_to_dispatch_log_under_the_main_working_tree_per_launch

file 35
skills/tdd/scripts/veri/dispatch.py
old 43
log.write(f"launched {previous} {now()}\n")
new 13
log.write("")
command 181
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_appends_one_launched_line_with_the_local_iso_time_to_dispatch_log_under_the_main_working_tree_per_launch

before 40
d8c8d1eae1f096c0f1ca7a4ac644422c74562c5d
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 330
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp45ouhdpo/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_dispatch.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_nothing_while_a_queued_merge_is_still_listed_on_the_next_pass_even_though_the_pr_is_not_merged

file 35
skills/tdd/scripts/veri/dispatch.py
old 37
if pr_url not in running and pr_state
new 11
if pr_state
command 178
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_nothing_while_a_queued_merge_is_still_listed_on_the_next_pass_even_though_the_pr_is_not_merged

