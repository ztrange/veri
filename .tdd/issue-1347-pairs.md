# Mutation-parity pairs proven for #1347

Every row below is `proven` by the conductor's own `mutation-parity.sh` run (step 1: 8/8, step 2: 7/7, both exit 0), each mutation in `skills/tdd/scripts/veri/affected_suites.py` save the symlink row's, which is in `skills/tdd/scripts/affected-suites.sh`.

## Step 1 — veri/ and tests/py/ mapping, the symlinked run, the branch point (#1138)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| a touched veri/event_log.py prints tests/py/test_event_log.py and tests/event-log.test.sh, without widening | `test_a_touched_veri_module_prints_its_pytest_file_and_its_shims_bash_suite_without_widening` | a veri module maps to no pytest file (`return ([]` + its shim suite) | proven |
| a touched veri/probe_queue.py with no tests/py/test_probe_queue.py prints only tests/probe-queue.test.sh, without widening | `test_a_touched_veri_module_with_no_pytest_file_prints_only_its_shims_bash_suite_without_widening` | a veri module maps to `tests/py/test_<name>.py` whether or not it exists | proven |
| a touched tests/py/test_status.py prints that file, without widening | `test_a_touched_pytest_file_under_tests_py_prints_itself_without_widening` | a `tests/py/` pytest file is unplaced, so it widens | proven |
| affected-suites.sh run through a symlink to the skill directory from the repository root answers as it does when run in place | `test_the_shim_run_through_a_symlink_to_the_skill_directory_answers_as_it_does_in_place` | the shim finds its module through the repository layout above the skill (`$(dirname "$0")/../../..`), not beside itself | proven |
| #1138: a suite the base gained after the branch point is not printed by affected-suites.sh <base>..HEAD, only the branch's own | `test_1138_a_suite_the_base_gained_after_the_branch_point_is_not_printed_only_the_branchs_own` | `<base>..<head>` is not rewritten to `<base>...<head>`, so the merge base is not used | proven |
| #1138: a non-suite file the base changed or deleted after the branch point contributes no suite to affected-suites.sh <base>..HEAD | `test_1138_a_non_suite_file_the_base_changed_or_deleted_after_the_branch_point_contributes_no_suite` | `<base>..<head>` is not rewritten to `<base>...<head>`, so the merge base is not used | proven |
| #1138: a suite the base added or deleted after the branch point does not make affected-suites.sh <base>..HEAD print skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py | `test_1138_a_suite_the_base_added_or_deleted_after_the_branch_point_does_not_pull_in_the_claude_md_counts_suite` | `<base>..<head>` is not rewritten to `<base>...<head>`, so the merge base is not used | proven |
| #1138: a suite the branch itself deleted is not printed by affected-suites.sh <base>..HEAD | `test_1138_a_suite_the_branch_itself_deleted_is_not_printed` | a changed suite is printed even when it no longer exists (`return [f]`) | proven |

## Step 2 — <base> with uncommitted or untracked work

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| affected-suites.sh <base> with an uncommitted edit to a script prints its suite, exits 0, and leaves stash, worktrees and HEAD as they were | `test_working_tree_an_uncommitted_edit_to_a_script_prints_its_suite_and_leaves_stash_worktrees_and_head` | working-tree mode diffs `<base>..HEAD`, ignoring uncommitted edits | proven |
| affected-suites.sh <base> with an uncommitted edit inside one ## section of SKILL.md prints the suites reading that section or SKILL.md unsliced, not one reading only another | `test_working_tree_an_uncommitted_edit_inside_one_section_of_skill_md_prints_the_suites_reading_it_or_skill_md_unsliced` | SKILL.md section slicing disabled (`section = None`) | proven |
| affected-suites.sh <base> with a new, untracked suite prints that suite | `test_working_tree_a_new_untracked_suite_is_printed` | untracked files dropped from the working-tree file list | proven |
| affected-suites.sh <base> with a new, untracked suite also prints skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py | `test_working_tree_a_new_untracked_suite_also_prints_the_claude_md_counts_suite` | untracked added suites never pull in the counts suite (`if False:`) | proven |
| affected-suites.sh <base> with a committed added suite and no untracked file still prints skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py | `test_working_tree_a_committed_added_suite_with_no_untracked_file_still_prints_the_claude_md_counts_suite` | working-tree mode skips the committed `--diff-filter=AD` count | proven |
| affected-suites.sh <base> with no committed and no uncommitted change since <base> exits 3 and prints nothing | `test_working_tree_with_nothing_changed_since_base_exits_3_and_prints_nothing` | nothing changed since `<base>` returns 0 instead of 3 | proven |
| affected-suites.sh <base> with an unresolvable <base> exits 2 with a diagnostic on stderr and nothing on stdout | `test_main_returns_2_with_the_usage_line_for_no_argument_and_names_an_unresolvable_base` | the unresolvable-revision diagnostic names no revision | proven |
