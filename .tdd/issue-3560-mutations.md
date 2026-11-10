file 35
skills/tdd/scripts/veri/dispatch.py
old 59
sys.stderr.write(str(failure))
                    return 2
new 59
sys.stderr.write(str(failure))
                    return 0
context 50
                    sys.stderr.write(str(failure))
command 163
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_exits_2_naming_the_diff_read_when_gh_pr_diff_answers_http_500_on_every_read_issue_3560

