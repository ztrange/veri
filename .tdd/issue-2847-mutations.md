before 40
de8ca54d89e58ab697386a6bbdef0a1320355929
keep 49
skills/tdd/scripts/tests/py/unit/test_tunables.py
command 131
make test TESTS=skills/tdd/scripts/tests/py/unit/test_tunables.py::test_2847_baseline_full_tier_unset_resolves_to_run_with_no_error

before 40
de8ca54d89e58ab697386a6bbdef0a1320355929
keep 49
skills/tdd/scripts/tests/py/unit/test_tunables.py
command 292
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpjulzmupo/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_tunables.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_tunables.py::test_2847_baseline_full_tier_set_to_reuse_resolves_to_reuse_with_no_error

file 41
skills/tdd/scripts/veri/full_tier_time.py
old 16
    if not argv:
new 13
    if False:
command 150
make test TESTS=skills/tdd/scripts/tests/py/unit/test_full_tier_time.py::test_main_called_with_no_argument_prints_the_usage_line_to_stderr_and_exits_2

before 40
49ff82c603ebfa2b34700864b787bce795fcd416
keep 55
skills/tdd/scripts/tests/py/unit/test_full_tier_time.py
command 325
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpeho1hzmb/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_full_tier_time.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_full_tier_time.py::test_main_asked_for_a_command_when_the_record_file_is_not_parseable_exits_2_with_a_stderr_line

file 41
skills/tdd/scripts/veri/full_tier_time.py
old 30
if not os.path.exists(RECORD):
new 72
if not os.path.exists(RECORD) or open(RECORD).read().startswith("{not"):
command 167
make test TESTS=skills/tdd/scripts/tests/py/unit/test_full_tier_time.py::test_main_asked_for_a_command_when_the_record_file_is_not_parseable_exits_2_with_a_stderr_line

before 40
49ff82c603ebfa2b34700864b787bce795fcd416
keep 55
skills/tdd/scripts/tests/py/unit/test_full_tier_time.py
command 332
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpeho1hzmb/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_full_tier_time.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_full_tier_time.py::test_main_asked_to_record_non_ascii_digit_seconds_prints_the_usage_line_and_exits_2_recording_nothing

file 41
skills/tdd/scripts/veri/full_tier_time.py
old 25
not argv[1].isascii() or 
new 0

command 174
make test TESTS=skills/tdd/scripts/tests/py/unit/test_full_tier_time.py::test_main_asked_to_record_non_ascii_digit_seconds_prints_the_usage_line_and_exits_2_recording_nothing

before 40
49ff82c603ebfa2b34700864b787bce795fcd416
keep 58
skills/tdd/scripts/tests/py/test_full_tier_time_process.py
command 337
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpeho1hzmb/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_full_tier_time_process.py make test TESTS=skills/tdd/scripts/tests/py/test_full_tier_time_process.py::test_record_from_a_subdirectory_of_the_main_tree_reads_back_from_a_subdirectory_of_a_linked_worktree

before 40
49ff82c603ebfa2b34700864b787bce795fcd416
keep 69
skills/tdd/scripts/tests/py/unit/test_preflight_baseline_full_tier.py
command 257
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpeho1hzmb/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_preflight_baseline_full_tier.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_preflight_baseline_full_tier.py

before 40
49ff82c603ebfa2b34700864b787bce795fcd416
keep 69
skills/tdd/scripts/tests/py/unit/test_preflight_baseline_full_tier.py
command 362
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp712mimd5/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_preflight_baseline_full_tier.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_preflight_baseline_full_tier.py::test_2847_skill_draft_pr_step_names_full_tier_time_sh_as_where_a_green_branch_full_run_records_its_time

