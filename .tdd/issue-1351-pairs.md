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
