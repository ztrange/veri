"""A ratchet: test files defining their own throwaway-repository builder only shrink in number; new cases use repo_builder."""
import pytest

# The test files (paths under tests/py, sorted, ONE per line) that still define a module-level new_repo, make_repo,
# fixture_repo or commit_all. Migrate a file to repo_builder's new_repo/commit_all and delete its line: a listed file that
# no longer defines one fails the second case below. Entries may be removed, NEVER added; a file not listed that defines
# one fails the first. One line per file keeps parallel migrations from conflicting. The files left build something
# repo_builder does not, said in each reason.
FILES_WITH_A_LOCAL_REPO_BUILDER = {
    "test_skill_preflight.py": "bare repository and configured identity for plain git commit",
}

LOCAL_BUILDERS = ("new_repo", "make_repo", "fixture_repo", "commit_all")


def _files_defining_a_local_repo_builder(tests_py_index):
    return sorted("/".join(entry.path.parts[entry.path.parts.index("py") + 1:]) for entry in tests_py_index
                  if any(definition.name in LOCAL_BUILDERS for definition in entry.walk.definitions))


def test_the_list_is_sorted():
    paths = list(FILES_WITH_A_LOCAL_REPO_BUILDER)

    assert paths == sorted(paths)


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_no_test_file_outside_the_list_defines_a_local_repo_builder(tests_py_index):
    unlisted = [path for path in _files_defining_a_local_repo_builder(tests_py_index)
                if path not in FILES_WITH_A_LOCAL_REPO_BUILDER]

    assert not unlisted, (
        f"{unlisted} define their own {', '.join(LOCAL_BUILDERS)}: build repositories with repo_builder's new_repo and "
        f"commit_all instead. FILES_WITH_A_LOCAL_REPO_BUILDER only shrinks, never add to it")


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_a_listed_file_that_no_longer_defines_a_local_repo_builder_is_removed_from_the_list(tests_py_index):
    found = _files_defining_a_local_repo_builder(tests_py_index)
    gone = [path for path in FILES_WITH_A_LOCAL_REPO_BUILDER if path not in found]

    assert not gone, f"{gone} no longer define a local repo builder: remove them from FILES_WITH_A_LOCAL_REPO_BUILDER"
