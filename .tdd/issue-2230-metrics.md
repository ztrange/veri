### 📊 Metrics — issue 2230

Wall time for the issue: 5338 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2263.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.03 over 66 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89190 |
| 2 | $0.03 | 90157 |
| 3 | $0.03 | 92099 |
| 4 | $0.02 | 92377 |
| 5 | $0.02 | 92823 |
| 6 | $0.02 | 93180 |
| 7 | $0.02 | 93538 |
| 8 | $0.02 | 93828 |
| 9 | $0.03 | 94632 |
| 10 | $0.03 | 95457 |
| 11 | $0.03 | 97012 |
| 12 | $0.04 | 99812 |
| 13 | $0.05 | 103376 |
| 14 | $0.05 | 106958 |
| 15 | $0.04 | 109164 |
| 16 | $0.04 | 110840 |
| 17 | $0.06 | 115767 |
| 18 | $0.03 | 116177 |
| 19 | $0.03 | 116963 |
| 20 | $0.03 | 117514 |
| 21 | $0.03 | 118298 |
| 22 | $0.12 | 130463 |
| 23 | $0.03 | 131495 |
| 24 | $0.03 | 132568 |
| 25 | $0.04 | 134405 |
| 26 | $0.04 | 135605 |
| 27 | $0.03 | 136427 |
| 28 | $0.03 | 137192 |
| 29 | $0.03 | 137560 |
| 30 | $0.03 | 138439 |
| 31 | $0.04 | 139882 |
| 32 | $0.04 | 140994 |
| 33 | $0.04 | 142200 |
| 34 | $0.03 | 142955 |
| 35 | $0.04 | 143953 |
| 36 | $0.04 | 144841 |
| 37 | $0.05 | 147344 |
| 38 | $0.04 | 148062 |
| 39 | $0.04 | 148755 |
| 40 | $0.04 | 150179 |
| 41 | $0.03 | 150547 |
| 42 | $0.04 | 151215 |
| 43 | $0.04 | 152427 |
| 44 | $0.03 | 152822 |
| 45 | $0.04 | 154404 |
| 46 | $0.04 | 155737 |
| 47 | $0.04 | 156843 |
| 48 | $0.03 | 157292 |
| 49 | $0.04 | 158346 |
| 50 | $0.04 | 159337 |
| 51 | $0.04 | 160071 |
| 52 | $0.04 | 161127 |
| 53 | $0.04 | 161621 |
| 54 | $0.04 | 161967 |
| 55 | $0.05 | 164394 |
| 56 | $0.04 | 165528 |
| 57 | $0.04 | 165778 |
| 58 | $0.04 | 166842 |
| 59 | $0.04 | 167885 |
| 60 | $0.04 | 168579 |
| 61 | $0.05 | 170473 |
| 62 | $0.04 | 170778 |
| 63 | $0.04 | 171222 |
| 64 | $0.04 | 171770 |
| 65 | $0.04 | 172114 |
| 66 | $0.04 | 172702 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1011 | 0 | 30524 | 0.09 |
| red | 6 | 3 | 0 | 0 | 283 | 137 | 38 | 76 | 16432 | 1194390 | 178536 | 0.73 |
| green | 6 | 3 | 0 | 0 | 2889 | 224 | 83 | 160 | 25120 | 3058582 | 243898 | 1.17 |
| refactor | 6 | 3 | 0 | 0 | 270 | 35 | 16 | 32 | 3140 | 384359 | 101079 | 0.32 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 1465 | 118 | 39 | 76 | 12201 | 890413 | 283203 | 0.92 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 1989 | 287 | 99 | 194 | 33502 | 3746918 | 270834 | 1.39 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tests-frozen.sh check-earlier's exit-0 pass marker names the state it checked, uncommitted work-tree changes included (it keeps its `step:` and `head:` lines and adds a line naming a hash of the work tree, tracked and untracked files alike, with run state under `.tdd/` left out), so a work-tree edit between two passing check-earlier runs gives two different markers and no edit gives the same one; pinned by a process case (a real git repository under tmp_path) in skills/tdd/scripts/tests/py/test_tests_frozen_process.py ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 78 | 26 | 52 | 8297 | 725040 | 111738 | 0.43 | 489 | unknown | 0/5 | nothing-left |  |  | full |
| supervise.sh refuses a verify-red or verify-green launch, exit 2 and no leaf started, when the step's pass marker names a state other than the current one, and launches it when the marker names the current state; pinned by cases in a new file skills/tdd/scripts/tests/py/test_check_earlier_state_gate_process.py (a real git repository under tmp_path, check-earlier run then supervise driven in-process with the leaf's start spied): a marker written before a work-tree edit → exit 2 and no leaf; a marker for the current state → launch; the older cases' hand-written markers in test_supervise.py are brought to the new marker's form ⟦guard-subject: skills/tdd/scripts/tests/py/test_supervise.py⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 159 | 57 | 108 | 18283 | 2127813 | 141364 | 0.75 | 916 | unknown | 0/5 | nothing-left |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_verify.py — FAILED test_verify_sh_refuses_a_verifier_leaf_that_changed_the_tree_or_head_with_exit_2_naming_it_and_restores_what_it_was_handed (also test_verify_sh_saves_the_same_refusal_diff_whatever_the_global_git_config_says_1846 and test_verify_sh_under_the_repos_own_gitignore_accepts_nested_run_state_and_refuses_an_edited_root_ledger_or_tracked_path_naming_each_569): verify.sh exits 0 where 2 was wanted on a verifier that changed the tree; skills/tdd/scripts/tests/py/test_skill_leaf_env.py — FAILED test_every_leaf_skill_md_launches_leaves_events_carrying_the_runs_issue_and_step (also test_every_leaf_skill_md_launches_with_veri_step_set_sees_the_runs_step_as_veri_step and test_every_verifier_skill_md_launches_through_verify_sh_sees_the_runs_test_command_as_veri_test_cmd): the SKILL.md verify-red/verify-green launches start no leaf; skills/tdd/scripts/tests/py/test_verdict_chain.py — FAILED test_1463_wait_leaf_returns_the_verdict_the_stub_verifier_gave_through_the_real_chain - assert (2, False) == (0, True) ⟦suite-repair⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 159 | 54 | 108 | 18112 | 1784478 | 270411 | 1.04 | 2759 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests-frozen.sh check-earlier's exit-0 pass marker names the state it checked, uncommitted work-tree changes included (it keeps its `step:` and `head:` lines and adds a line naming a hash of the work tree, tracked and untracked files alike, with run state under `.tdd/` left out), so a work-tree edit between two passing check-earlier runs gives two different markers and no edit gives the same one; pinned by a process case (a real git repository under tmp_path) in skills/tdd/scripts/tests/py/test_tests_frozen_process.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 67 | 0.09 |
| supervise.sh refuses a verify-red or verify-green launch, exit 2 and no leaf started, when the step's pass marker names a state other than the current one, and launches it when the marker names the current state; pinned by cases in a new file skills/tdd/scripts/tests/py/test_check_earlier_state_gate_process.py (a real git repository under tmp_path, check-earlier run then supervise driven in-process with the leaf's start spied): a marker written before a work-tree edit → exit 2 and no leaf; a marker for the current state → launch; the older cases' hand-written markers in test_supervise.py are brought to the new marker's form ⟦guard-subject: skills/tdd/scripts/tests/py/test_supervise.py⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 49 | 0.09 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_verify.py — FAILED test_verify_sh_refuses_a_verifier_leaf_that_changed_the_tree_or_head_with_exit_2_naming_it_and_restores_what_it_was_handed (also test_verify_sh_saves_the_same_refusal_diff_whatever_the_global_git_config_says_1846 and test_verify_sh_under_the_repos_own_gitignore_accepts_nested_run_state_and_refuses_an_edited_root_ledger_or_tracked_path_naming_each_569): verify.sh exits 0 where 2 was wanted on a verifier that changed the tree; skills/tdd/scripts/tests/py/test_skill_leaf_env.py — FAILED test_every_leaf_skill_md_launches_leaves_events_carrying_the_runs_issue_and_step (also test_every_leaf_skill_md_launches_with_veri_step_set_sees_the_runs_step_as_veri_step and test_every_verifier_skill_md_launches_through_verify_sh_sees_the_runs_test_command_as_veri_test_cmd): the SKILL.md verify-red/verify-green launches start no leaf; skills/tdd/scripts/tests/py/test_verdict_chain.py — FAILED test_1463_wait_leaf_returns_the_verdict_the_stub_verifier_gave_through_the_real_chain - assert (2, False) == (0, True) ⟦suite-repair⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 154 | 0.15 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 19 | 13 | 35 | 31 | 39 | 26 | 10 | 12 | 10 | 1 | 94 | 16 | 11 | 11 | 24 | 100 | 104 | 117 |
| fast | 27 | 26 | 19 | 20 | 78 | 15 | 16 | 15 | 16 |  |  |  |  |  |  |  |  |  |
| target | 10 | 4 | 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 138 | 270 | 45703 | 4637331 | 554037 | 2.31 |
