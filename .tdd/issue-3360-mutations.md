file 35
skills/tdd/scripts/veri/dispatch.py
old 102
os.path.getmtime(f)
                    for f in (events, log, *glob.glob(os.path.join(tdd, "*.out")))
new 110
os.path.getmtime(f) + 10**9
                    for f in (events, log, *glob.glob(os.path.join(tdd, "*.out")))
command 208
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_stalled_and_exits_0_when_the_events_conductor_log_and_detached_command_output_are_all_older_than_the_stall_window_issue_3360

