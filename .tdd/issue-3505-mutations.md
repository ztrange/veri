file 39
skills/tdd/scripts/veri/tests_frozen.py
old 12
"--reverse",
new 0

context 78
        revs = _git_out("log", "--reverse", "--format=%H", "--", path).split()
command 196
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_earlier_derives_the_step_base_from_its_own_commits_when_an_earlier_plan_commit_introduced_the_step_line_3468

