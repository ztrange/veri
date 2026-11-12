file 8
Makefile
old 37
skills/tdd/scripts/tests/py,test_%.py
new 28
projects/dashboard,test_%.py
command 69
make test TESTS=projects/dashboard/tests/test_veri_make_test_scope.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 321
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 304
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 28
sorted(runs.glob("*.jsonl"))
new 38
reversed(sorted(runs.glob("*.jsonl")))
command 154
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 13
if l.strip()]
new 1
]
command 154
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 17
if not events or 
new 3
if 
command 154
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_lists_running_runs_in_sorted_order_skipping_blank_lines_and_empty_journals
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 310
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_bail_or_merged_ending_event
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 62
if not events or any(e.get("event") in ENDING for e in events)
new 13
if not events
command 160
make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_bail_or_merged_ending_event
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 300
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make -C projects/dashboard test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_done_ending_event
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
ce97239c8367c40279c8a815989f7b70641a23f3
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 283
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpqfh3702t/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_done_ending_event
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 45
any(e.get("event") in ENDING for e in events)
new 5
False
command 133
python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_page_leaves_out_runs_whose_journal_has_a_done_ending_event
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 304
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_open_page_script_rerenders_freshly_fetched_running_data_into_the_page_without_reload
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 309
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py python3 -m pytest -q projects/dashboard/tests/test_serve_get_root.py::test_open_page_script_rerenders_freshly_fetched_running_data_into_the_page_without_reload
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 323
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py sh -c 'cd projects/dashboard && python3 -m pytest -q tests/test_serve_get_root.py::test_open_page_script_rerenders_freshly_fetched_running_data_into_the_page_without_reload'
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 49
document.getElementById("running").innerHTML = t;
new 7
void t;
command 173
sh -c 'cd projects/dashboard && python3 -m pytest -q tests/test_serve_get_root.py::test_open_page_script_rerenders_freshly_fetched_running_data_into_the_page_without_reload'
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 301
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_page_script_fetches_a_data_only_endpoint_holding_running_lines_and_no_page_markup
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 320
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py sh -c 'cd projects/dashboard && python3 -m pytest -q tests/test_serve_get_root.py::test_page_script_fetches_a_data_only_endpoint_holding_running_lines_and_no_page_markup'
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 27
if self.path == "/running":
new 9
if False:
command 170
sh -c 'cd projects/dashboard && python3 -m pytest -q tests/test_serve_get_root.py::test_page_script_fetches_a_data_only_endpoint_holding_running_lines_and_no_page_markup'
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 8
Makefile
old 38
if [ -n "$(DASH_TESTS)" ]; then printf
new 20
if true; then printf
command 170
make test TESTS=skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3265_a_plain_make_test_collects_no_dashboard_case_and_never_calls_the_dashboard_runner
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 8
Makefile
old 38
if [ -n "$(DASH_TESTS)" ]; then printf
new 20
if true; then printf
command 237
/Users/marioferreira/.veri-tools/venv/bin/python3 -m pytest -q -p no:cacheprovider skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py::test_3265_a_plain_make_test_collects_no_dashboard_case_and_never_calls_the_dashboard_runner
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 51
projects/dashboard/tests/test_serve_source_reads.py
command 221
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_source_reads.py make test TESTS=projects/dashboard/tests/test_serve_source_reads.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 7
import 
new 19
import subprocess, 
command 72
python3 -m pytest -q projects/dashboard/tests/test_serve_source_reads.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 52
projects/dashboard/tests/test_serve_source_writes.py
command 68
make test TESTS=projects/dashboard/tests/test_serve_source_writes.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 52
projects/dashboard/tests/test_serve_source_writes.py
command 73
python3 -m pytest -q projects/dashboard/tests/test_serve_source_writes.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 22
self.wfile.write(body)
new 18
open("/tmp/x","w")
command 73
python3 -m pytest -q projects/dashboard/tests/test_serve_source_writes.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 55
projects/dashboard/tests/test_serve_source_processes.py
command 266
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_source_processes.py make test TESTS=projects/dashboard/tests/test_serve_source_processes.py::test_serve_source_starts_no_process
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 55
projects/dashboard/tests/test_serve_source_processes.py
command 231
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_source_processes.py python3 -m pytest projects/dashboard/tests/test_serve_source_processes.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 7
import 
new 19
import subprocess, 
command 73
python3 -m pytest projects/dashboard/tests/test_serve_source_processes.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 52
projects/dashboard/tests/test_serve_source_skills.py
command 226
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_source_skills.py make -C projects/dashboard test TESTS=tests/test_serve_source_skills.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 52
projects/dashboard/tests/test_serve_source_skills.py
command 111
bash -c 'cd projects/dashboard && env -u PYTEST_PLUGINS python3 -m pytest -q tests/test_serve_source_skills.py'
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 15
import argparse
new 38
import argparse
from skills.x import y
command 111
bash -c 'cd projects/dashboard && env -u PYTEST_PLUGINS python3 -m pytest -q tests/test_serve_source_skills.py'
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 27
projects/dashboard/serve.py
old 15
import argparse
new 53
import argparse, sys
sys.path.insert(0, 'skills/tdd')
command 111
bash -c 'cd projects/dashboard && env -u PYTEST_PLUGINS python3 -m pytest -q tests/test_serve_source_skills.py'
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

before 40
36eda2d95c8d40f5a12604d5b57dd423e63b8943
keep 53
projects/dashboard/tests/test_veri_make_test_scope.py
command 225
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmp2ddnc37g/scripts/timed-test-run.sh target projects/dashboard/tests/test_veri_make_test_scope.py make test TESTS=projects/dashboard/tests/test_veri_make_test_scope.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

file 8
Makefile
old 113
py_tests = $(if $(1),$(foreach t,$(2),$(if $(findstring .py,$(t)),$(if $(filter $(DASH_PATH),$(t)),,$(t)))),$(3))
new 126
py_tests = $(if $(1),$(foreach t,$(2),$(if $(findstring .py,$(t)),$(t))),$(3))  $(wildcard projects/dashboard/tests/test_*.py)
command 74
python3 -m pytest -q projects/dashboard/tests/test_veri_make_test_scope.py
retired 56
mutated file deleted by bc96a54094 (dashboard left veri)

