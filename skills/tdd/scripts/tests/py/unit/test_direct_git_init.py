"""A ratchet: test files running `git init` directly only shrink in number.

New cases build their scratch repository with `repo_builder.new_repo`, which copies a per-worker template instead of
running `git init` each time (#3931). repo_builder.py is exempt: it is the one that runs it.

"Directly" is lexical (#4813): a list or tuple literal whose first element is "git" and whose first element after it that
is neither an option nor an option's value (`-C <dir>`, `-c <key=value>`) is "init", or a call to a callable whose name
contains `git` with "init" as its first or second positional argument. A site that assembles its argv (`git + ["init"]`)
is outside the rule.
"""
import ast

import pytest

# The test files (paths under tests/py, sorted, ONE per line) that still run git init directly. Migrate a file to
# repo_builder.new_repo and delete its line: a listed file that no longer runs it fails the second case below. Entries may
# be removed, NEVER added; a file not listed that runs it fails the first. One line per file keeps parallel migrations
# from conflicting. A file whose only sites are `--bare` stays: new_repo has no bare form yet.
FILES_RUNNING_GIT_INIT = (
    "test_add_ledger_step_process.py",
    "test_branch_gate_process.py",
    "test_case_history_process.py",
    "test_check_earlier_state_gate_process.py",
    "test_ci_flake_process.py",
    "test_content_mtimes_process.py",
    "test_diff_leaf_deviation_process.py",
    "test_drop_ledger_step_process.py",
    "test_event.py",
    "test_full_tier_time_process.py",
    "test_fused_comments_process.py",
    "test_gitignore_process.py",
    "test_grade_prose_process.py",
    "test_graded_changed_process.py",
    "test_graded_rebase_conflict_process.py",
    "test_install_links_process.py",
    "test_invisible_work_process.py",
    "test_issue_worktree_process.py",
    "test_leaf_tree_guard_process.py",
    "test_ledger_growth_process.py",
    "test_merge_lock_gate_push_process.py",
    "test_merge_lock_process.py",
    "test_metrics_process.py",
    "test_mutation_parity_process.py",
    "test_no_product_caller_process.py",
    "test_one_operator_role_process.py",
    "test_one_role_process.py",
    "test_parallel_conductors.py",
    "test_pin_fast_tier_process.py",
    "test_pr_finish_process.py",
    "test_pr_prepare_process.py",
    "test_pr_ready_process.py",
    "test_pr_ready_wait_process.py",
    "test_preflight_process.py",
    "test_preserve_attempt_process.py",
    "test_production_frozen_process.py",
    "test_prose_owed_waiver_process.py",
    "test_push_branch_process.py",
    "test_queued_merge_process.py",
    "test_ready_check_process.py",
    "test_rebase_graded_only_process.py",
    "test_rebase_onto_default_process.py",
    "test_report_process.py",
    "test_requirements_tracked_process.py",
    "test_restore_production_process.py",
    "test_resume_clean_process.py",
    "test_retired_filers_sweep_process.py",
    "test_run_conductor_process.py",
    "test_run_done_process.py",
    "test_run_finished_process.py",
    "test_skill_ci_conflict.py",
    "test_skill_ci_conflict_graded_process.py",
    "test_skill_edit_guard_process.py",
    "test_skill_leaf_env.py",
    "test_skill_preflight_process.py",
    "test_skill_refactor_touched.py",
    "test_solvable_issues_process.py",
    "test_stack_branch_process.py",
    "test_stack_carry_process.py",
    "test_stack_culprit_process.py",
    "test_stack_fix_process.py",
    "test_stack_green_process.py",
    "test_stack_land_process.py",
    "test_stack_pr_process.py",
    "test_stack_recover_process.py",
    "test_status_process.py",
    "test_status_refresh_scope_process.py",
    "test_status_report_landed_process.py",
    "test_status_report_landed_since_process.py",
    "test_status_report_refresh_process.py",
    "test_status_report_waiting_process.py",
    "test_step_close_process.py",
    "test_stop_reason_process.py",
    "test_suite_red_resume_process.py",
    "test_supervise_process.py",
    "test_tests_frozen_record_check_process.py",
    "test_tick_ledger_process.py",
    "test_timed_test_run_process.py",
    "test_verdict_chain.py",
    "test_veri_bail_patch_process.py",
    "test_watch_runs_process.py",
    "test_workqueue_process.py",
    "unit/test_report_cache.py",
)

EXEMPT = ("repo_builder.py",)
TAKES_A_VALUE = ("-C", "-c")


def _subcommand(elements):
    """The first element of a git argv (after "git") that is neither an option nor an option's value, or None."""
    rest = iter(elements)
    for element in rest:
        if not (isinstance(element, ast.Constant) and isinstance(element.value, str)):
            return None
        if element.value in TAKES_A_VALUE:
            next(rest, None)
        elif not element.value.startswith("-"):
            return element.value
    return None


def _callee(call):
    return call.func.id if isinstance(call.func, ast.Name) else call.func.attr if isinstance(call.func, ast.Attribute) else ""


def _runs_git_init(node):
    if isinstance(node, (ast.List, ast.Tuple)):
        first = node.elts[0] if node.elts else None
        return (isinstance(first, ast.Constant) and first.value == "git"
                and _subcommand(node.elts[1:]) == "init")
    return (isinstance(node, ast.Call) and "git" in _callee(node)
            and any(isinstance(a, ast.Constant) and a.value == "init" for a in node.args[:2]))


def _files_running_git_init(tests_py_index):
    return sorted(path for path, entry in (("/".join(e.path.parts[e.path.parts.index("py") + 1:]), e) for e in tests_py_index)
                  if path not in EXEMPT and any(_runs_git_init(node) for node in entry.nodes))


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_no_test_file_outside_the_list_runs_git_init_directly(tests_py_index):
    unlisted = [path for path in _files_running_git_init(tests_py_index) if path not in FILES_RUNNING_GIT_INIT]

    assert not unlisted, (
        f"{unlisted} run git init directly: build the repository with repo_builder.new_repo instead. "
        f"FILES_RUNNING_GIT_INIT only shrinks, never add to it")


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_a_listed_file_that_no_longer_runs_git_init_directly_is_removed_from_the_list(tests_py_index):
    found = _files_running_git_init(tests_py_index)
    gone = [path for path in FILES_RUNNING_GIT_INIT if path not in found]

    assert not gone, f"{gone} no longer run git init directly: remove them from FILES_RUNNING_GIT_INIT"


def test_the_list_is_sorted():
    paths = list(FILES_RUNNING_GIT_INIT)

    assert paths == sorted(paths)
