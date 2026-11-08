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

before 40
d8c8d1eae1f096c0f1ca7a4ac644422c74562c5d
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 329
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp45ouhdpo/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_dispatch.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_nothing_and_takes_the_slot_decision_again_when_a_running_queued_merge_ends_with_the_pr_merged

file 35
skills/tdd/scripts/veri/dispatch.py
old 32
and pr_state(pr_url) != "MERGED"
new 32
and pr_state(pr_url) == "MERGED"
command 177
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_nothing_and_takes_the_slot_decision_again_when_a_running_queued_merge_ends_with_the_pr_merged

before 40
d8c8d1eae1f096c0f1ca7a4ac644422c74562c5d
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 328
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp45ouhdpo/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_dispatch.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_the_stall_window_unset_reports_a_conductor_silent_for_3600_seconds_but_not_one_silent_for_3599

file 35
skills/tdd/scripts/veri/dispatch.py
old 29
"VERI_DISPATCH_STALL", "3600"
new 29
"VERI_DISPATCH_STALL", "3599"
command 176
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_the_stall_window_unset_reports_a_conductor_silent_for_3600_seconds_but_not_one_silent_for_3599

file 35
skills/tdd/scripts/veri/dispatch.py
old 29
"VERI_DISPATCH_STALL", "3600"
new 29
"VERI_DISPATCH_STALL", "3601"
command 176
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_the_stall_window_unset_reports_a_conductor_silent_for_3600_seconds_but_not_one_silent_for_3599

