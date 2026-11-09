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

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 280
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_eta_when_only_the_prd_itself_has_a_lane

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 130
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_eta_when_only_the_prd_itself_has_a_lane

file 27
projects/dashboard/serve.py
old 69
if any(i.get("lane") for i in cache["issues"] if i["state"] == "OPEN"
new 79
if any(i.get("lane") for i in cache["issues"] if i["state"] == "OPEN" and False
command 130
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_eta_when_only_the_prd_itself_has_a_lane

file 27
projects/dashboard/serve.py
old 33
 and i["number"] != prd["number"]
new 0

command 130
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_eta_when_only_the_prd_itself_has_a_lane

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 295
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_eta_when_the_laned_issues_are_closed_or_of_another_prd

file 27
projects/dashboard/serve.py
old 78
for i in cache["issues"] if i["state"] == "OPEN"
               and prd_number
new 62
for i in cache["issues"] if True
               and prd_number
command 145
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_eta_when_the_laned_issues_are_closed_or_of_another_prd

file 27
projects/dashboard/serve.py
old 35
and prd_number(i["title"]) == n and
new 12
and True and
command 145
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_eta_when_the_laned_issues_are_closed_or_of_another_prd

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 325
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_rate_yet_when_closed_issues_outside_the_lanes_or_older_than_7_days_make_up_the_three

file 27
projects/dashboard/serve.py
old 106
i.get("lane") in lanes
                      and datetime.datetime.fromisoformat(i["closedAt"]) >= cutoff]
new 5
True]
command 175
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_no_rate_yet_when_closed_issues_outside_the_lanes_or_older_than_7_days_make_up_the_three

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 323
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_the_eta_range_with_the_longest_open_blocked_by_chain_when_longer_than_the_child_count

file 27
projects/dashboard/serve.py
old 71
longest = max([len(children)] + [chain(c["number"]) for c in children])
new 23
longest = len(children)
command 173
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_shows_the_eta_range_with_the_longest_open_blocked_by_chain_when_longer_than_the_child_count

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 318
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_eta_uses_lower_and_upper_quartile_wall_seconds_not_min_and_max_with_five_closed_issues

file 27
projects/dashboard/serve.py
old 28
walls[(len(walls) - 1) // 4]
new 8
walls[0]
command 168
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_eta_uses_lower_and_upper_quartile_wall_seconds_not_min_and_max_with_five_closed_issues

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 322
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_eta_uses_fastest_lanes_fast_rate_and_slowest_lanes_slow_rate_and_counts_only_open_blockers

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 172
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_eta_uses_fastest_lanes_fast_rate_and_slowest_lanes_slow_rate_and_counts_only_open_blockers

file 27
projects/dashboard/serve.py
old 9
max(fast)
new 9
min(fast)
command 172
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_eta_uses_fastest_lanes_fast_rate_and_slowest_lanes_slow_rate_and_counts_only_open_blockers

file 27
projects/dashboard/serve.py
old 9
min(slow)
new 9
max(slow)
command 172
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_eta_uses_fastest_lanes_fast_rate_and_slowest_lanes_slow_rate_and_counts_only_open_blockers

file 27
projects/dashboard/serve.py
old 17
if b in by_number
new 7
if True
command 172
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_eta_uses_fastest_lanes_fast_rate_and_slowest_lanes_slow_rate_and_counts_only_open_blockers

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 307
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_for_a_stale_owed_leaves_report_owed_json_byte_identical_and_creates_no_file

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 63
make test TESTS=projects/dashboard/tests/test_serve_get_root.py

file 27
projects/dashboard/serve.py
old 41
            return "\n<p>owed: stale</p>"
new 69
            owed_path.write_text("{}"); return "\n<p>owed: stale</p>"
command 157
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_report_page_for_a_stale_owed_leaves_report_owed_json_byte_identical_and_creates_no_file

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 282
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpjqawuzrk/scripts/timed-test-run.sh target projects/dashboard/tests/test_serve_get_root.py make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_serve_answers_report_on_loopback_and_on_no_other_local_address

before 40
9fc78558628ec9cb59f906bd849b37eab658a78a
keep 47
projects/dashboard/tests/test_serve_get_root.py
command 132
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_serve_answers_report_on_loopback_and_on_no_other_local_address

file 27
projects/dashboard/serve.py
old 24
("127.0.0.1", args.port)
new 22
("0.0.0.0", args.port)
command 132
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_serve_answers_report_on_loopback_and_on_no_other_local_address

file 27
projects/dashboard/serve.py
old 22
self.path == "/report"
new 23
self.path == "/reportx"
command 132
make test TESTS=projects/dashboard/tests/test_serve_get_root.py::test_serve_answers_report_on_loopback_and_on_no_other_local_address

