"""A ratchet: test files defining their own module-level git helper only shrink in number.

New cases run git through `repo_builder.git` (`from repo_builder import git`), never a module-level `def git(` or
`def _git(` of their own. repo_builder.py is exempt: it is the shared one. A helper defined inside a test function (a
function-local `def git(`) is outside the rule.
"""
import pytest

# The test files (paths under tests/py, sorted, ONE per line) that still define a module-level git or _git function.
# Migrate a file to repo_builder.git and delete its line: a listed file that no longer defines one fails the second case
# below. Entries may be removed, NEVER added; a file not listed that defines one fails the first. One line per file keeps
# parallel migrations from conflicting.
FILES_WITH_A_LOCAL_GIT_HELPER = {
    "test_case_history_process.py": "git -C with check=True: a failure raises CalledProcessError, not repo_builder's AssertionError",
    "test_check_earlier_state_gate_process.py": "git by cwd=, check=True, returns nothing",
    "test_diff_leaf_deviation_process.py": "git -C with check=True, stdout unstripped",
    "test_ensure_run_state_ignored_process.py": "returns the CompletedProcess, unchecked, and passes kwargs through",
    "test_leaf_tree_guard_process.py": "git -C with check=True: a failure raises CalledProcessError",
    "test_ledger_growth_process.py": "git -C with check=True, stdout unstripped",
    "test_merge_lock_gate_push_process.py": "_git with protocol.file.allow=always and identity in the environment",
    "test_no_product_caller_process.py": "git -C with check=True: a failure raises CalledProcessError",
    "test_production_frozen_process.py": "git -C with check=True: a failure raises CalledProcessError",
    "test_ready_check_process.py": "_git by cwd=, check=True, returns nothing",
    "test_restore_production_process.py": "git with a replaced environment (PATH and GIT_ENV only), stdout unstripped",
    "test_resume_clean_process.py": "git -C with check=True, stdout unstripped",
    "test_skill_edit_guard_process.py": "git -C with check=True: a failure raises CalledProcessError",
    "test_skill_edit_step_process.py": "git -C with check=True: a failure raises CalledProcessError",
    "test_skill_preflight_process.py": "git -C with no identity, returns nothing",
    "test_skill_refactor_touched.py": "git -C with check=True, stdout unstripped",
    "test_stop_run_process.py": "git(*args, cwd=), output discarded",
    "test_suite_red_resume_process.py": "git -C with check=True, stdout unstripped",
    "test_tests_frozen_process.py": "git by cwd=, check=True, returns nothing",
    "test_tests_frozen_record_check_process.py": "_git by cwd=, check=True, returns nothing",
    "test_tick_ledger_process.py": "git by cwd=, check=True, returns nothing",
    "test_transform_touches_tests_process.py": "git -C returning the CompletedProcess after asserting exit 0",
    "test_veri_bail_patch_process.py": "git by cwd=, check=True, stdout as bytes",
    "unit/test_git.py": "a fixture named git that imports veri.git; it runs no git",
}

EXEMPT = ("repo_builder.py",)
HELPERS = ("git", "_git")


def _files_defining_a_local_git_helper(tests_py_index):
    return sorted(path for path, entry in (("/".join(e.path.parts[e.path.parts.index("py") + 1:]), e) for e in tests_py_index)
                  if path not in EXEMPT
                  and any(d.name in HELPERS and d.segment.startswith(("def ", "async def "))
                          for d in entry.walk.definitions))


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_no_test_file_outside_the_list_defines_a_module_level_git_helper(tests_py_index):
    unlisted = [path for path in _files_defining_a_local_git_helper(tests_py_index)
                if path not in FILES_WITH_A_LOCAL_GIT_HELPER]

    assert not unlisted, (
        f"{unlisted} define their own module-level git or _git: use repo_builder.git instead. "
        f"FILES_WITH_A_LOCAL_GIT_HELPER only shrinks, never add to it")
