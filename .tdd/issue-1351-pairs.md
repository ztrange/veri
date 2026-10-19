# Mutation-parity pairs proven for #1351

Every row is the conductor's own `mutation-parity.sh` run, on a scratch tree at the step's base (the bash cases still present) plus its new pytest cases.

## Step 1 — run-affordable.test.sh (6/6 proven, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| a projection over VERI_RUN_BUDGET exits 1 printing spent, steps remaining, median and projection | `test_main_passes_the_exit_statuses_of_the_budget_and_the_log_through` | the over-budget branch returns 0 instead of 1 | proven |
| a projection within VERI_RUN_BUDGET exits 0 printing nothing | `test_main_passes_the_exit_statuses_of_the_budget_and_the_log_through` | the within-budget early `return 0` is removed (`if False:`), so a projection under the ceiling prints and exits 1 | proven |
| no completed full step, only pins or no usage at all, exits 3 printing nothing | `test_a_log_with_only_pins_or_no_usage_at_all_exits_3_printing_nothing` | no completed full step returns 0 instead of 3 | proven |
| run-affordable.sh two exits 2 with nothing on stdout and the refusal then the usage line on stderr | `test_main_refuses_a_bad_argument_with_2_and_answers_1_or_3_from_the_siblings` | the refusal drops the usage line from stderr | proven |
| run through a symlink to the skill directory from another working directory, it answers as in place and reads that directory's event log | `test_run_from_another_working_directory_it_answers_from_that_directorys_event_log` | `step_cost.logical_cwd()` returns the module directory instead of the working directory | proven |
| #818: step-cost.sh failing with 1 on an event log holding a non-UTF-8 byte exits 2 printing nothing | `test_an_event_log_step_cost_cannot_decode_exits_2_printing_nothing` | step_cost.py reads the log with `errors="replace"`, so a non-UTF-8 byte no longer fails | proven |

## Step 2 — step-budget.test.sh (3/3 proven, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| neither budget set prints 12 then 120, each on its own line, exit 0 | `test_cli_with_neither_budget_set_prints_12_then_120_each_on_its_own_line_and_exits_0` | the step budget default is 13 instead of 12 | proven |
| an argument exits 2 with nothing on stdout and the usage line alone on stderr | `test_cli_with_an_argument_exits_2_with_nothing_on_stdout_and_the_usage_line_alone_on_stderr` | the argument refusal is removed (`if False:`), so an argument is ignored | proven |
| step-budget.sh run through a symlink to the skill directory and from another working directory answers no argument, VERI_STEP_BUDGET=twelve and the argument 0 as it does in place | `test_cli_from_another_working_directory_answers_no_argument_a_bad_step_budget_and_the_argument_0` | the module refuses when its working directory is named `elsewhere` | proven |

## Step 3 — step-cost.test.sh (4/4 proven, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| a step's usage events are summed to two decimals, exit 0 | `test_cli_sums_a_steps_usage_events_to_two_decimals_and_exits_0` | the sum is formatted to one decimal instead of two | proven |
| a step no usage event carries prints nothing, exit 3 | `test_cli_for_a_step_no_usage_event_carries_prints_nothing_and_exits_3` | a step no usage event carries returns 0 instead of 3 | proven |
| no argument, an unknown option, --run or --steps with a step text, and a missing log each exit 2 with stderr only | `test_cli_exits_2_with_stderr_only_for_no_argument_an_unknown_option_run_or_steps_with_a_step_text_and_a_missing_log` | the unknown-option refusal is removed (`if False:`), so `--bogus` is read as a step text | proven |
| step-cost.sh run through a symlink to the skill directory and from another working directory prints the same figure and exit code as when run in place | `test_cli_from_another_working_directory_prints_the_figure_and_exit_code_of_that_directorys_event_log` | `logical_cwd()` returns the module directory instead of the working directory | proven |

## Step 4 — time-budget.test.sh (3/3 proven, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| time-budget.sh: unset tunables resolve to 10 and 1.5; a non-numeric one exits 2 naming the variable | `test_cli_with_both_tunables_unset_prints_10_and_1_5_and_a_non_numeric_one_exits_2_naming_its_variable` | the VERI_UNIT_BUDGET default is 11 instead of 10 | proven |
| time-budget.sh: VERI_UNIT_BUDGET=ten exits 2, nothing on stdout, stderr exactly the one diagnostic line | `test_cli_with_a_non_numeric_budget_exits_2_with_nothing_on_stdout_and_exactly_the_one_diagnostic_line` | the VERI_UNIT_BUDGET diagnostic reads `must be seconds` instead of `must be a number of seconds` | proven |
| time-budget.sh run through a symlink to the skill directory and from another working directory answers as it does when run in place | `test_cli_answers_the_same_from_another_working_directory_with_the_tunables_unset_or_a_non_numeric_budget` | main exits 2 printing nothing when its working directory is named `elsewhere` | proven |

## Step 5 — timed-test-run.test.sh (4/4 proven, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| timed-test-run.sh <tier> <suites> <cmd>: runs the command, writes one test-run event carrying tier, suites and seconds, and exits with the command's own status | `test_cli_runs_the_command_and_writes_one_test_run_event_with_tier_suites_and_seconds_exiting_with_its_status` | the test-run event records `suites=x` instead of the suites given | proven |
| timed-test-run.sh records the command's own exit status on the test-run event, so a reader can say whether that run passed | `test_cli_records_the_commands_own_exit_status_on_the_test_run_event` | the test-run event records `status=0` whatever the command exited | proven |
| timed-test-run.sh refuses fewer than three arguments, an empty <tier> or an empty <cmd>: exit 2, the usage line alone on stderr, nothing on stdout, no event written | `test_cli_refuses_fewer_than_three_arguments_an_empty_tier_or_an_empty_cmd_with_exit_2_and_the_usage_line_alone` | the empty-`<cmd>` refusal is removed, so `all "" ""` runs and records an event | proven |
| timed-test-run.sh, run through a symlink to the skill directory and from another working directory, answers as in place: the command's own status, the same stdout and stderr, event.sh found, and its one test-run line in the caller's .tdd/events.jsonl | `test_cli_from_another_working_directory_answers_as_in_place_with_its_one_test_run_line_in_that_directory` | the event is written under the module directory instead of the caller's working directory | proven |
