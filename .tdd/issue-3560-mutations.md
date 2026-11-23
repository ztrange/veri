file 37
skills/tdd/scripts/veri/watch_runs.py
old 59
sys.stderr.write(str(failure))
                    return 2
new 59
sys.stderr.write(str(failure))
                    return 0
context 50
                    sys.stderr.write(str(failure))
command 160
make test TESTS=skills/tdd/scripts/tests/py/unit/test_watch_runs.py::test_main_with_target_exits_2_and_passes_on_stderr_when_solvable_issues_exits_non_zero_1930

file 35
skills/tdd/scripts/veri/dispatch.py
old 74
    try:
        return read(*args)
    except github.NoAnswer as failure:
new 154
    try:
        try:
            return read(*args)
        except github.NoAnswer:
            return read(*args)
    except github.NoAnswer as failure:
context 8
    try:
command 164
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_exits_2_naming_the_diff_read_after_one_read_when_gh_pr_diff_answers_http_404_issue_3560

before 40
18d5d2c05e6824522de639f4f8e3b0225c4db3e6
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 167
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_sleeps_the_vari_dispatch_retry_sleep_seconds_once_per_failed_http_500_diff_read_issue_3560

before 40
7bd8769b48aff1c00f0a6c5ba87bd3cb973308ab
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 183
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_goes_on_to_launch_when_the_open_pr_list_read_answers_http_500_for_the_first_reads_then_succeeds_issue_3560

before 40
7bd8769b48aff1c00f0a6c5ba87bd3cb973308ab
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 181
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_goes_on_to_launch_when_the_issue_body_read_answers_http_500_for_the_first_reads_then_succeeds_issue_3560

