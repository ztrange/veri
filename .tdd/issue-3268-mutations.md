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

