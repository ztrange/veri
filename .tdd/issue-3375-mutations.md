before 40
6642f10fa1aeda8789f94871b2ddbe55bf2633b9
keep 44
skills/tdd/scripts/tests/py/test_stop_run.py
command 205
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_leaves_waits_the_kill_grace_the_env_names_between_the_term_and_the_kill_of_a_detached_group_and_by_default_waits_a_positive_time

file 35
skills/tdd/scripts/veri/stop_run.py
old 32
os.killpg(group, signal.SIGKILL)
new 4
pass
command 205
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_leaves_waits_the_kill_grace_the_env_names_between_the_term_and_the_kill_of_a_detached_group_and_by_default_waits_a_positive_time

file 35
skills/tdd/scripts/veri/stop_run.py
old 6
or "5"
new 6
or "0"
command 205
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_leaves_waits_the_kill_grace_the_env_names_between_the_term_and_the_kill_of_a_detached_group_and_by_default_waits_a_positive_time

before 40
6642f10fa1aeda8789f94871b2ddbe55bf2633b9
keep 44
skills/tdd/scripts/tests/py/test_stop_run.py
command 184
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_main_now_terms_only_pids_whose_ps_runs_supervise_sh_of_their_name_ignoring_kill_errors_and_other_modes_signal_nothing

before 40
00b3f00cc59b93ff8aa2d80ecbcf8ed98f031f6b
keep 44
skills/tdd/scripts/tests/py/test_stop_run.py
command 203
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_run_cli_mode_now_exits_0_when_the_detached_group_leader_sent_kill_is_an_unreaped_zombie_and_2_when_a_live_member_survives_kill

file 35
skills/tdd/scripts/veri/stop_run.py
old 55
if (pid_file._ps("stat", group) or "").startswith("Z"):
new 9
if False:
context 59
    if (pid_file._ps("stat", group) or "").startswith("Z"):
command 203
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_run_cli_mode_now_exits_0_when_the_detached_group_leader_sent_kill_is_an_unreaped_zombie_and_2_when_a_live_member_survives_kill

file 35
skills/tdd/scripts/veri/stop_run.py
old 19
for _ in range(10):
new 18
for _ in range(1):
context 23
    for _ in range(10):
command 166
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_run_cli_mode_now_exits_0_when_a_member_of_the_detached_group_dies_a_moment_after_the_kill

file 35
skills/tdd/scripts/veri/stop_run.py
old 19
for _ in range(10):
new 18
for _ in range(1):
context 23
    for _ in range(10):
command 199
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_run_mode_now_exits_0_when_a_member_of_the_detached_group_is_alive_at_the_first_probes_after_kill_and_gone_at_a_later_probe

before 40
37749e585077f15c814b0a5e8ae7e4ce736ce89d
keep 44
skills/tdd/scripts/tests/py/test_stop_run.py
command 199
make test TESTS=skills/tdd/scripts/tests/py/test_stop_run.py::test_3375_stop_run_mode_now_exits_0_when_a_member_of_the_detached_group_is_alive_at_the_first_probes_after_kill_and_gone_at_a_later_probe

