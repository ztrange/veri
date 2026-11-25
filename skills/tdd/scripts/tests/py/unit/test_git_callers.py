"""A ratchet: the modules of veri/ that start git other than through veri/git.py only shrink in number.

"Starts git" is read with `ast`, by what a module does: a call whose first argument is a list or tuple literal whose
first element is the string "git" (`subprocess.run(["git", "status"])`), or a module-level function named `git` or
`_git`. veri/git.py is exempt: it is the shared way. New code calls `git.git`, `git.out`, `git.ok` or
`git.default_branch`.

Blind spots, by construction: a command list built elsewhere and passed in (`cmd = ["git", ...]; run(cmd)`), a name
bound to a list, a list spliced from another (`[*GIT, "status"]`), and a git started through a shell string.
"""
import ast

import pytest

# The modules of veri/ (by stem, sorted, ONE per line) that still start git themselves. Migrate a module to veri/git.py
# and delete its line: a listed module that no longer starts git fails the second case below. Entries may be removed,
# NEVER added; a module not listed that starts git fails the first. One line per module keeps parallel migrations from
# conflicting.
MODULES_RUNNING_GIT_DIRECTLY = {
    "add_ledger_step": "git rev-parse --short and a built git call, through subprocess",
    "ensure_run_state_ignored": "git -C <root> rev-parse, through subprocess",
    "frozen_record": "git rev-parse, write-tree and check-ignore, through subprocess",
    "github": "git ls-remote origin and push --dry-run, through bounded_group",
    "install_links": "git -C <root>, through subprocess",
    "issue_worktree": "git remote, worktree, show-ref and fetch, through subprocess; its own read of origin/HEAD (PRD 025.14)",
    "leaf_tree_guard": "its own git helper; git add -A and update-ref",
    "ledger_growth": "git -C <root>, through subprocess",
    "merge_lock": "git rev-parse --path-format=absolute, through subprocess",
    "mutation_parity": "git apply and apply -R, through subprocess",
    "mutation_probe": "git rev-parse, diff, ls-files and show, through subprocess",
    "parallel_conductors": "git rev-parse --git-common-dir, through subprocess",
    "park_issue": "git remote get-url, through subprocess",
    "push_branch": "git rev-parse, push and ls-remote, through subprocess",
    "queued_merge": "its own _git helper over git -C <root>",
    "refactor_touched": "git rev-parse, diff --name-only and ls-files, through subprocess",
    "report_cache": "git -C <root>, through subprocess",
    "requirements": "git ls-files -z, through subprocess",
    "run_conductor": "its own git helper; keeps its own read of the default branch (PRD 025.14)",
    "run_dir": "git worktree list, through subprocess",
    "skill_edit_guard": "git calls on built argument lists, through subprocess",
    "skill_edit_step": "git add, commit and rev-parse, through subprocess",
    "stale_rows": "git show, through subprocess",
    "status": "git -C <worktree>, through subprocess",
    "suite_red_resume": "git reset --hard and a built git call, through subprocess",
    "supervise": "git ls-files -m, through subprocess",
    "transform_touches_tests": "git log and rev-parse --verify, through subprocess",
    "update_veri": "its own git helper over git -C <clone>; its own read of origin/HEAD (PRD 025.14)",
    "workqueue": "git remote get-url, through subprocess",
}

EXEMPT = ("git",)


def _starts_git(tree):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in ("git", "_git"):
            return True
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], (ast.List, ast.Tuple)):
            first = node.args[0].elts[:1]
            if first and isinstance(first[0], ast.Constant) and first[0].value == "git":
                return True
    return False


def _modules_starting_git(veri_modules_index):
    return sorted(name for name in veri_modules_index.names
                  if name not in EXEMPT and _starts_git(veri_modules_index.tree(name)))


@pytest.mark.tree_audit("every module of veri/")
def test_no_module_outside_the_list_starts_git_itself(veri_modules_index):
    unlisted = [name for name in _modules_starting_git(veri_modules_index) if name not in MODULES_RUNNING_GIT_DIRECTLY]

    assert not unlisted, (
        f"{unlisted} start git themselves: run it through veri/git.py (git.git, git.out, git.ok) instead. "
        f"MODULES_RUNNING_GIT_DIRECTLY only shrinks, never add to it")


@pytest.mark.tree_audit("every module of veri/")
def test_a_listed_module_that_no_longer_starts_git_is_removed_from_the_list(veri_modules_index):
    found = _modules_starting_git(veri_modules_index)
    gone = [name for name in MODULES_RUNNING_GIT_DIRECTLY if name not in found]

    assert not gone, f"{gone} no longer start git themselves: remove them from MODULES_RUNNING_GIT_DIRECTLY"


def test_the_list_is_sorted():
    names = list(MODULES_RUNNING_GIT_DIRECTLY)

    assert names == sorted(names)
