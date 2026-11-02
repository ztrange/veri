file 41
skills/tdd/scripts/veri/detach_command.py
old 28
    print(code)
    return 1
new 28
    print(code)
    return 0
command 203
make test TESTS=skills/tdd/scripts/tests/py/test_detach_command_process.py::test_wait_alone_on_a_red_command_whose_named_file_is_still_red_alone_exits_1_with_the_code_and_writes_no_suite_flake_event_2912

file 41
skills/tdd/scripts/veri/detach_command.py
old 55
rerun_alone.main([alone, exit_file[:-5] + ".out"]) == 0
new 4
True
command 171
make test TESTS=skills/tdd/scripts/tests/py/unit/test_detach_command.py::test_wait_alone_reruns_through_the_shared_rerun_alone_helper_so_breaking_it_turns_a_flake_red_2912

