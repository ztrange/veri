before 40
97e8836507b13debb31e120d6aba38fac4a3d9b2
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 279
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpgr2uyn1z/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_orders_blocks_by_prd_number_not_by_issue_number

before 40
97e8836507b13debb31e120d6aba38fac4a3d9b2
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 63
make test TESTS=projects/dashboard/tests/test_serve_get_root.py

file 27
projects/dashboard/serve.py
old 34
for n, i in sorted(first.items()))
new 66
for n, i in sorted(first.items(), key=lambda kv: kv[1]["number"]))
command 63
make test TESTS=projects/dashboard/tests/test_serve_get_root.py

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 299
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_does_not_show_owed_none_when_the_current_entry_has_a_non_zero_count

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 149
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_does_not_show_owed_none_when_the_current_entry_has_a_non_zero_count

file 27
projects/dashboard/serve.py
old 40
if entry["answer"]["count"] == 0 else ""
new 15
if True else ""
command 149
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_does_not_show_owed_none_when_the_current_entry_has_a_non_zero_count

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 126
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_left_line_ignores_closed_children_of_the_prd

file 27
projects/dashboard/serve.py
old 62
children = [i for i in cache["issues"] if i["state"] == "OPEN"
new 46
children = [i for i in cache["issues"] if True
command 126
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_left_line_ignores_closed_children_of_the_prd

