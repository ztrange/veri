# Mutation-parity pairs proven for #1346

Every row below is `proven` by the conductor's own `mutation-parity.sh` run, each mutation in `skills/tdd/scripts/veri/affected_suites.py`.

## Step 1 — rules 5–6, fail-closed widening and its stderr, run state

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| rule 5: a diff touching only files rules 1–4 match never falls back to the full suite | `test_rule_5_a_diff_touching_only_files_rules_1_to_4_match_never_falls_back_to_the_full_suite` | widening fires whenever anything is placed (`if unplaced or placed:`) | proven |
| rule 6: a change to the prompt prompts/develop-red.md prints every suite that names it, and no others | `test_rule_6_a_change_to_the_prompt_prompts_develop_red_md_prints_every_suite_that_names_it_and_no_others` | a prompt maps to every suite instead of the suites naming it | proven |
| rule 6: a prompt and a suite in one range print that suite and the prompt's suites, without widening | `test_rule_6_a_prompt_and_a_suite_in_one_range_print_that_suite_and_the_prompts_suites_without_widening` | a changed prompt is unplaced, so it widens | proven |
| fail-closed: a range whose only changed file matches no rule prints every suite | `test_main_widens_to_every_suite_file_but_not_a_directory_named_like_one` | widening dropped: an unplaced file leaves the placed list as it is | proven |
| a widened answer names on stderr the file that forced the widening | `test_main_widens_to_every_suite_file_but_not_a_directory_named_like_one` | the widening stderr line names no file | proven |
| run state: a .tdd/ ledger alongside a script change prints exactly that script's suite | `test_run_state_a_tdd_ledger_alongside_a_script_change_prints_exactly_that_scripts_suite` | a `.tdd/` file is unplaced, so it widens | proven |
| run state alone → exit 3 and prints nothing | `test_run_state_alone_exits_3_and_prints_nothing` | nothing placed returns 0 instead of 3 | proven |
| fail-closed: run state alongside a file no rule places still prints every suite | `test_fail_closed_run_state_alongside_a_file_no_rule_places_still_prints_every_suite` | widening skipped when the range also touches `.tdd/` | proven |
| a widening caused by two unplaced files names both on stderr | `test_a_widening_caused_by_two_unplaced_files_names_both_on_stderr` | the widening stderr line names only the first unplaced file | proven |
| a green commit's shape — ledger, refactor-owed file and a source change — prints exactly that script's suite | `test_a_green_commits_shape_ledger_refactor_owed_file_and_a_source_change_prints_exactly_that_scripts_suite` | only `.tdd/issue-<n>.md` is run state; the refactor-owed file is unplaced | proven |
