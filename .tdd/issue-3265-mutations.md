file 8
Makefile
old 37
skills/tdd/scripts/tests/py,test_%.py
new 28
projects/dashboard,test_%.py
command 69
make test TESTS=projects/dashboard/tests/test_veri_make_test_scope.py

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 321
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 304
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals

file 27
projects/dashboard/serve.py
old 28
sorted(runs.glob("*.jsonl"))
new 38
reversed(sorted(runs.glob("*.jsonl")))
command 154
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals

file 27
projects/dashboard/serve.py
old 13
if l.strip()]
new 1
]
command 154
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals

file 27
projects/dashboard/serve.py
old 17
if not events or 
new 3
if 
command 154
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 310
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_bail_or_merged_ending_event

file 27
projects/dashboard/serve.py
old 62
if not events or any(e.get("event") in ENDING for e in events)
new 13
if not events
command 160
make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_bail_or_merged_ending_event

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 300
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_done_ending_event

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 283
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_done_ending_event

file 27
projects/dashboard/serve.py
old 45
any(e.get("event") in ENDING for e in events)
new 5
False
command 133
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_done_ending_event

