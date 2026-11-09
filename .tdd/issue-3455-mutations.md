file 34
skills/tdd/scripts/veri/wait_ci.py
old 99
        if now >= slice_end:
            break
        subprocess.run(["sleep", poll])
    return 3
new 79
        warn("no CI run for %s" % (want or head))
        return 2
    return 3
context 28
        if now >= slice_end:
command 186
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_ends_its_slice_with_3_naming_no_missing_run_while_a_ready_heads_state_has_been_none_under_the_grace_issue_3455

file 34
skills/tdd/scripts/veri/wait_ci.py
old 29
    return "green", "", False
new 28
    return "none", "", False
context 29
    return "green", "", False
command 190
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_keeps_waiting_past_the_no_run_grace_and_exits_0_when_a_none_heads_check_run_appears_and_completes_green_issue_3455

