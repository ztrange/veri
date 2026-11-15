"""A ratchet: test files defining their own throwaway-repository builder do not grow in number; new cases use repo_builder."""
import pytest

# Test files that still define a module-level new_repo, make_repo, fixture_repo or commit_all. Lower this number when you
# migrate a file to repo_builder's new_repo/commit_all; never raise it. The files left build something repo_builder does
# not: a bare repository or a configured identity for plain `git commit` (test_skill_preflight, test_skill_drift), a
# remote and a branch with a ledger (test_push_branch_process), a copy of the Makefile (test_watch_process), an
# allow-empty commit through another git helper (test_affected_suites).
FILES_WITH_A_LOCAL_REPO_BUILDER = 5

LOCAL_BUILDERS = ("new_repo", "make_repo", "fixture_repo", "commit_all")


def _files_defining_a_local_repo_builder(tests_py_index):
    return [entry.path.name for entry in tests_py_index
            if any(definition.name in LOCAL_BUILDERS for definition in entry.walk.definitions)]


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_no_more_test_files_define_a_local_repo_builder_than_the_ratchet_allows(tests_py_index):
    found = _files_defining_a_local_repo_builder(tests_py_index)

    assert len(found) <= FILES_WITH_A_LOCAL_REPO_BUILDER, (
        f"{len(found)} test files define their own {', '.join(LOCAL_BUILDERS)}, the ratchet allows "
        f"{FILES_WITH_A_LOCAL_REPO_BUILDER}: build repositories with repo_builder's new_repo and commit_all instead: {found}")


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_the_ratchet_is_lowered_to_the_number_of_files_still_defining_a_local_repo_builder(tests_py_index):
    found = _files_defining_a_local_repo_builder(tests_py_index)

    assert len(found) >= FILES_WITH_A_LOCAL_REPO_BUILDER, (
        f"only {len(found)} test files still define a local repo builder, below the ratchet's "
        f"{FILES_WITH_A_LOCAL_REPO_BUILDER}: lower FILES_WITH_A_LOCAL_REPO_BUILDER to {len(found)}")
