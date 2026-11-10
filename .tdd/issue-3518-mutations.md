file 35
skills/tdd/scripts/veri/dispatch.py
old 41
if i not in live and restart_pending(i)})
new 23
if restart_pending(i)})
context 57
                if i not in live and restart_pending(i)})
command 193
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_exactly_one_at_target_3_beside_a_live_run_with_a_leftover_marker_and_a_never_seen_restarting_run_issue_3495

file 35
skills/tdd/scripts/veri/dispatch.py
old 39
held = len(live) + len(set(pending) | {
new 39
held = len(live) + len(pending) + len({
context 51
            held = len(live) + len(set(pending) | {
command 193
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_exactly_one_at_target_3_beside_a_live_run_with_a_leftover_marker_and_a_never_seen_restarting_run_issue_3495

file 35
skills/tdd/scripts/veri/dispatch.py
old 41
if i not in live and restart_pending(i)})
new 23
if restart_pending(i)})
context 57
                if i not in live and restart_pending(i)})
command 193
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_exactly_one_at_target_3_beside_a_live_run_with_a_leftover_marker_and_a_never_seen_restarting_run_issue_3495

file 35
skills/tdd/scripts/veri/dispatch.py
old 39
held = len(live) + len(set(pending) | {
new 39
held = len(live) + len(pending) + len({
context 51
            held = len(live) + len(set(pending) | {
command 193
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_exactly_one_at_target_3_beside_a_live_run_with_a_leftover_marker_and_a_never_seen_restarting_run_issue_3495

