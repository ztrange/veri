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

