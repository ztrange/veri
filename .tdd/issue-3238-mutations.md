before 40
f70edde5f86b95391604e3f04a65c214b9b7f0aa
keep 60
skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py
command 155
make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_wrong_argument_count_prints_usage_on_stderr_and_exits_2_filing_nothing

file 46
skills/tdd/scripts/veri/refactor_candidates.py
old 18
return 2
    issue
new 18
return 1
    issue
command 155
make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_wrong_argument_count_prints_usage_on_stderr_and_exits_2_filing_nothing

before 40
f70edde5f86b95391604e3f04a65c214b9b7f0aa
keep 60
skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py
command 299
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpja67gw1x/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_never_labels_with_the_opt_in_label_or_ready_for_agent

file 46
skills/tdd/scripts/veri/refactor_candidates.py
old 38
LABELS = ("refactor", "refactor-owed")
new 87
LABELS = ("refactor", "refactor-owed", __import__("os").environ.get("VERI_LABEL", "x"))
command 136
make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_never_labels_with_the_opt_in_label_or_ready_for_agent

before 40
f70edde5f86b95391604e3f04a65c214b9b7f0aa
keep 60
skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py
command 417
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpja67gw1x/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_closed_issue_with_the_same_title_is_not_found_so_a_new_one_is_created_not_edited make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_closed_issue_with_the_same_title_is_not_found_so_a_new_one_is_created_not_edited

file 46
skills/tdd/scripts/veri/refactor_candidates.py
old 17
"--state", "open"
new 16
"--state", "all"
command 165
make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_closed_issue_with_the_same_title_is_not_found_so_a_new_one_is_created_not_edited

before 40
f70edde5f86b95391604e3f04a65c214b9b7f0aa
keep 60
skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py
command 379
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpja67gw1x/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_replace_prints_the_url_github_returned_for_the_existing_issue make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_replace_prints_the_url_github_returned_for_the_existing_issue

file 46
skills/tdd/scripts/veri/refactor_candidates.py
old 51
url = existing[0].get("url") or "/issues/" + number
new 25
url = "/issues/" + number
command 146
make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_replace_prints_the_url_github_returned_for_the_existing_issue

before 40
f70edde5f86b95391604e3f04a65c214b9b7f0aa
keep 60
skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py
command 288
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpja67gw1x/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_github_failure_exits_2_and_files_nothing

file 46
skills/tdd/scripts/veri/refactor_candidates.py
old 122
found = json.loads(github.gh_issue_list("--state", "open", "--search", title + " in:title", "--json", "number,title,url"))
new 10
found = []
command 125
make test TESTS=skills/tdd/scripts/tests/py/unit/test_refactor_candidates.py::test_a_github_failure_exits_2_and_files_nothing

