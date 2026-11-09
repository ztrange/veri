file 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
old 41
if list(argv) == ["ps", "-axo", "args="]:
new 9
if False:
command 146
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_without_a_queued_merges_fake_fails_naming_the_unfaked_call_issue_3435

file 35
skills/tdd/scripts/veri/dispatch.py
old 33
        running = queued_merges()
new 74
        running = queued_merges(); subprocess.run(["ps", "-axo", "args="])
command 161
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_with_a_queued_merges_fake_runs_under_the_guard_and_reaches_the_faked_wait_issue_3435

